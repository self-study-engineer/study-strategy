"""
Immediate Acceptance Mechanism (IA) — 即時受入方式

対応するマッチング問題:
  - 学校選択問題（生徒が学校を志望し，学校が優先順位を持つ）
  - 即時確定型の多対1マッチング

使い方:
  student_prefs     : 生徒 i の選好リスト（学校の番号, 1-indexed）
  school_priorities : 学校 j の優先順位リスト（生徒の番号, 1-indexed）
  capacities        : 学校 j の定員（省略時はすべて 1）
  verbose           : True のとき各ラウンドを表示

DA との違い:
  DA は仮受入（後から置き換え可能）だが，IA は即時確定（置き換え不可）。
  そのため IA は耐戦略性を満たさず，第1志望に集中しすぎると損をする場合がある。

別名:
  Boston Mechanism とも呼ばれる（ボストン市の学校選択制度で採用されていたことに由来）。
"""

from dataclasses import dataclass


@dataclass
class IAInput:
    student_prefs: list[list[int]]
    school_priorities: list[list[int]]
    capacities: list[int] | None = None
    student_label: str = "S"
    school_label: str = "C"

    @property
    def n_students(self) -> int:
        return len(self.student_prefs)

    @property
    def n_schools(self) -> int:
        return len(self.school_priorities)

    def get_capacities(self) -> list[int]:
        if self.capacities is None:
            return [1] * self.n_schools
        return self.capacities


@dataclass
class IAResult:
    student_match: list[int]          # student_match[i] = 学校の0-index (-1 = unmatched)
    school_match: list[list[int]]     # school_match[j] = 生徒の0-indexリスト


def immediate_acceptance(data: IAInput, verbose: bool = True) -> IAResult:
    """
    Immediate Acceptance Mechanism を実行し，即時確定型のマッチングを返す。

    各ラウンドで:
      1. 未マッチの生徒が当該ラウンドの志望順位の学校に出願する
      2. 各学校は残定員の範囲で優先順位の高い生徒から即時受入（確定）する
      3. 定員を超えた生徒は即時拒否（次ラウンドへ進む）
      4. 全員マッチするか全志望校への出願が終わるまで繰り返す
    """
    S = data.n_students
    C = data.n_schools
    caps = data.get_capacities()
    sl = data.student_label
    cl = data.school_label

    p_rank = _build_priority_rank(data.school_priorities, S)

    student_match: list[int] = [-1] * S
    school_match: list[list[int]] = [[] for _ in range(C)]
    remaining_caps: list[int] = caps[:]

    unmatched: set[int] = set(range(S))

    if verbose:
        _print_preferences(data)
        print("=== Immediate Acceptance Mechanism 開始 ===\n")

    max_rounds = max(len(p) for p in data.student_prefs)

    for round_num in range(1, max_rounds + 1):
        if not unmatched:
            break

        if verbose:
            print(f"--- ラウンド {round_num} ---")

        applications: dict[int, list[int]] = {j: [] for j in range(C)}
        still_unmatched_after = set()

        for student in sorted(unmatched):
            prefs = data.student_prefs[student]
            if round_num - 1 < len(prefs):
                school = prefs[round_num - 1] - 1
                applications[school].append(student)
                if verbose:
                    print(f"  {sl}{student+1} が {cl}{school+1} に出願")
            else:
                still_unmatched_after.add(student)
                if verbose:
                    print(f"  {sl}{student+1} は志望リストが尽きた → マッチなし")

        if verbose:
            print()

        newly_unmatched: set[int] = set()
        for school, applicants in applications.items():
            if not applicants:
                continue
            if remaining_caps[school] <= 0:
                for s in applicants:
                    newly_unmatched.add(s)
                if verbose:
                    rejected = ", ".join(f"{sl}{s+1}" for s in applicants)
                    print(f"  {cl}{school+1} は定員なし → {rejected} を拒否")
                continue

            ranked = sorted(applicants, key=lambda s: p_rank[school][s])
            accepted = ranked[: remaining_caps[school]]
            rejected = ranked[remaining_caps[school] :]

            for s in accepted:
                student_match[s] = school
                school_match[school].append(s)
                remaining_caps[school] -= 1
                if verbose:
                    print(f"  {cl}{school+1} が {sl}{s+1} を受入（確定）")

            for s in rejected:
                newly_unmatched.add(s)
                if verbose:
                    print(f"  {cl}{school+1} が {sl}{s+1} を拒否")

        if verbose:
            print()

        unmatched = newly_unmatched | still_unmatched_after

    result = IAResult(
        student_match=student_match,
        school_match=school_match,
    )

    if verbose:
        print("=== Immediate Acceptance Mechanism 終了 ===\n")
        _print_result(result, data)

    return result


def _build_priority_rank(
    priorities: list[list[int]],
    n_students: int,
) -> list[list[int]]:
    """優先順位リスト (1-indexed) を順位表 (0-indexed) に変換する。"""
    rank = [[n_students] * n_students for _ in range(len(priorities))]
    for j, row in enumerate(priorities):
        for r, student in enumerate(row):
            rank[j][student - 1] = r
    return rank


def _print_preferences(data: IAInput) -> None:
    sl = data.student_label
    cl = data.school_label
    print(f"【{sl} の選好】")
    for i, pref in enumerate(data.student_prefs):
        row = " ".join(f"{cl}{x}" for x in pref)
        print(f"  {sl}{i+1}: {row}")
    print()
    print(f"【{cl} の優先順位】")
    for j, pri in enumerate(data.school_priorities):
        row = " ".join(f"{sl}{x}" for x in pri)
        print(f"  {cl}{j+1}: {row}")
    caps = data.get_capacities()
    if any(c != 1 for c in caps):
        print()
        print(f"【{cl} の定員】")
        for j, c in enumerate(caps):
            print(f"  {cl}{j+1}: {c}")
    print()


def _print_result(result: IAResult, data: IAInput) -> None:
    sl = data.student_label
    cl = data.school_label
    print("【マッチング結果】")
    for i, c in enumerate(result.student_match):
        partner = f"{cl}{c+1}" if c != -1 else "マッチなし"
        print(f"  {sl}{i+1}: {partner}")
    print()
