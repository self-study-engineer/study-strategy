from serial_dictatorship import *


def example_basic():
    """
    実行例 1: 基本的な住宅配分問題（1対1）

    エージェント3人が住宅3軒を選ぶ。優先順位は A1 > A2 > A3。
    """
    print("=" * 50)
    print("例1: 基本的な住宅配分問題（1対1）")
    print("=" * 50)
    print()

    data = SDInput(
        agent_prefs=[
            [3, 1, 2],   # A1: h3 > h1 > h2
            [1, 3, 2],   # A2: h1 > h3 > h2
            [1, 2, 3],   # A3: h1 > h2 > h3
        ],
        priority_order=[1, 2, 3],   # A1 > A2 > A3
        agent_label="A",
        object_label="h",
    )
    serial_dictatorship(data)


def example_school_choice():
    """
    実行例 2: 学校選択問題（多対1マッチング）

    5人の生徒が定員を持つ3校に配分される。
    優先順位は試験スコア順（生徒1が最高）とする。
    """
    print("=" * 50)
    print("例2: 学校選択問題（多対1マッチング）")
    print("=" * 50)
    print()

    data = SDInput(
        agent_prefs=[
            [1, 2, 3],   # 生徒1: 学校1 > 学校2 > 学校3
            [1, 2, 3],   # 生徒2: 学校1 > 学校2 > 学校3
            [2, 1, 3],   # 生徒3: 学校2 > 学校1 > 学校3
            [2, 3, 1],   # 生徒4: 学校2 > 学校3 > 学校1
            [3, 2, 1],   # 生徒5: 学校3 > 学校2 > 学校1
        ],
        priority_order=[1, 2, 3, 4, 5],   # 生徒1が最高優先
        capacities=[1, 2, 2],
        agent_label="生徒",
        object_label="学校",
    )
    serial_dictatorship(data)


def example_priority_effect():
    """
    実行例 3: 優先順位の違いが配分に与える影響

    同じ選好でも優先順位を変えると配分が大きく変わることを示す。
    """
    print("=" * 50)
    print("例3: 優先順位の違いによる配分の変化")
    print("=" * 50)
    print()

    prefs = [
        [1, 2, 3],   # A1: o1 > o2 > o3
        [1, 2, 3],   # A2: o1 > o2 > o3
        [1, 2, 3],   # A3: o1 > o2 > o3
    ]

    print("【優先順位: A1 > A2 > A3】")
    data1 = SDInput(
        agent_prefs=prefs,
        priority_order=[1, 2, 3],
        agent_label="A",
        object_label="o",
    )
    serial_dictatorship(data1)

    print("【優先順位: A3 > A2 > A1】")
    data2 = SDInput(
        agent_prefs=prefs,
        priority_order=[3, 2, 1],
        agent_label="A",
        object_label="o",
    )
    serial_dictatorship(data2)


def example_unallocated():
    """
    実行例 4: 一部のエージェントが配分なしになる場合

    オブジェクトの総定員がエージェント数より少ない場合。
    """
    print("=" * 50)
    print("例4: 余りあり（エージェント4人, 総定員2）")
    print("=" * 50)
    print()

    data = SDInput(
        agent_prefs=[
            [1, 2],   # A1: o1 > o2
            [1, 2],   # A2: o1 > o2
            [2, 1],   # A3: o2 > o1
            [2, 1],   # A4: o2 > o1
        ],
        priority_order=[1, 2, 3, 4],
        capacities=[1, 1],
        agent_label="A",
        object_label="o",
    )
    serial_dictatorship(data)


if __name__ == "__main__":
    example_basic()
    example_school_choice()
    example_priority_effect()
    example_unallocated()
