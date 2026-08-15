"""
拡張RPメカニズムの実行例 — 会社の案件割り当て

  実行例1: 1案件に複数人（A=3人, B=2人, C=1人）
  実行例2: ペアにしてはいけない社員がいる
  実行例3: 若手だけで案件を埋めてはいけない
  実行例4: 実行例2と実行例3を組み合わせた大きめの割り当て（社員16人・案件6種類）
  実行例5: 拡張RPが順序効率的とは限らないことを示す例（第7章 例1 と同型）
"""

import random
from extended_rp_algorithm import (
    EMPTY,
    ConstrainedInput,
    at_most_juniors,
    check_constraints,
    extended_random_priority,
    forbid_pair,
    print_input,
    print_result,
)
from extended_assignment_check import check_all

# 表示に使う社員名（agent_names）
NAMES = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺"]


def example1(verbose: bool = True) -> None:
    """実行例1: 1案件に複数人を割り当てる（A=3人, B=2人, C=1人）。

    社員6人を必要人数の異なる3案件に割り当てる。案件Aを4人が第1希望にして競合する。
    """
    print("=" * 56)
    print("実行例1: 1案件に複数人を割り当てる（A=3人, B=2人, C=1人）")
    print("=" * 56)
    print()

    data = ConstrainedInput(
        prefs=[
            ["A", "B", "C", EMPTY],   # 佐藤
            ["A", "B", "C", EMPTY],   # 鈴木
            ["A", "C", "B", EMPTY],   # 高橋
            ["A", "B", "C", EMPTY],   # 田中
            ["B", "A", "C", EMPTY],   # 伊藤
            ["C", "B", "A", EMPTY],   # 渡辺
        ],
        capacities={"A": 3, "B": 2, "C": 1},
        agent_names=NAMES,
    )
    print_input(data)
    matrix = extended_random_priority(data, verbose=False)
    print_result(data, matrix, "拡張RPメカニズムの期待行列")
    check_constraints(data, matrix, verbose=verbose)
    check_all(data, matrix, mechanism=extended_random_priority, verbose=verbose)
    print()


def example2(verbose: bool = True) -> None:
    """実行例2: ペアにしてはいけない社員がいる割り当て。

    鈴木と高橋は同じ案件に入れない（各案件で 2 人の同席を禁止）。
    2人とも案件Aを希望するが同席は不可なので，必ず別々の案件になる。
    """
    print("=" * 56)
    print("実行例2: ペアにしてはいけない社員がいる割り当て")
    print("=" * 56)
    print()

    data = ConstrainedInput(
        prefs=[
            ["A", "B", "C", EMPTY],   # 佐藤
            ["A", "B", "C", EMPTY],   # 鈴木 ← ペア対象
            ["A", "B", "C", EMPTY],   # 高橋 ← ペア対象
            ["B", "A", "C", EMPTY],   # 田中
            ["B", "C", "A", EMPTY],   # 伊藤
        ],
        capacities={"A": 2, "B": 2, "C": 1},
        constraints=forbid_pair(1, 2, ["A", "B", "C"], names=("鈴木", "高橋")),
        agent_names=NAMES[:5],
    )
    print_input(data)
    matrix = extended_random_priority(data, verbose=False)
    print_result(data, matrix, "拡張RPメカニズムの期待行列")
    check_constraints(data, matrix, verbose=verbose)
    check_all(data, matrix, mechanism=extended_random_priority, verbose=verbose)
    print()


def example3(verbose: bool = True) -> None:
    """実行例3: 若手だけで案件を埋めてはいけない割り当て。

    若手=鈴木(2年)・高橋(1年)・伊藤(3年)。各案件（定員2）の若手は最大1人とし，
    必ず1枠を中堅以上（佐藤・田中・渡辺）に確保する。
    """
    print("=" * 56)
    print("実行例3: 若手だけで案件を埋めてはいけない割り当て")
    print("=" * 56)
    print()

    juniors = [1, 2, 4]  # 鈴木・高橋・伊藤
    data = ConstrainedInput(
        prefs=[
            ["A", "B", EMPTY],   # 佐藤（中堅以上）
            ["A", "B", EMPTY],   # 鈴木（若手）
            ["A", "B", EMPTY],   # 高橋（若手）
            ["B", "A", EMPTY],   # 田中（中堅以上）
            ["A", "B", EMPTY],   # 伊藤（若手）
            ["B", "A", EMPTY],   # 渡辺（中堅以上）
        ],
        capacities={"A": 2, "B": 2},
        constraints=[
            at_most_juniors(juniors, "A", cap=1),
            at_most_juniors(juniors, "B", cap=1),
        ],
        agent_names=NAMES,
    )
    print_input(data)
    matrix = extended_random_priority(data, verbose=False)
    print_result(data, matrix, "拡張RPメカニズムの期待行列")
    check_constraints(data, matrix, verbose=verbose)
    check_all(data, matrix, mechanism=extended_random_priority, verbose=verbose)
    print()


