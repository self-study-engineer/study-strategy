"""
一気通貫：選好 → 拡張PS → 一般化BvN → 確定的な割り当てのくじ

記事2（1対1）では
    選好 ──[PS]──> 確率行列 ──[BvN定理]──> 置換行列のくじ
だったパイプラインを、記事3（多対1）では
    選好 ──[拡張PS]──> 期待割当 ──[一般化BvN定理]──> 純割当のくじ
に置き換える。財の定員が2以上でも、列の一部にグループ別クォータがあっても通る。

実行:
    python3 pipeline_exec.py
"""

from __future__ import annotations

from fractions import Fraction

from extended_ps_algorithm import (
    EMPTY,
    Constraint,
    ConstrainedInput,
    check_constraints,
    extended_probabilistic_serial,
)
from generalized_bvn_algorithm import (
    find_bihierarchy,
    frac_str,
    from_constrained_input,
    generalized_bvn,
    print_matrix,
    verify,
)


def header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def run(data: ConstrainedInput, title: str) -> None:
    header(title)

    # ── ステップ1: 選好 → 期待割当（拡張PS）──────────────
    print("\n─── ステップ1: 拡張PSで期待割当を求める ───\n")
    matrix = extended_probabilistic_serial(data)
    check_constraints(data, matrix)

    # ── ステップ2: 期待割当 → 制約構造（アダプタ）──────────
    print("\n─── ステップ2: 制約構造に変換する ───\n")
    X, structure = from_constrained_input(data, matrix)
    split = find_bihierarchy(structure)
    if split is None:
        print("  → bihierarchy ではない（実装可能性は保証されない）")
        return
    h1, h2 = split
    print(f"  制約集合の総数: {len(structure.sets)}")
    print(f"  → bihierarchy（H1: {len(h1)}集合 / H2: {len(h2)}集合）")
    print("\n  期待割当 X（列は " + ", ".join(matrix.columns) + "）")
    print_matrix(X, indent="    ")

    # ── ステップ3: 期待割当 → 純割当のくじ（一般化BvN）──────
    print("\n─── ステップ3: 一般化BvNで純割当のくじに分解する ───\n")
    terms = generalized_bvn(X, structure)
    print(f"  分解された純割当の数: {len(terms)}\n")
    for k, t in enumerate(terms, 1):
        print(f"  【第{k}項】 λ = {frac_str(t.weight)}")
        for i, r in enumerate(t.assignment):
            got = [matrix.columns[a] for a, v in enumerate(r) if v > 0]
            print(f"    {data.name(i)}: {', '.join(got)}")
        print()

    problems = verify(terms, X, structure)
    print("  検証: " + ("すべて OK（再構成一致・全項が制約を満たす）"
                        if not problems else "\n        ".join(problems)))


# ─────────────────────────────────────────────
# 実行例
# ─────────────────────────────────────────────

def example_school_choice() -> None:
    """学校選択：定員2の学校＋グループ別クォータ（記事3 の例2）。"""
    data = ConstrainedInput(
        prefs=[
            ["a", "b", EMPTY],   # 学生1
            ["a", "b", EMPTY],   # 学生2
            ["b", "a", EMPTY],   # 学生3
            ["b", "a", EMPTY],   # 学生4
        ],
        capacities={"a": 2, "b": 1},
        constraints=[
            Constraint(
                pairs=frozenset({(0, "a"), (1, "a"), (2, "a")}),
                upper=1,
                label="学校a は 学生1,2,3 から高々1人",
            )
        ],
        agent_names=["学生1", "学生2", "学生3", "学生4"],
        agent_label="学生",
        object_label="学校",
    )
    run(data, "学校選択：定員2の学校＋グループ別クォータ")


def example_project_assignment() -> None:
    """社内の案件アサイン：定員3の案件＋ペア禁止制約。"""
    data = ConstrainedInput(
        prefs=[
            ["A", "B", EMPTY],   # 佐藤
            ["A", "B", EMPTY],   # 鈴木
            ["A", "B", EMPTY],   # 高橋
            ["B", "A", EMPTY],   # 田中
        ],
        capacities={"A": 2, "B": 2},
        constraints=[
            Constraint(
                pairs=frozenset({(0, "A"), (1, "A")}),
                upper=1,
                label="佐藤と鈴木を案件Aで同席させない",
            )
        ],
        agent_names=["佐藤", "鈴木", "高橋", "田中"],
        agent_label="社員",
        object_label="案件",
    )
    run(data, "社内の案件アサイン：定員2の案件＋ペア禁止制約")


if __name__ == "__main__":
    example_school_choice()
    example_project_assignment()
    print()
