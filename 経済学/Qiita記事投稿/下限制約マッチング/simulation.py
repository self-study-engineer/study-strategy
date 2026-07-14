"""
simulation.py — PLDA-RQ vs RSDA-RQ vs ACDA 比較実験

参考文献:
    Goto et al. (2016) "Strategyproof matching with regional minimum and maximum quotas"
    Artificial Intelligence 235, 40-57.  Section 6.

実験設定の概要:
    - 学生数 n, 学校数 m
    - 木構造: binary tree または octary tree（簡易版）
    - 選好生成: 共通ベクトル u_c と個人ベクトル u_s を alpha で混合
    - 指標:
        (1) claiming students 比率（wastefulness の代理）
        (2) 学生厚生: k番目以上に選んだ学校に割り当てられた学生の累積比率 (CDF)
"""

from __future__ import annotations
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from model import Market, RegionNode, RegionTree
from mechanisms import plda_rq, rsda_rq, acda
from feasibility import claiming_students, check_feasible_matching_exists


# ─────────────────────────────────────────────────────────────────────────────
# 木構造の生成
# ─────────────────────────────────────────────────────────────────────────────

def build_binary_tree(
    school_indices: list[int],
    individual_max: int,
    individual_min: int,
    regional_min_excess_ratio: float = 0.0,
    regional_max_shrink_ratio: float = 0.0,
    n_students: int = 0,
) -> RegionNode:
    """
    二分木を再帰的に構築する。

    Parameters
    ----------
    school_indices           : 学校インデックスのリスト（葉ノードの順）
    individual_max           : 個別最大定員 q_c
    individual_min           : 個別最低定員 p_c
    regional_min_excess_ratio: 地域最低定員を子の合計より超過させる比率 (a_r / total)
    regional_max_shrink_ratio: 地域最高定員を子の合計より縮小させる比率 (b_r / total)
    n_students               : 学生数（ルートの定員設定用）
    """
    if len(school_indices) == 1:
        c = school_indices[0]
        return RegionNode(
            name=f"{{c{c+1}}}",
            schools=frozenset([c]),
            min_quota=individual_min,
            max_quota=individual_max,
        )

    mid = len(school_indices) // 2
    left = build_binary_tree(
        school_indices[:mid], individual_max, individual_min,
        regional_min_excess_ratio, regional_max_shrink_ratio, n_students,
    )
    right = build_binary_tree(
        school_indices[mid:], individual_max, individual_min,
        regional_min_excess_ratio, regional_max_shrink_ratio, n_students,
    )

    children_min_sum = left.min_quota + right.min_quota
    children_max_sum = left.max_quota + right.max_quota

    # 地域最低定員 = 子の合計 + 超過分
    excess = int(children_min_sum * regional_min_excess_ratio)
    region_min = children_min_sum + excess

    # 地域最高定員 = 子の合計 - 縮小分
    shrink = int(children_max_sum * regional_max_shrink_ratio)
    region_max = max(children_max_sum - shrink, region_min)

    node = RegionNode(
        name=f"r{{{','.join(f'c{c+1}' for c in sorted(school_indices))}}}",
        schools=frozenset(school_indices),
        min_quota=region_min,
        max_quota=region_max,
        children=[left, right],
    )
    left.parent = node
    right.parent = node
    return node


