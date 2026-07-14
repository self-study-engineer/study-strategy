"""
feasibility.py — 下限制約マッチング: 実行可能性チェック

参考文献:
    Goto et al. (2016) "Strategyproof matching with regional minimum and maximum quotas"
    Artificial Intelligence 235, 40-57.

実装する理論:
    - Definition 10: Expected minimum count e_r(X')
    - Theorem 3: 階層木の場合の実行可能マッチング存在判定 (線形時間)
    - Theorem 4: X' が semi-school-feasible ⟺ e_r(X') ≤ q_r for all r
"""

from __future__ import annotations
from model import RegionNode, RegionTree, Market


# ─────────────────────────────────────────────────────────────────────────────
# Expected Minimum Count (Definition 10)
# ─────────────────────────────────────────────────────────────────────────────

def expected_min_count(X: frozenset[tuple[int, int]], node: RegionNode) -> int:
    """
    マッチング X' におけるノード r の期待最小カウント e_r(X') を計算する。

    Definition 10:
        e_r(X') = |X'_r|                                         if |r| = 1 (葉)
                = Σ_{r'∈children(r)} max(e_{r'}(X'), p_{r'})    otherwise

    Parameters
    ----------
    X    : コントラクト集合 {(s, c), ...}
    node : 計算対象のノード r

    Returns
    -------
    int : e_r(X')
    """
    if node.is_leaf():
        # 葉ノード: 該当学校に割り当てられたコントラクト数
        school_idx = next(iter(node.schools))
        return sum(1 for (_, c) in X if c == school_idx)
    else:
        # 内部ノード: 子の expected_min_count と子の最低定員の大きい方を合計
        return sum(
            max(expected_min_count(X, child), child.min_quota)
            for child in node.children
        )


def expected_min_count_all(
    X: frozenset[tuple[int, int]],
    tree: RegionTree,
) -> dict[RegionNode, int]:
    """
    全ノードの e_r(X') を一括計算して辞書で返す（ボトムアップ・再帰）。
    頻繁に呼び出す場合はこちらを使うと効率的。
    """
    result: dict[RegionNode, int] = {}

    def _compute(node: RegionNode) -> int:
        if node.is_leaf():
            school_idx = next(iter(node.schools))
            val = sum(1 for (_, c) in X if c == school_idx)
        else:
            val = sum(
                max(_compute(child), child.min_quota)
                for child in node.children
            )
        result[node] = val
        return val

    _compute(tree.root)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Semi-school-feasibility (Theorem 4)
# ─────────────────────────────────────────────────────────────────────────────

def is_semi_school_feasible(
    X: frozenset[tuple[int, int]],
    tree: RegionTree,
) -> bool:
    """
    X が semi-school-feasible かどうか判定する。

    Theorem 4:
        X' is semi-school-feasible  ⟺  e_r(X') ≤ q_r for all r ∈ R

    Returns
    -------
    bool
    """
    e_vals = expected_min_count_all(X, tree)
    return all(e <= node.max_quota for node, e in e_vals.items())


def is_school_feasible(
    X: frozenset[tuple[int, int]],
    tree: RegionTree,
) -> bool:
    """
    X が school-feasible かどうか判定する。

    school-feasible: ∀r, p_r ≤ |X'_r| ≤ q_r
    """
    for node in tree.all_nodes():
        count = sum(1 for (_, c) in X if c in node.schools)
        if not (node.min_quota <= count <= node.max_quota):
            return False
    return True


def is_feasible(
    X: frozenset[tuple[int, int]],
    market: Market,
) -> bool:
    """
    X が feasible かどうか判定する（student-feasible かつ school-feasible）。

    - student-feasible: 各学生に割り当てが1つ
    - school-feasible: 各地域の定員を満たす
    """
    # student-feasible
    students_in_X = [s for (s, _) in X]
    if len(students_in_X) != len(set(students_in_X)):
        return False  # 重複あり
    if len(students_in_X) != market.n_students:
        return False  # 未割当の学生あり

    return is_school_feasible(X, market.region_tree)


# ─────────────────────────────────────────────────────────────────────────────
# 実行可能マッチング存在判定 (Theorem 3)
# ─────────────────────────────────────────────────────────────────────────────

def check_feasible_matching_exists(tree: RegionTree) -> bool:
    """
    地域の最小・最大定員を満たす実行可能マッチングが存在するか判定する。

    Theorem 3 の証明に基づくアルゴリズム (線形時間):
      1. 各ノード r の p_r を深さ優先で更新:
         p_r ← max(p_r, Σ_{r'∈children(r)} p_{r'})
      2. 各ノード r の q_r を深さ優先で更新:
         q_r ← min(q_r, Σ_{r'∈children(r)} q_{r'})
      3. 全 r で p_r ≤ q_r なら実行可能マッチング存在。

    注意: この関数はノードの値を変更しない（コピーで計算）。

    Returns
    -------
    bool : 実行可能マッチングが存在するなら True
    """
    # ボトムアップに p, q を修正した値を計算
    revised_p: dict[RegionNode, int] = {}
    revised_q: dict[RegionNode, int] = {}

    def _revise(node: RegionNode) -> None:
        if node.is_leaf():
            revised_p[node] = node.min_quota
            revised_q[node] = node.max_quota
        else:
            for child in node.children:
                _revise(child)
            sum_p = sum(revised_p[child] for child in node.children)
            sum_q = sum(revised_q[child] for child in node.children)
            revised_p[node] = max(node.min_quota, sum_p)
            revised_q[node] = min(node.max_quota, sum_q)

    _revise(tree.root)

    return all(revised_p[node] <= revised_q[node] for node in tree.all_nodes())


# ─────────────────────────────────────────────────────────────────────────────
# claiming student の判定
# ─────────────────────────────────────────────────────────────────────────────

def claiming_students(
    X: frozenset[tuple[int, int]],
    market: Market,
) -> list[int]:
    """
    マッチング X において empty seat を主張できる学生のリストを返す。

    Definition 2 (nonwastefulness):
        学生 s が学校 c' の empty seat を主張できる
        ⟺ c' ≻_s c (s の現在の割当 c より c' を好む)
        かつ (X \ {(s,c)}) ∪ {(s,c')} が feasible

    Returns
    -------
    list[int] : claiming students の学生インデックスリスト
    """
    claiming = []
    for s, c in X:
        # s が c より好む学校 c' をすべてチェック
        pref = market.student_prefs[s]
        current_rank = market.student_rank(s, c)
        for c_prime in pref:
            if market.student_rank(s, c_prime) >= current_rank:
                break  # c 以降は全部悪い（c 自身も含む）
            # c' ≻_s c — c' に移動できるか
            X_new = (X - {(s, c)}) | {(s, c_prime)}
            if is_feasible(X_new, market):
                claiming.append(s)
                break

    return claiming
