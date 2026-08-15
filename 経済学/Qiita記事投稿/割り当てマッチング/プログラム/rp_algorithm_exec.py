"""
RPメカニズムの実行例（『マッチング理論とマーケットデザイン』）。
"""

import random
from rp_algorithm import EMPTY, Input, random_priority, print_input, print_result
from assignment_check import check_all

# 表示に使う個人名（agent_names）
NAMES = ["佐藤", "鈴木", "高橋", "田中"]


def example1(verbose: bool = True) -> None:
    """例1: 個人4人・財2つ。

    選好  ≻1,≻2: a, b, ∅      ≻3,≻4: b, a, ∅      供給 q_a = q_b = 1
    教科書の確率行列:
        佐藤,鈴木: a=5/12, b=1/12, ∅=1/2
        高橋,田中: a=1/12, b=5/12, ∅=1/2
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
    matrix = random_priority(data, verbose=False)
    print_result(data, matrix, "RPメカニズムの確率行列")
    check_all(data, matrix, mechanism=random_priority, verbose=verbose)
    print()


def example1_monte_carlo() -> None:
    """例1の補足: 同じ問題をモンテカルロ近似で解き，厳密値に近づくことを確認する。"""
    print("=" * 56)
    print("例: モンテカルロ近似（厳密値 5/12≈0.417 と比較）")
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
    matrix = random_priority(data, n_samples=200_000, seed=42, verbose=False)
    print("近似確率行列（200,000 回サンプリング, 小数表示）:")
    for i, row in enumerate(matrix.rows):
        cells = "  ".join(f"{float(p):.3f}" for p in row)
        print(f"  {data.name(i)}: {cells}   （列: a, b, ∅）")
    print()


def example2(verbose: bool = True) -> None:
    """例2: 耐戦略性を満たすことの確認

    選好  ≻1: a, b, ∅   ≻2: a, ∅   ≻3: b, ∅   ≻4: b, ∅
    この選好は PSメカニズムでは佐藤が ≻1': b, a, ∅ と偽ると得をする反例だが，
    RPメカニズムではどの個人も虚偽申告で正直申告の割り当てを上回れない。
    → 耐戦略性が ✅ になることを確認する。
    """
    print("=" * 56)
    print("例2: 耐戦略性を満たすことの確認")
    print("=" * 56)
    print()

    data = Input(
        prefs=[
            ["a", "b", EMPTY],   # 佐藤
            ["a", EMPTY],        # 鈴木
            ["b", EMPTY],        # 高橋
            ["b", EMPTY],        # 田中
        ],
        capacities={"a": 1, "b": 1},
        agent_names=NAMES,
    )
    print_input(data)
    matrix = random_priority(data, verbose=False)
    print_result(data, matrix, "RPメカニズムの確率行列")
    check_all(data, matrix, mechanism=random_priority, verbose=verbose)
    print()


def example3(verbose: bool = True) -> None:
    """例3: 確率行列をそのまま表示できる最大規模（個人8人）の例。

    RPメカニズムの厳密計算は全 n! 通りの優先順位を列挙するため，ここが律速になる。
        n=8 : 8! = 40,320 通り  ≈ 0.3 秒
        n=9 : 9! = 362,880 通り ≈ 3 秒（実用上の上限）
        n=10: 10! = 3,628,800 通り ≈ 30 秒（実用外）
        n≥11: 非現実的
    よって確率行列をそのまま表示できる実用的な上限はおおむね 8〜9 人。
    （PSは決定的で高速だが，RPと揃えて厳密な確率行列を出せる上限がRP側で決まる。）
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
    matrix = random_priority(data, verbose=False)   # 厳密計算（8! 通りを列挙）
    print_result(data, matrix, "RPメカニズムの確率行列（n=8, 厳密計算）")
    check_all(data, matrix, mechanism=None, verbose=verbose) # メカニズムをNoneにすることで対戦略性のチェックをスキップ
    print()


if __name__ == "__main__":
    example1()
    example1_monte_carlo()
    example2()
    example3()