def build_octary_tree(
    school_indices: list[int],
    individual_max: int,
    individual_min: int,
    regional_min_excess_ratio: float = 0.0,
    regional_max_shrink_ratio: float = 0.0,
) -> RegionNode:
    """
    8分木を再帰的に構築する（各内部ノードが8つの子を持つ）。
    """
    if len(school_indices) == 1:
        c = school_indices[0]
        return RegionNode(
            name=f"{{c{c+1}}}",
            schools=frozenset([c]),
            min_quota=individual_min,
            max_quota=individual_max,
        )

    chunk_size = max(1, len(school_indices) // 8)
    child_groups = []
    for i in range(0, len(school_indices), chunk_size):
        child_groups.append(school_indices[i:i + chunk_size])

    children = [
        build_octary_tree(
            group, individual_max, individual_min,
            regional_min_excess_ratio, regional_max_shrink_ratio,
        )
        for group in child_groups
    ]

    children_min_sum = sum(c.min_quota for c in children)
    children_max_sum = sum(c.max_quota for c in children)

    excess = int(children_min_sum * regional_min_excess_ratio)
    region_min = children_min_sum + excess

    shrink = int(children_max_sum * regional_max_shrink_ratio)
    region_max = max(children_max_sum - shrink, region_min)

    node = RegionNode(
        name=f"region({len(school_indices)})",
        schools=frozenset(school_indices),
        min_quota=region_min,
        max_quota=region_max,
        children=children,
    )
    for child in children:
        child.parent = node
    return node


# ─────────────────────────────────────────────────────────────────────────────
# 市場の生成
# ─────────────────────────────────────────────────────────────────────────────

def generate_market(
    n_students: int,
    n_schools: int,
    individual_max: int,
    individual_min: int,
    alpha: float,
    tree_type: str = "binary",
    regional_min_excess_ratio: float = 0.2,
    regional_max_shrink_ratio: float = 0.3,
    rng: random.Random | None = None,
) -> Market:
    """
    ランダムな市場を生成する（Section 6 の設定に準拠）。

    選好生成:
        共通ユーティリティ u_c ∈ [0,1]^m と個人ユーティリティ u_s ∈ [0,1]^m を
        alpha * u_c + (1 - alpha) * u_s で合成して順序に変換。

    Parameters
    ----------
    n_students               : 学生数
    n_schools                : 学校数
    individual_max           : 個別最大定員
    individual_min           : 個別最低定員
    alpha                    : 共通ユーティリティの重み (0: 独立, 1: 完全相関)
    tree_type                : "binary" または "octary"
    regional_min_excess_ratio: a_r の比率
    regional_max_shrink_ratio: b_r の比率
    rng                      : 乱数生成器（省略時は random モジュール）
    """
    if rng is None:
        rng = random.Random()

    # ── 選好の生成 ─────────────────────────────────────────────────────
    u_common = [rng.random() for _ in range(n_schools)]

    student_prefs = []
    for _ in range(n_students):
        u_private = [rng.random() for _ in range(n_schools)]
        u_combined = [
            alpha * u_common[c] + (1 - alpha) * u_private[c]
            for c in range(n_schools)
        ]
        # ユーティリティが高い順に並べ替えた学校インデックス
        pref = sorted(range(n_schools), key=lambda c: -u_combined[c])
        student_prefs.append(pref)

    # ── 優先度の生成 ─────────────────────────────────────────────────
    school_priors = []
    for _ in range(n_schools):
        perm = list(range(n_students))
        rng.shuffle(perm)
        school_priors.append(perm)

    # ── 木構造の生成 ──────────────────────────────────────────────────
    school_indices = list(range(n_schools))
    if tree_type == "binary":
        root = build_binary_tree(
            school_indices, individual_max, individual_min,
            regional_min_excess_ratio, regional_max_shrink_ratio, n_students,
        )
    elif tree_type == "octary":
        root = build_octary_tree(
            school_indices, individual_max, individual_min,
            regional_min_excess_ratio, regional_max_shrink_ratio,
        )
    else:
        raise ValueError(f"Unknown tree_type: {tree_type}")

    # ルートの定員を n_students に固定
    root.min_quota = n_students
    root.max_quota = n_students

    tree = RegionTree(root=root)

    return Market(
        student_names=[f"s{i+1}" for i in range(n_students)],
        school_names=[f"c{c+1}" for c in range(n_schools)],
        student_prefs=student_prefs,
        school_priors=school_priors,
        region_tree=tree,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 指標の計算
# ─────────────────────────────────────────────────────────────────────────────

def ratio_claiming(
    result: frozenset[tuple[int, int]],
    market: Market,
) -> float:
    """claiming students の比率を返す。"""
    claiming = claiming_students(result, market)
    return len(claiming) / market.n_students


def student_welfare_ranks(
    result: frozenset[tuple[int, int]],
    market: Market,
) -> list[int]:
    """各学生の割当学校の選好順位（1-indexed）を返す。"""
    assignment = {s: c for (s, c) in result}
    ranks = []
    for s in range(market.n_students):
        c = assignment.get(s, -1)
        if c == -1:
            ranks.append(market.n_schools + 1)
        else:
            ranks.append(market.student_rank(s, c) + 1)
    return ranks


def welfare_cdf(
    result: frozenset[tuple[int, int]],
    market: Market,
    max_rank: int | None = None,
) -> list[float]:
    """
    k 番目以上に選んだ学校に割り当てられた学生の比率の累積分布 (CDF) を返す。

    Returns
    -------
    list[float]: cdf[k-1] = (k 番目以上に割り当てられた学生) / n_students
    """
    if max_rank is None:
        max_rank = market.n_schools
    ranks = student_welfare_ranks(result, market)
    n = market.n_students
    return [sum(1 for r in ranks if r <= k) / n for k in range(1, max_rank + 1)]


# ─────────────────────────────────────────────────────────────────────────────
# メイン実験
# ─────────────────────────────────────────────────────────────────────────────

def run_simulation(
    n_students: int = 64,
    n_schools: int = 8,
    individual_max: int = 16,
    individual_min: int = 0,
    n_instances: int = 20,
    alpha_values: list[float] | None = None,
    tree_type: str = "binary",
    seed: int = 42,
) -> dict:
    """
    複数の alpha 値について PLDA-RQ, RSDA-RQ, ACDA を比較する。

    Returns
    -------
    dict: {alpha: {"plda": ..., "rsda": ..., "acda": ...}}
    """
    if alpha_values is None:
        alpha_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    results = {}
    rng = random.Random(seed)

    print(f"\n{'='*60}")
    print(f"  比較実験: {tree_type} tree, n={n_students}, m={n_schools}")
    print(f"  instances={n_instances}, individual_max={individual_max}, "
          f"individual_min={individual_min}")
    print(f"{'='*60}\n")

    for alpha in alpha_values:
        plda_claims, rsda_claims, acda_claims = [], [], []
        plda_ranks, rsda_ranks, acda_ranks = [], [], []
        skip_count = 0

        for _ in range(n_instances):
            market = generate_market(
                n_students=n_students,
                n_schools=n_schools,
                individual_max=individual_max,
                individual_min=individual_min,
                alpha=alpha,
                tree_type=tree_type,
                rng=rng,
            )

            if not check_feasible_matching_exists(market.region_tree):
                skip_count += 1
                continue

            try:
                r_plda = plda_rq(market, verbose=False)
                r_rsda = rsda_rq(market, verbose=False)
                r_acda = acda(market, verbose=False)

                plda_claims.append(ratio_claiming(r_plda, market))
                rsda_claims.append(ratio_claiming(r_rsda, market))
                acda_claims.append(ratio_claiming(r_acda, market))

                plda_ranks.extend(student_welfare_ranks(r_plda, market))
                rsda_ranks.extend(student_welfare_ranks(r_rsda, market))
                acda_ranks.extend(student_welfare_ranks(r_acda, market))

            except Exception as e:
                skip_count += 1
                continue

        n_valid = n_instances - skip_count

        def avg(lst):
            return sum(lst) / len(lst) if lst else float("nan")

        def avg_rank(ranks):
            return sum(ranks) / len(ranks) if ranks else float("nan")

        results[alpha] = {
            "n_valid": n_valid,
            "plda_claim_avg": avg(plda_claims),
            "rsda_claim_avg": avg(rsda_claims),
            "acda_claim_avg": avg(acda_claims),
            "plda_rank_avg": avg_rank(plda_ranks),
            "rsda_rank_avg": avg_rank(rsda_ranks),
            "acda_rank_avg": avg_rank(acda_ranks),
        }

        print(f"  alpha={alpha:.1f} | 有効={n_valid}/{n_instances} | "
              f"Claiming率: PLDA={avg(plda_claims):.3f}, "
              f"RSDA={avg(rsda_claims):.3f}, "
              f"ACDA={avg(acda_claims):.3f} | "
              f"平均順位: PLDA={avg_rank(plda_ranks):.2f}, "
              f"RSDA={avg_rank(rsda_ranks):.2f}, "
              f"ACDA={avg_rank(acda_ranks):.2f}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# エントリポイント
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("【実験 1: binary tree, pc=0 (論文 Fig. 2 相当)】")
    run_simulation(
        n_students=64,
        n_schools=8,
        individual_max=16,
        individual_min=0,
        n_instances=30,
        tree_type="binary",
        alpha_values=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    )

    print("\n\n【実験 2: octary tree, pc=0 (論文 Fig. 3 相当)】")
    run_simulation(
        n_students=64,
        n_schools=8,
        individual_max=16,
        individual_min=0,
        n_instances=30,
        tree_type="octary",
        alpha_values=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    )

    print("\n\n【実験 3: binary tree, pc=2 (論文 Fig. 8 相当)】")
    run_simulation(
        n_students=64,
        n_schools=8,
        individual_max=16,
        individual_min=2,
        n_instances=30,
        tree_type="binary",
        alpha_values=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    )
