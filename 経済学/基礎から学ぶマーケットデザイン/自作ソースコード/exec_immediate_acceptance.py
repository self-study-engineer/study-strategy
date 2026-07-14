from immediate_acceptance import *


def example_basic():
    """
    実行例 1: 基本的な学校選択問題（1対1マッチング）

    DA と比較すると:
      - DA では生徒が全員第1志望に最適にマッチされる可能性があるが，
        IA では第1志望集中による「押し出し」が即時確定するため結果が変わる。
    """
    print("=" * 50)
    print("例1: 基本的な学校選択問題（1対1マッチング）")
    print("=" * 50)
    print()

    data = IAInput(
        student_prefs=[
            [1, 2, 3],   # s1: c1 > c2 > c3
            [1, 2, 3],   # s2: c1 > c2 > c3
            [2, 1, 3],   # s3: c2 > c1 > c3
        ],
        school_priorities=[
            [2, 1, 3],   # c1: s2 > s1 > s3
            [1, 3, 2],   # c2: s1 > s3 > s2
            [1, 2, 3],   # c3: s1 > s2 > s3
        ],
        student_label="生徒",
        school_label="学校",
    )
    immediate_acceptance(data)


def example_many_to_one():
    """
    実行例 2: 多対1マッチング（学校の定員が複数）
    """
    print("=" * 50)
    print("例2: 多対1マッチング（学校の定員が複数）")
    print("=" * 50)
    print()

    data = IAInput(
        student_prefs=[
            [1, 2, 3],   # s1: c1 > c2 > c3
            [1, 2, 3],   # s2: c1 > c2 > c3
            [1, 3, 2],   # s3: c1 > c3 > c2
            [2, 1, 3],   # s4: c2 > c1 > c3
            [3, 1, 2],   # s5: c3 > c1 > c2
        ],
        school_priorities=[
            [1, 2, 3, 4, 5],   # c1: s1 > s2 > s3 > s4 > s5
            [3, 4, 1, 2, 5],   # c2: s3 > s4 > s1 > s2 > s5
            [5, 1, 2, 3, 4],   # c3: s5 > s1 > s2 > s3 > s4
        ],
        capacities=[2, 2, 1],
        student_label="生徒",
        school_label="学校",
    )
    immediate_acceptance(data)


def example_strategy_vulnerability():
    """
    実行例 3: 耐戦略性の欠如を示す例

    生徒3が正直に第1志望（学校2）を申告すると学校3に押し出される。
    しかし第1志望として学校3を申告（戦略的操作）すると学校3を確保できる。
    → IA は耐戦略性を満たさないため，正直申告が支配戦略とはならない。
    """
    print("=" * 50)
    print("例3: 耐戦略性の欠如（正直申告 vs 戦略的操作）")
    print("=" * 50)
    print()

    print("【正直申告の場合】")
    data_honest = IAInput(
        student_prefs=[
            [1, 2, 3],   # s1: c1 > c2 > c3
            [1, 2, 3],   # s2: c1 > c2 > c3
            [2, 3, 1],   # s3（正直）: c2 > c3 > c1
        ],
        school_priorities=[
            [1, 2, 3],   # c1: s1 > s2 > s3
            [1, 2, 3],   # c2: s1 > s2 > s3
            [3, 1, 2],   # c3: s3 > s1 > s2
        ],
        student_label="生徒",
        school_label="学校",
    )
    immediate_acceptance(data_honest)

    print("【生徒3が戦略的操作（第1志望を学校3に変更）した場合】")
    data_strategic = IAInput(
        student_prefs=[
            [1, 2, 3],   # s1: c1 > c2 > c3
            [1, 2, 3],   # s2: c1 > c2 > c3
            [3, 2, 1],   # s3（操作）: c3 > c2 > c1
        ],
        school_priorities=[
            [1, 2, 3],
            [1, 2, 3],
            [3, 1, 2],
        ],
        student_label="生徒",
        school_label="学校",
    )
    immediate_acceptance(data_strategic)


def example_unmatched():
    """
    実行例 4: 定員超過により一部の生徒がマッチなしになる場合
    """
    print("=" * 50)
    print("例4: 余りあり（生徒4人, 総定員3）")
    print("=" * 50)
    print()

    data = IAInput(
        student_prefs=[
            [1, 2],   # s1: c1 > c2
            [1, 2],   # s2: c1 > c2
            [1, 2],   # s3: c1 > c2
            [1, 2],   # s4: c1 > c2
        ],
        school_priorities=[
            [1, 2, 3, 4],   # c1（定員1）: s1 > s2 > s3 > s4
            [2, 3, 4, 1],   # c2（定員2）: s2 > s3 > s4 > s1
        ],
        capacities=[1, 2],
        student_label="生徒",
        school_label="学校",
    )
    immediate_acceptance(data)


if __name__ == "__main__":
    example_basic()
    example_many_to_one()
    example_strategy_vulnerability()
    example_unmatched()
