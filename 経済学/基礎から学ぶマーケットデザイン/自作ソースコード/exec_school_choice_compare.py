from da_algorithm import *;
from ttc_algorithm import *;

def example_school_choice_many_to_one_with_ttc():
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
    school_choice_ttc(data, False)


def example_many_to_one_with_da():
    """
    例2: 多対1マッチング（学生・研究室配属）
    """
    print("=" * 50)
    print("例2: 多対1マッチング（学生提案 DA）")
    print("=" * 50)
    print()

    data = DAInput(
        proposer_prefs=[
            [1, 2, 3],
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ],
        receiver_prefs=[
            [1, 2, 3, 4],
            [2, 3, 4, 1],
            [4, 1, 2, 3],
        ],
        capacities=[1, 1, 2],
        proposer_label="学生",
        receiver_label="大学",
    )
    deferred_acceptance(data, False)


def _compare(da_data: DAInput, ttc_data: SchoolChoiceTTCInput) -> None:
    """DA と TTC を同一データで実行し、結果を並べて表示する。"""
    da_result  = deferred_acceptance(da_data, verbose=False)
    ttc_result = school_choice_ttc(ttc_data, verbose=False)

    sl = ttc_data.student_label
    cl = ttc_data.school_label
    n  = ttc_data.n_students

    print(f"{'学生':<6} {'DA 結果':<10} {'TTC 結果':<10} 差異")
    print("-" * 36)
    for i in range(n):
        da_school  = da_result.proposer_match[i]
        ttc_school = ttc_result.student_match[i]
        da_str  = f"{cl}{da_school+1}"  if da_school  != -1 else "未配分"
        ttc_str = f"{cl}{ttc_school+1}" if ttc_school != -1 else "未配分"
        diff = "← 異なる" if da_school != ttc_school else ""
        print(f"{sl}{i+1:<5} {da_str:<10} {ttc_str:<10} {diff}")
    print()


def example_compare_1():
    """
    比較例1: 3学生・3学校（定員1）— DA と TTC で結果が異なるケース

    ポイント:
      S1 と S2 が互いの第1希望を交換できる状況。
      DA は安定性（優先順位）を守るため S1・S2 がともに第2希望に落ちる。
      TTC は交換サイクル（S1→C1, C1→S2, S2→C2, C2→S1）を検出し
      S1・S2 がともに第1希望を獲得する（ただし安定性は失われる）。
    """
    print("=" * 60)
    print("比較例1: 3学生・3学校（DA vs TTC 結果が異なる）")
    print("=" * 60)

    da_data = DAInput(
        proposer_prefs=[
            [1, 2, 3],   # S1: C1 > C2 > C3
            [2, 1, 3],   # S2: C2 > C1 > C3
            [1, 2, 3],   # S3: C1 > C2 > C3
        ],
        receiver_prefs=[
            [2, 3, 1],   # C1: S2 > S3 > S1
            [1, 3, 2],   # C2: S1 > S3 > S2
            [1, 2, 3],   # C3: S1 > S2 > S3
        ],
        proposer_label="学生",
        receiver_label="学校",
    )
    ttc_data = SchoolChoiceTTCInput(
        student_prefs=da_data.proposer_prefs,
        school_prefs=da_data.receiver_prefs,
        student_label="学生",
        school_label="学校",
    )

    print()
    print("【学生の選好】")
    print("  S1: C1 > C2 > C3    S2: C2 > C1 > C3    S3: C1 > C2 > C3")
    print("【学校の優先順位】")
    print("  C1: S2 > S3 > S1    C2: S1 > S3 > S2    C3: S1 > S2 > S3")
    print()

    _compare(da_data, ttc_data)

    print("【解説】")
    print("  DA : S1・S2 が C1 を争い連鎖的に押し出され、どちらも第2希望へ")
    print("  TTC: S1→C1→S2→C2→S1 のサイクルでS1・S2が第1希望を獲得")
    print("       （C1でS3がS1より優先度高 → 安定性は失われる）")
    print()


def example_compare_2():
    """
    比較例2: 4学生・4学校（定員1）— S2 と S3 が C3 を争うケース

    ポイント:
      S2 と S3 が同じ第1希望（C3）を持つ。C3 は S2 を優先するため DA では S2→C3。
      TTC では S1→C2 と S3→C3 が交換サイクルを形成し S3 が C3 を獲得する
      一方 S2 は第2希望（C1）に落ちる。
      DA と TTC でどちらの学生が得をするかが入れ替わる典型例。
    """
    print("=" * 60)
    print("比較例2: 4学生・4学校（DA vs TTC 利得関係が逆転）")
    print("=" * 60)

    da_data = DAInput(
        proposer_prefs=[
            [2, 3, 1, 4],   # S1: C2 > C3 > C1 > C4
            [3, 1, 2, 4],   # S2: C3 > C1 > C2 > C4
            [3, 1, 2, 4],   # S3: C3 > C1 > C2 > C4
            [4, 1, 2, 3],   # S4: C4 > C1 > C2 > C3
        ],
        receiver_prefs=[
            [2, 3, 4, 1],   # C1: S2 > S3 > S4 > S1
            [3, 1, 4, 2],   # C2: S3 > S1 > S4 > S2
            [1, 2, 4, 3],   # C3: S1 > S2 > S4 > S3
            [4, 1, 2, 3],   # C4: S4 > S1 > S2 > S3
        ],
        proposer_label="学生",
        receiver_label="学校",
    )
    ttc_data = SchoolChoiceTTCInput(
        student_prefs=da_data.proposer_prefs,
        school_prefs=da_data.receiver_prefs,
        student_label="学生",
        school_label="学校",
    )

    print()
    print("【学生の選好】")
    print("  S1: C2>C3>C1>C4    S2: C3>C1>C2>C4")
    print("  S3: C3>C1>C2>C4    S4: C4>C1>C2>C3")
    print("【学校の優先順位】")
    print("  C1: S2>S3>S4>S1    C2: S3>S1>S4>S2")
    print("  C3: S1>S2>S4>S3    C4: S4>S1>S2>S3")
    print()

    _compare(da_data, ttc_data)

    print("【解説】")
    print("  DA : C3 は S1>S2>S4>S3 の優先順位 → S2 が C3 を獲得、S3 は C1 へ")
    print("  TTC: S1→C2, C2→S3, S3→C3, C3→S1 のサイクルで S3 が C3 を獲得")
    print("       S2 は C3 から外れ C1 へ → DA:S2有利、TTC:S3有利")
    print()


if __name__ == "__main__":
    # 比較テストデータ（DA と TTC で結果が異なる）
    example_compare_1()
    example_compare_2()

    # 既存の比較例
    example_school_choice_many_to_one_with_ttc()
    example_many_to_one_with_da()
