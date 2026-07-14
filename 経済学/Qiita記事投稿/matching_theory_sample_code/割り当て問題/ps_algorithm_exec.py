"""
PSメカニズムの実行例（『マッチング理論とマーケットデザイン』）
"""
# pyright: reportArgumentType=false

import random
from ps_algorithm import EMPTY, Input, probabilistic_serial, print_input, print_result
from assignment_check import check_all

# 表示に使う個人名（agent_names）
NAMES = ["佐藤", "鈴木", "高橋", "田中"]


def example1(verbose: bool = True) -> None:
    """例1: 個人4人・財2つ。

    選好  ≻1,≻2: a, b, ∅      ≻3,≻4: b, a, ∅
    教科書の確率行列:
        佐藤,鈴木: (a, b, ∅) = (1/2, 0, 1/2)
        高橋,田中: (a, b, ∅) = (0, 1/2, 1/2)
    """
    print("=" * 56)
    print("例1: 個人4人・財2つ")
    print("=" * 56)
    print()

    data = Input(
        prefs=[
            ["a", "b", EMPTY],
            ["a", "b", EMPTY],
            ["b", "a", EMPTY],
            ["b", "a", EMPTY],
        ],
        capacities={"a": 1, "b": 1},
        agent_names=NAMES,
    )
    print_input(data)
    matrix = probabilistic_serial(data, verbose=False)
    print_result(data, matrix, "PSメカニズムの確率行列")
    check_all(data, matrix, mechanism=probabilistic_serial, verbose=verbose)
    print()


def example2(verbose: bool = True) -> None:
    """例2: 耐戦略性を満たさないケース。

    選好  ≻1: a, b, ∅   ≻2: a, ∅   ≻3: b, ∅   ≻4: b, ∅
    正直申告のときの佐藤の割り当ては (a, b, ∅) = (1/2, 0, 1/2) だが，
    佐藤が選好を ≻1': b, a, ∅ と偽ると割り当てが (1/3, 1/3, 1/3) になる。
    正直申告の割り当てが虚偽申告の割り当てを弱確率支配しないため，佐藤の
    効用の取り方によっては虚偽申告が有利になりうる。
    → 耐戦略性が ❌ になることを確認する。
    """
    print("=" * 56)
    print("例2: 耐戦略性を満たさないケース")
    print("=" * 56)
    print()

    data = Input(
        prefs=[
            ["a", "b", EMPTY],   # 佐藤（真の選好。b, a, ∅ と偽ると得をしうる）
            ["a", EMPTY],        # 鈴木
            ["b", EMPTY],        # 高橋
            ["b", EMPTY],        # 田中
        ],
        capacities={"a": 1, "b": 1},
        agent_names=NAMES,
    )
    print_input(data)
    matrix = probabilistic_serial(data, verbose=False)
    print_result(data, matrix, "PSメカニズムの確率行列")
    check_all(data, matrix, mechanism=probabilistic_serial, verbose=verbose)
    print()


def example3(verbose: bool = True) -> None:
    """例3: 確率行列をそのまま表示できる最大規模（個人8人）の例。

    PSは決定的で n が大きくても高速に計算できるが，同じ問題を RPメカニズムで
    厳密に出すには全 n! 通りの優先順位の列挙が必要で，こちらが律速になる。
        n=8 : 8! = 40,320 通り  ≈ 0.3 秒
        n=9 : 9! = 362,880 通り ≈ 3 秒（実用上の上限）
        n=10: 10! = 3,628,800 通り ≈ 30 秒（実用外）/ n≥11: 非現実的
    よって RP と揃えて確率行列をそのまま表示できる実用的な上限はおおむね 8〜9 人。
    """
    print("=" * 56)
    print("例3: 確率行列を表示できる最大規模（個人8人・財4種類）")
    print("=" * 56)
    print()

    rng = random.Random(2)
    goods = ["a", "b", "c", "d"]
    capacities = {"a": 1, "b": 1, "c": 1, "d": 3}   # 合計6（残り2人は∅）
    prefs = []
    for _ in range(8):
        order = goods[:]
        rng.shuffle(order)
        prefs.append([*order, EMPTY])
    data = Input(prefs=prefs, capacities=capacities)

    print_input(data)
    matrix = probabilistic_serial(data, verbose=False)
    print_result(data, matrix, "PSメカニズムの確率行列（n=8, 厳密計算）")
    check_all(data, matrix, mechanism=probabilistic_serial, verbose=verbose)
    print()


def example4() -> None:
    """例3: 大きな市場（個人40人・財20種類）にPSメカニズムを適用する。

    財20種類のうち15種類は供給数1，残り5種類は供給数3（合計供給30）。
    PSは決定的なので厳密に計算できる。ただし40×21の確率行列は巨大（分母が数百万に
    なる）なので，希望順位ごとの割当人数（期待値）で結果を要約する。
    """
    print("=" * 56)
    print("例4: 大きな市場（個人40人・財20種類）— PSメカニズム")
    print("=" * 56)
    print()
    print("財20種類: 供給数1が15種類, 供給数3が5種類（合計供給30）/ 選好はランダム(seed=0)")
    print()

    rng = random.Random(0)
    goods = [chr(ord("a") + k) for k in range(20)]          # a〜t
    capacities = {g: (1 if k < 15 else 3) for k, g in enumerate(goods)}
    prefs = []
    for _ in range(40):
        order = goods[:]
        rng.shuffle(order)
        prefs.append([*order, EMPTY])
    data = Input(prefs=prefs, capacities=capacities)
    matrix = probabilistic_serial(data, verbose=False)
    print_result(data, matrix, "PSメカニズムの確率行列")


if __name__ == "__main__":
    example1()
    example2()
    example3()
    example4()
