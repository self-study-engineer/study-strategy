
from ttc_algorithm import *

# ===========================================================================
# 学校選択問題の実行例（DAアルゴリズムと同一データで比較可能）
# ===========================================================================

def example_school_choice_one_to_one():
    """
    学校選択例1: 1対1（定員1の学校3校，学生3人）
    da_algorithm_exec.py の example_one_to_one と同一データ
    """
    print("=" * 50)
    print("学校選択例1: 1対1マッチング（TTC）")
    print("=" * 50)
    print()

    data = SchoolChoiceTTCInput(
        student_prefs=[
            [1, 2, 3],   # S1: C1 > C2 > C3
            [2, 3, 1],   # S2: C2 > C3 > C1
            [3, 1, 2],   # S3: C3 > C1 > C2
        ],
        school_prefs=[
            [2, 3, 1],   # C1: S2 > S3 > S1
            [1, 3, 2],   # C2: S1 > S3 > S2
            [3, 2, 1],   # C3: S3 > S2 > S1
        ],
        student_label="学生",
        school_label="学校",
    )
    school_choice_ttc(data)


def example_school_choice_many_to_one():
    """
    学校選択例2: 多対1（定員あり）
    da_algorithm_exec.py の example_many_to_one と同一データ
    """
    print("=" * 50)
    print("学校選択例2: 多対1マッチング（TTC）")
    print("=" * 50)
    print()

    data = SchoolChoiceTTCInput(
        student_prefs=[
            [1, 2, 3],   # S1: C1 > C2 > C3
            [1, 2, 3],   # S2: C1 > C2 > C3
            [2, 3, 1],   # S3: C2 > C3 > C1
            [3, 1, 2],   # S4: C3 > C1 > C2
        ],
        school_prefs=[
            [1, 2, 3, 4],   # C1: S1 > S2 > S3 > S4
            [2, 3, 4, 1],   # C2: S2 > S3 > S4 > S1
            [4, 1, 2, 3],   # C3: S4 > S1 > S2 > S3
        ],
        capacities=[1, 1, 2],
        student_label="学生",
        school_label="大学",
    )
    school_choice_ttc(data)


def example_basic():
    """
    実行例 1: 基本的な住宅配分問題
    """
    print("=" * 50)
    print("例1: 基本的な住宅配分問題")
    print("=" * 50)
    print()

    data = TTCInput(
        preferences=[
            [3, 1, 2],
            [1, 3, 2],
            [1, 2, 3],
        ],
        initial_endowment=[1, 2, 3],
        agent_label="A",
        object_label="h",
    )
    top_trading_cycles(data)

def example_multi_round():
    """
    実行例 2: サイクルが複数ラウンドにまたがる場合
    """
    print("=" * 50)
    print("例2: 複数ラウンドにわたる TTC")
    print("=" * 50)
    print()

    data = TTCInput(
        preferences=[
            [2, 1, 3, 4],
            [1, 2, 3, 4],
            [4, 2, 1, 3],
            [3, 1, 2, 4],
        ],
        initial_endowment=[1, 2, 3, 4],
        agent_label="A",
        object_label="h",
    )
    top_trading_cycles(data)


if __name__ == "__main__":
    example_school_choice_one_to_one()
    example_school_choice_many_to_one()
    example_basic()
    example_multi_round()
