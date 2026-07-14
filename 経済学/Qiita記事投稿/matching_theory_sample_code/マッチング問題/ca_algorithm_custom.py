"""
Cutoff Adjustment Algorithm — Custom (ca_algorithm_custom.py)

ca_algorithm.py の拡張版。以下の2点を追加対応する:

  1. 課レベルのクロスプロダクト回避制約
       禁止ペアのメンバーが同一課内の「異なる製品」に配属されても違反とみなす。
       既存の collision_avoidance_constraint は単一受入者内しかチェックしないため対応不可。

  2. 稼働量カバレッジ制約（下限制約）の後処理チェック
       必要稼働量 <= Σ可能稼働量 は遺伝的単調性を満たさない下限制約のため、
       CA ループには組み込まず、マッチング確定後に検証してレポートする。

【アルゴリズム設計の要点】

  標準 CA の課題:
    カットオフを +1 ずつ上げる標準 CA では、クロスプロダクト衝突を解消できない。
    理由: 禁止ペアのどちらかが当該製品の最上位優先者だった場合、
          カットオフを最大値まで上げても需要から除外できない。

  解決策 — "blocked セット" の導入:
    稼働量上限違反: 標準 CA 通り、カットオフを +1 上げる（遺伝的上限制約）
    課レベル衝突  : 禁止ペアの低優先側を当該製品の "blocked" セットに追加する
                    → blocked な応募者は次の希望製品を試みる（DA の仮拒否に相当）

  収束の保証:
    カットオフと blocked セットは単調増加のみで、状態空間は有限なため必ず収束する。

対応するマッチング問題:
  - 4課・複数製品（各課1〜3製品）・応募者多数・禁止ペアあり
  - 応募者は希望製品と各製品への可能稼働量を提出
  - 各製品には必要稼働量（下限）と最大受入稼働量（上限）が存在
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field


# ─────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────

@dataclass
class WorkloadInput:
    """
    稼働量制約・課レベル回避制約付きマッチング問題の入力データ。

    Args:
        proposer_prefs:     応募者 i の選好リスト（1-indexed 製品番号）
        product_prefs:      製品 j の優先順位リスト（1-indexed 応募者番号）
        workload_available: w[(応募者idx, 製品idx)] = 応募者の可能稼働量（0-indexed）
        workload_required:  製品 j の必要稼働量（下限; 後処理で検証）
        workload_max:       製品 j の最大受入稼働量（上限; アルゴリズムループで使用）
        department_of:      製品 j が属する課のインデックス（0-indexed）
        conflict_pairs:     同一課に配属してはならない応募者ペア（0-indexed）
        department_names:   課名リスト
        product_names:      製品名リスト
        proposer_names:     応募者名リスト
    """
    proposer_prefs:     list[list[int]]
    product_prefs:      list[list[int]]
    workload_available: dict[tuple[int, int], int]
    workload_required:  list[int]
    workload_max:       list[int]
    department_of:      list[int]
    conflict_pairs:     list[tuple[int, int]]
    department_names:   list[str]
    product_names:      list[str]
    proposer_names:     list[str]

    @property
    def n_proposers(self) -> int:
        return len(self.proposer_prefs)

    @property
    def n_products(self) -> int:
        return len(self.product_prefs)

    @property
    def n_departments(self) -> int:
        return len(self.department_names)

    def p_name(self, i: int) -> str:
        return self.proposer_names[i]

    def r_name(self, j: int) -> str:
        return self.product_names[j]

    def d_name(self, k: int) -> str:
        return self.department_names[k]

    def products_of(self, dept: int) -> list[int]:
        """課 dept に属する製品の 0-indexed リスト"""
        return [j for j, d in enumerate(self.department_of) if d == dept]


@dataclass
class WorkloadResult:
    proposer_match:   list[int]        # proposer_match[i] = 製品の 0-index（-1 = 未配分）
    product_match:    list[list[int]]  # product_match[j] = 応募者の 0-indexed リスト
    cutoff_profile:   list[int]        # 最終カットオフプロファイル
    blocked_final:    dict[int, set[int]]  # blocked[j] = 最終的にブロックされた応募者集合
    workload_total:   list[int]        # workload_total[j] = 製品 j の確定稼働量合計
    coverage_ok:      list[bool]       # coverage_ok[j] = 必要稼働量を満たすか


# ─────────────────────────────────────────────
# メインアルゴリズム
# ─────────────────────────────────────────────

def cutoff_adjustment_workload(data: WorkloadInput, verbose: bool = True) -> WorkloadResult:
    """
    稼働量制約・課レベル回避制約付き CA アルゴリズム。

    ループ内で以下の2制約を処理する:
      ① 稼働量上限制約: 製品 j の割当稼働量合計 > workload_max[j] → cutoff[j] += 1
      ② 課レベル回避制約: 禁止ペアが同一課内に共存 → 低優先側を blocked セットに追加

    稼働量カバレッジ（下限制約）は後処理で検証する。
    """
    P = data.n_proposers
    R = data.n_products

    # 製品ごとの優先順位表（priority_rank[j][p] = 製品jにとっての応募者pの順位、0=最優先）
    priority_rank = _build_priority_rank(data.product_prefs, P)

    # 初期化
    cutoff  = [1] * R
    blocked: dict[int, set[int]] = {j: set() for j in range(R)}

    if verbose:
        _print_input(data)
        print("=== CA アルゴリズム（稼働量制約・課レベル回避制約版）開始 ===\n")
        print(f"  初期カットオフ: {cutoff}\n")

    iteration = 1
    while True:
        # 需要計算（blocked セットを考慮）
        demand = _compute_demand_with_blocks(data, cutoff, priority_rank, blocked, P, R)
        dept_demand = _aggregate_by_dept(demand, data)

        new_cutoff  = list(cutoff)
        new_blocked = deepcopy(blocked)
        changed     = False

        if verbose:
            print(f"--- 反復 {iteration} ---")

        # ① 稼働量上限制約チェック → 標準カットオフ調整
        for j in range(R):
            total_wl = sum(data.workload_available.get((p, j), 0) for p in demand[j])
            if total_wl > data.workload_max[j]:
                new_cutoff[j] += 1
                changed = True
                if verbose:
                    demand_str = ", ".join(data.p_name(p) for p in sorted(demand[j]))
                    print(f"  {data.r_name(j)}[{data.d_name(data.department_of[j])}]: "
                          f"cutoff={cutoff[j]}, D=[{demand_str}]  "
                          f"稼働量={total_wl}/{data.workload_max[j]} ❌(稼働量上限超過)")
            else:
                if verbose:
                    demand_str = ", ".join(data.p_name(p) for p in sorted(demand[j]))
                    print(f"  {data.r_name(j)}[{data.d_name(data.department_of[j])}]: "
                          f"cutoff={cutoff[j]}, D=[{demand_str}]  "
                          f"稼働量={total_wl}/{data.workload_max[j]} ✅")

        # ② 課レベル回避制約チェック → blocked セットに追加
        if verbose:
            print()
        for dept_k in range(data.n_departments):
            prods_in_dept = data.products_of(dept_k)
            dept_dem      = dept_demand[dept_k]

            for (a, b) in data.conflict_pairs:
                if a not in dept_dem or b not in dept_dem:
                    continue

                # a と b がどの製品に配属されているか特定
                prod_a = next((j for j in prods_in_dept if a in demand[j]), None)
                prod_b = next((j for j in prods_in_dept if b in demand[j]), None)

                if prod_a is None or prod_b is None:
                    continue  # 未配分ケース（スキップ）

                # 低優先側（rank が大きい方）を blocked に追加
                rank_a = priority_rank[prod_a][a]
                rank_b = priority_rank[prod_b][b]

                if rank_a >= rank_b:
                    target_p, target_j = a, prod_a
                else:
                    target_p, target_j = b, prod_b

                if target_p not in new_blocked[target_j]:
                    new_blocked[target_j].add(target_p)
                    changed = True
                    if verbose:
                        print(f"  【禁止ペア衝突】({data.p_name(a)}, {data.p_name(b)}) "
                              f"→ {data.d_name(dept_k)} 内で共存")
                        print(f"    {data.p_name(target_p)} を "
                              f"{data.r_name(target_j)} からブロック "
                              f"（優先順位: rank={priority_rank[target_j][target_p]}）")

        if verbose:
            if changed:
                print(f"\n  → cutoff: {cutoff} → {new_cutoff}")
                for j in range(R):
                    added = new_blocked[j] - blocked[j]
                    if added:
                        names = ", ".join(data.p_name(p) for p in sorted(added))
                        print(f"     blocked[{data.r_name(j)}] += [{names}]")
            print()

        if not changed:
            if verbose:
                print(f"  収束: cutoff={cutoff}\n")
            break

        cutoff  = new_cutoff
        blocked = new_blocked
        iteration += 1

        # 安全装置
        if all(c > P for c in cutoff):
            break

    # 最終マッチング確定
    demand = _compute_demand_with_blocks(data, cutoff, priority_rank, blocked, P, R)
    proposer_match: list[int]       = [-1] * P
    product_match:  list[list[int]] = [[] for _ in range(R)]

    for j in range(R):
        product_match[j] = sorted(demand[j])
        for p in demand[j]:
            proposer_match[p] = j

    workload_total = [
        sum(data.workload_available.get((p, j), 0) for p in product_match[j])
        for j in range(R)
    ]
    coverage_ok = [
        workload_total[j] >= data.workload_required[j]
        for j in range(R)
    ]

    result = WorkloadResult(
        proposer_match=proposer_match,
        product_match=product_match,
        cutoff_profile=cutoff,
        blocked_final=blocked,
        workload_total=workload_total,
        coverage_ok=coverage_ok,
    )

    if verbose:
        print("=== CA アルゴリズム（稼働量制約・課レベル回避制約版）終了 ===\n")
        _print_result(result, data)
    return result


# ─────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────

def _compute_demand_with_blocks(
    data:          WorkloadInput,
    cutoff:        list[int],
    priority_rank: list[list[int]],
    blocked:       dict[int, set[int]],
    P:             int,
    R:             int,
) -> list[list[int]]:
    """
    カットオフと blocked セットを考慮して各製品の需要を計算する。

    各応募者は「足切り通過かつブロックされていない」製品のうち、
    自分の選好で最も上位のものに割り当てられる。
    """
    qualified: list[set[int]] = [set() for _ in range(R)]
    for j in range(R):
        threshold = P - cutoff[j]
        for p in range(P):
            if priority_rank[j][p] <= threshold and p not in blocked[j]:
                qualified[j].add(p)

    demand: list[list[int]] = [[] for _ in range(R)]
    for p in range(P):
        for r_1indexed in data.proposer_prefs[p]:
            j = r_1indexed - 1
            if p in qualified[j]:
                demand[j].append(p)
                break
    return demand


def _aggregate_by_dept(
    demand: list[list[int]],
    data:   WorkloadInput,
) -> list[set[int]]:
    """各課の統合需要（課内全製品の需要の和集合）を返す。"""
    dept_demand: list[set[int]] = [set() for _ in range(data.n_departments)]
    for j, applicants in enumerate(demand):
        dept = data.department_of[j]
        dept_demand[dept].update(applicants)
    return dept_demand


def _build_priority_rank(
    product_prefs: list[list[int]],
    n_proposers:   int,
) -> list[list[int]]:
    """優先順位リスト（1-indexed）を順位表（0-indexed）に変換する。

    rank[j][p] = 製品 j にとっての応募者 p の順位（0=最優先、n_proposers=未申請）
    """
    rank = [[n_proposers] * n_proposers for _ in range(len(product_prefs))]
    for j, row in enumerate(product_prefs):
        for rank_pos, proposer_1indexed in enumerate(row):
            rank[j][proposer_1indexed - 1] = rank_pos
    return rank


def _print_input(data: WorkloadInput) -> None:
    print("【組織構造と稼働量設定】")
    for k in range(data.n_departments):
        prods = data.products_of(k)
        print(f"  {data.d_name(k)}")
        for j in prods:
            print(f"    {data.r_name(j)}: "
                  f"必要稼働量={data.workload_required[j]}, "
                  f"最大稼働量={data.workload_max[j]}")
    print()

    print("【禁止ペア（同一課への配属禁止）】")
    for a, b in data.conflict_pairs:
        print(f"  ({data.p_name(a)}, {data.p_name(b)})")
    print()

    print("【応募者の選好・可能稼働量】")
    for p in range(data.n_proposers):
        prefs_str = " > ".join(data.r_name(j - 1) for j in data.proposer_prefs[p])
        wl_parts = [
            f"{data.r_name(j)}:{data.workload_available.get((p, j), 0)}"
            for j in range(data.n_products)
            if data.workload_available.get((p, j), 0) > 0
        ]
        wl_str = ", ".join(wl_parts)
        print(f"  {data.p_name(p)}: [{prefs_str}]  稼働量={{{wl_str}}}")
    print()


def _print_result(result: WorkloadResult, data: WorkloadInput) -> None:
    print("【マッチング結果（課別）】")
    for k in range(data.n_departments):
        print(f"  {data.d_name(k)}")
        for j in data.products_of(k):
            matched = result.product_match[j]
            names = ", ".join(data.p_name(p) for p in matched) or "（なし）"
            wl    = result.workload_total[j]
            req   = data.workload_required[j]
            cov   = "✅" if result.coverage_ok[j] else "❌"
            print(f"    {data.r_name(j)}: [{names}]  稼働量={wl}/{req} {cov}")
    print()

    print("【応募者の配属結果】")
    for p, j in enumerate(result.proposer_match):
        if j != -1:
            dest = f"{data.r_name(j)}（{data.d_name(data.department_of[j])}）"
            pref_rank = next(
                (i for i, r in enumerate(data.proposer_prefs[p]) if r - 1 == j), -1
            )
            rank_str = f"第{pref_rank+1}希望" if pref_rank >= 0 else "?"
        else:
            dest, rank_str = "未配分", "-"
        print(f"  {data.p_name(p)}: {dest}  [{rank_str}]")
    print()

    print(f"【最終カットオフ】 {result.cutoff_profile}")
    print()

    print("【稼働量カバレッジチェック（下限制約の後処理検証）】")
    for j in range(data.n_products):
        wl    = result.workload_total[j]
        req   = data.workload_required[j]
        mark  = "✅" if result.coverage_ok[j] else "❌"
        dept  = data.d_name(data.department_of[j])
        print(f"  {data.r_name(j)}[{dept}]: 稼働量合計={wl} / 必要={req} {mark}")
    all_ok = all(result.coverage_ok)
    print(f"  → 全製品カバレッジ: {'✅ 充足' if all_ok else '❌ 一部不足'}")
    print()

    print("【禁止ペア分離チェック（課レベル）】")
    all_sep = True
    for a, b in data.conflict_pairs:
        ja = result.proposer_match[a]
        jb = result.proposer_match[b]
        da = data.department_of[ja] if ja != -1 else -1
        db = data.department_of[jb] if jb != -1 else -1
        same   = (da == db and da != -1)
        status = "❌ 同一課（制約違反）" if same else "✅ 別課（または未配分）"
        pa = (f"{data.r_name(ja)}（{data.d_name(da)}）"
              if ja != -1 else "未配分")
        pb = (f"{data.r_name(jb)}（{data.d_name(db)}）"
              if jb != -1 else "未配分")
        print(f"  ({data.p_name(a)}, {data.p_name(b)}): {pa} / {pb} → {status}")
        if same:
            all_sep = False
    print(f"  → 全禁止ペア分離: {'✅' if all_sep else '❌'}")
    print()