def example4(verbose: bool = True) -> None:
    """実行例4: 禁止ペアと若手制約を組み合わせた割り当て（社員16人・案件6種類）。

    実行例2（ペア禁止）と実行例3（若手だけで埋めない）を同時に課す大きめの例。
    案件: A,B（定員3）/ C,D,E（定員2）/ F（定員1）。合計13で，16人中3人は ∅。
    選好はランダム(seed=3)。制約は次の組み合わせ:
      - 高橋と渡辺は同じ案件に入れない（各案件で同席不可）。
      - 定員2以上の各案件で若手は最大「定員−1」人（必ず中堅以上を1枠確保）。
    社員16人では全 16! 通りの優先順位の列挙は不可能なので，モンテカルロ近似（50,000回）で
    確率を求める（小数表示）。
    """
    print("=" * 56)
    print("実行例4: 禁止ペア＋若手制約の組み合わせ（社員16人・案件6種類）")
    print("=" * 56)
    print()

    names = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
             "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上"]
    goods = ["A", "B", "C", "D", "E", "F"]
    capacities = {"A": 3, "B": 3, "C": 2, "D": 2, "E": 2, "F": 1}
    juniors = [1, 2, 4, 7, 9, 11, 13, 15]   # 若手8人（鈴木・高橋・伊藤・中村・加藤・山田・山口・井上）
    constraints = forbid_pair(2, 5, goods, names=("高橋", "渡辺"))
    constraints += [at_most_juniors(juniors, g, cap=capacities[g] - 1) for g in goods if capacities[g] >= 2]

    rng = random.Random(3)
    prefs = []
    for _ in range(16):
        order = goods[:]
        rng.shuffle(order)
        prefs.append([*order, EMPTY])
    data = ConstrainedInput(prefs=prefs, capacities=capacities, constraints=constraints, agent_names=names)

    print_input(data)
    matrix = extended_random_priority(data, n_samples=50_000, seed=1, verbose=False)
    print_result(data, matrix, "拡張RPメカニズムの期待行列（モンテカルロ近似）", as_float=True)
    check_constraints(data, matrix, verbose=verbose)
    print()


def example5(verbose: bool = True) -> None:
    """実行例5: 拡張RPが順序効率的とは限らないことを示す例（第7章 例1 と同型）。

    社員4人・案件A,B（必要人数各1）。佐藤・鈴木は A>B、高橋・田中は B>A。
    追加制約なしの拡張RPは基本RPと一致し、期待行列（A列: 5/12, 5/12, 1/12, 1/12）は
    順序効率性を満たさない（LP判定で改善割当が見つかる）。同じ入力を拡張PSで解くと
    順序効率的な期待行列（1/2, 0, 1/2 型）になる（extended_ps_algorithm_exec の
    実行例5参照）。拡張RPの限界と拡張PSの利点を対で示す例。
    """
    print("=" * 56)
    print("実行例5: 拡張RPが順序効率的とは限らない例（4人・2案件）")
    print("=" * 56)
    print()

    data = ConstrainedInput(
        prefs=[
            ["A", "B", EMPTY],   # 佐藤
            ["A", "B", EMPTY],   # 鈴木
            ["B", "A", EMPTY],   # 高橋
            ["B", "A", EMPTY],   # 田中
        ],
        capacities={"A": 1, "B": 1},
        agent_names=NAMES[:4],
    )
    print_input(data)
    matrix = extended_random_priority(data, verbose=False)
    print_result(data, matrix, "拡張RPメカニズムの期待行列")
    check_constraints(data, matrix, verbose=verbose)
    check_all(data, matrix, mechanism=extended_random_priority, verbose=verbose)
    print()


if __name__ == "__main__":
    example1()
    example2()
    example3()
    example4()
    example5()
