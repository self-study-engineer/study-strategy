"""
example.py — 論文 Example 3, 4 の再現

参考文献:
    Goto et al. (2016) "Strategyproof matching with regional minimum and maximum quotas"
    Artificial Intelligence 235, 40-57.

Example 3 (Section 5.2): PLDA-RQ の動作確認
Example 4 (Section 5.3): RSDA-RQ の動作確認

木構造 (Fig. 1):
    C = {c1, c2, c3, c4},  p_C = q_C = 8
    ├── r1 = {c1, c2},  p=3, q=5
    │   ├── {c1},  p=1, q=3
    │   └── {c2},  p=1, q=3
    └── r2 = {c3, c4},  p=3, q=5
        ├── {c3},  p=1, q=3
        └── {c4},  p=1, q=3

学生: s1, ..., s8
選好:
    s1, s2, s3: c4 > c3 > c2 > c1
    s4, s5, s6: c4 > c1 > c2 > c3
    s7, s8:     c1 > c2 > c3 > c4
優先度:
    c1, c3: s1 > s2 > s3 > s4 > s5 > s6 > s7 > s8
    c2, c4: s8 > s7 > s6 > s5 > s4 > s3 > s2 > s1

論文の期待される出力:
    Example 3 (PLDA-RQ): {(s8, c2), (s1, c3), (s2, c3), (s3, c3), (s6, c4), (s4, c1), (s5, c4), (s7, c1)}
    Example 4 (RSDA-RQ): {(s4, c1), (s3, c2), (s1, c3), (s6, c4), (s7, c1), (s2, c3), (s5, c4), (s8, c1)}
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from model import Market, RegionNode, RegionTree
from mechanisms import plda_rq, rsda_rq, print_matching
from feasibility import claiming_students, check_feasible_matching_exists


# ─────────────────────────────────────────────────────────────────────────────
# 市場の定義 (Fig. 1 の木構造)
# ─────────────────────────────────────────────────────────────────────────────

def build_example_market() -> Market:
    """論文 Example 3, 4 の市場を構築する。"""

    n_students = 8
    school_names = ["c1", "c2", "c3", "c4"]

    # ── 地域木 (Fig. 1) ──────────────────────────────────────────────────
    leaf_c1 = RegionNode(name="{c1}", schools=frozenset([0]), min_quota=1, max_quota=3)
    leaf_c2 = RegionNode(name="{c2}", schools=frozenset([1]), min_quota=1, max_quota=3)
    leaf_c3 = RegionNode(name="{c3}", schools=frozenset([2]), min_quota=1, max_quota=3)
    leaf_c4 = RegionNode(name="{c4}", schools=frozenset([3]), min_quota=1, max_quota=3)

    region_r1 = RegionNode(
        name="r:{c1,c2}", schools=frozenset([0, 1]),
        min_quota=3, max_quota=5,
        children=[leaf_c1, leaf_c2],
    )
    region_r2 = RegionNode(
        name="r:{c3,c4}", schools=frozenset([2, 3]),
        min_quota=3, max_quota=5,
        children=[leaf_c3, leaf_c4],
    )
    root = RegionNode(
        name="r:{c1,c2,c3,c4}", schools=frozenset([0, 1, 2, 3]),
        min_quota=n_students, max_quota=n_students,
        children=[region_r1, region_r2],
    )
    # 親リンクを設定
    for node in [leaf_c1, leaf_c2]:
        node.parent = region_r1
    for node in [leaf_c3, leaf_c4]:
        node.parent = region_r2
    region_r1.parent = root
    region_r2.parent = root

    tree = RegionTree(root=root)

    # ── 学生の選好 (0-indexed) ───────────────────────────────────────────
    # s1, s2, s3: c4 > c3 > c2 > c1  → [3, 2, 1, 0]
    # s4, s5, s6: c4 > c1 > c2 > c3  → [3, 0, 1, 2]
    # s7, s8:     c1 > c2 > c3 > c4  → [0, 1, 2, 3]
    student_prefs = [
        [3, 2, 1, 0],  # s1
        [3, 2, 1, 0],  # s2
        [3, 2, 1, 0],  # s3
        [3, 0, 1, 2],  # s4
        [3, 0, 1, 2],  # s5
        [3, 0, 1, 2],  # s6
        [0, 1, 2, 3],  # s7
        [0, 1, 2, 3],  # s8
    ]

    # ── 学校の優先度 (0-indexed) ─────────────────────────────────────────
    # c1, c3: s1 > s2 > s3 > s4 > s5 > s6 > s7 > s8  → [0,1,2,3,4,5,6,7]
    # c2, c4: s8 > s7 > s6 > s5 > s4 > s3 > s2 > s1  → [7,6,5,4,3,2,1,0]
    school_priors = [
        [0, 1, 2, 3, 4, 5, 6, 7],  # c1
        [7, 6, 5, 4, 3, 2, 1, 0],  # c2
        [0, 1, 2, 3, 4, 5, 6, 7],  # c3
        [7, 6, 5, 4, 3, 2, 1, 0],  # c4
    ]

    # ── タイブレーク順: c1 → c2 → c3 → c4 ───────────────────────────────
    tiebreak_order = [0, 1, 2, 3]

    return Market(
        student_names=[f"s{i+1}" for i in range(n_students)],
        school_names=school_names,
        student_prefs=student_prefs,
        school_priors=school_priors,
        region_tree=tree,
        tiebreak_order=tiebreak_order,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Example 3: PLDA-RQ
# ─────────────────────────────────────────────────────────────────────────────

def run_example3():
    print("=" * 60)
    print("  Example 3: PLDA-RQ の動作確認")
    print("  (Section 5.2, Goto et al. 2016)")
    print("=" * 60)

    market = build_example_market()

    print("\n【市場の概要】")
    print("  学生数:", market.n_students)
    print("  学校数:", market.n_schools)
    print("  実行可能マッチング存在?",
          check_feasible_matching_exists(market.region_tree))

    print("\n【優先リスト PL の先頭10件】")
    pl = market.priority_list()
    for i, (s, c) in enumerate(pl[:10]):
        print(f"  {i+1}位: ({market.s_name(s)}, {market.c_name(c)})")

    print("\n【PLDA-RQ 実行】")
    result = plda_rq(market, verbose=True)

    print_matching(result, market, title="PLDA-RQ マッチング結果")

    # 論文の期待結果との照合
    expected = frozenset([
        (7, 1),  # (s8, c2)
        (0, 2),  # (s1, c3)
        (1, 2),  # (s2, c3)
        (2, 2),  # (s3, c3)
        (5, 3),  # (s6, c4)
        (3, 0),  # (s4, c1)
        (4, 3),  # (s5, c4)
        (6, 0),  # (s7, c1)
    ])
    print("\n【論文との照合】")
    if result == expected:
        print("  ✓ 論文 Example 3 の結果と一致")
    else:
        print("  ✗ 不一致")
        print("  期待値:", {(market.s_name(s), market.c_name(c)) for s, c in expected})
        print("  実際値:", {(market.s_name(s), market.c_name(c)) for s, c in result})

    # claiming students
    claiming = claiming_students(result, market)
    print(f"\n  Claiming students: {[market.s_name(s) for s in claiming]}")
    print("  ※ 論文では s1, s2, s3 が c4 の empty seat を主張 (wastefulness)")


# ─────────────────────────────────────────────────────────────────────────────
# Example 4: RSDA-RQ
# ─────────────────────────────────────────────────────────────────────────────

def run_example4():
    print("\n" + "=" * 60)
    print("  Example 4: RSDA-RQ の動作確認")
    print("  (Section 5.3, Goto et al. 2016)")
    print("=" * 60)

    market = build_example_market()

    print("\n【RSDA-RQ 実行 (ラウンドロビン: c1 → c2 → c3 → c4)】")
    round_robin_order = [0, 1, 2, 3]  # c1 → c2 → c3 → c4
    result = rsda_rq(market, round_robin_order=round_robin_order, verbose=True)

    print_matching(result, market, title="RSDA-RQ マッチング結果")

    # 論文の期待結果との照合
    expected = frozenset([
        (3, 0),  # (s4, c1)
        (2, 1),  # (s3, c2)
        (0, 2),  # (s1, c3)
        (5, 3),  # (s6, c4)
        (6, 0),  # (s7, c1)
        (1, 2),  # (s2, c3)
        (4, 3),  # (s5, c4)
        (7, 0),  # (s8, c1)
    ])
    print("\n【論文との照合】")
    if result == expected:
        print("  ✓ 論文 Example 4 の結果と一致")
    else:
        print("  ✗ 不一致")
        print("  期待値:", {(market.s_name(s), market.c_name(c)) for s, c in expected})
        print("  実際値:", {(market.s_name(s), market.c_name(c)) for s, c in result})

    claiming = claiming_students(result, market)
    print(f"\n  Claiming students: {[market.s_name(s) for s in claiming]}")
    print("  ※ 論文では s1, s2, s4 が empty seat を主張 (wastefulness)")


# ─────────────────────────────────────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_example3()
    run_example4()
