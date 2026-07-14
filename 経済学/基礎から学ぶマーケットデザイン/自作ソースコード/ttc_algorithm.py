"""
Top Trading Cycles (TTC) Algorithm — トップトレーディングサイクル方式

対応するマッチング問題:
  - 住宅配分問題（各エージェントが初期保有を持ち，交換して効用を高める）
  - 腎臓交換など，初期保有のある交換経済
  - 学校選択問題（school_choice_ttc を使用）

【住宅配分問題】使い方:
  preferences      : エージェント i が望む財（オブジェクト）の選好リスト（1-indexed）
  initial_endowment: エージェント i が最初に保有する財の番号（1-indexed）
  verbose          : True のとき各ラウンドを表示

返り値:
  TTCResult.allocation[i] = エージェント i が最終的に受け取る財（0-indexed）

【学校選択問題】使い方:
  student_prefs: 学生 i の学校選好リスト（1-indexed）
  school_prefs : 学校 j の学生優先順位リスト（1-indexed）
  capacities   : 学校 j の定員（省略時はすべて 1）
  verbose      : True のとき各ラウンドを表示

返り値:
  SchoolChoiceTTCResult.student_match[i] = 学生 i に割り当てられた学校の0-index (-1 = 未配分)
"""

from dataclasses import dataclass


@dataclass
class TTCInput:
    preferences: list[list[int]]
    initial_endowment: list[int]
    agent_label: str = "A"
    object_label: str = "O"

    @property
    def n_agents(self) -> int:
        return len(self.preferences)


@dataclass
class TTCResult:
    allocation: list[int]   # allocation[i] = 財の0-index


def top_trading_cycles(data: TTCInput, verbose: bool = True) -> TTCResult:
    """
    TTC アルゴリズムを実行し，パレート効率的な配分を返す。

    各ラウンドで:
      1. 各エージェントは手持ちの未配分財の中で最も好きな財の保有者を指す
      2. 有向グラフ上のサイクルを検出する
      3. サイクル内のエージェントが互いに財を交換（確定配分）
      4. 配分済みエージェントと財を取り除いて繰り返す
    """
    N = data.n_agents
    al = data.agent_label
    ol = data.object_label

    if verbose:
        _print_preferences(data)
        print("=== TTC アルゴリズム 開始 ===\n")

    allocation: list[int] = [-1] * N

    # 現在まだ配分されていないエージェントと財
    remaining_agents: set[int] = set(range(N))
    remaining_objects: set[int] = set(range(N))

    # 各エージェントの現在の初期保有（0-indexed）
    endowment: list[int] = [e - 1 for e in data.initial_endowment]

    # 財の現在の保有者（0-indexed）
    owner: list[int] = [-1] * N
    for i in range(N):
        owner[endowment[i]] = i

    round_num = 1

    while remaining_agents:
        if verbose:
            print(f"--- ラウンド {round_num} ---")
            _print_state(remaining_agents, endowment, data)

        # --- 各エージェントが最も好きな残存財を指す ---
        points_to: dict[int, int] = {}  # agent -> agent (財の保有者)
        for agent in remaining_agents:
            top_object = _top_remaining_object(agent, data.preferences, remaining_objects)
            points_to[agent] = owner[top_object]
            if verbose:
                print(f"  {al}{agent+1} → {ol}{top_object+1}"
                      f"（保有: {al}{owner[top_object]+1}）")
        print() if verbose else None

        # --- サイクル検出 ---
        cycles = _find_cycles(points_to, remaining_agents)

        if verbose:
            for cyc in cycles:
                names = " → ".join(f"{al}{a+1}" for a in cyc)
                print(f"  サイクル: {names} → {al}{cyc[0]+1}")

        # --- サイクル内で財を交換・配分確定 ---
        for cycle in cycles:
            # cycle[0] が points_to[cycle[-1]] の財を受け取り，
            # 各エージェントは次のエージェントの財を受け取る
            cycle_objects = [endowment[a] for a in cycle]
            # cycle[i] は cycle[i-1] が指した財（cycle[i] の所持品）を受け取る
            # つまり cycle[i] は cycle[(i+1) % len] の保有財を受け取る
            # → points_to[cycle[i]] = cycle[(i+1)%len] なので，
            #   cycle[i] は endowment[points_to[cycle[i]]] を受け取る
            for i, agent in enumerate(cycle):
                received_object = cycle_objects[(i + 1) % len(cycle)]
                allocation[agent] = received_object
                if verbose:
                    print(f"  {al}{agent+1} が {ol}{received_object+1} を受け取り（確定）")

            # 配分済みエージェントと財を除外
            for obj in cycle_objects:
                remaining_objects.discard(obj)
                owner_agent = owner[obj]
                remaining_agents.discard(owner_agent)

        print() if verbose else None
        round_num += 1

    result = TTCResult(allocation=allocation)

    if verbose:
        print("=== TTC アルゴリズム 終了 ===\n")
        _print_result(result, data)

    return result


def _top_remaining_object(
    agent: int,
    preferences: list[list[int]],
    remaining: set[int],
) -> int:
    for obj_1indexed in preferences[agent]:
        obj = obj_1indexed - 1
        if obj in remaining:
            return obj
    raise ValueError(f"エージェント {agent+1} の選好リストに残存財がありません")


def _find_cycles(
    points_to: dict[int, int],
    remaining: set[int],
) -> list[list[int]]:
    """有向グラフ（各ノードの出次数 = 1）からすべてのサイクルを検出する。"""
    visited: set[int] = set()
    cycles: list[list[int]] = []

    for start in remaining:
        if start in visited:
            continue
        path: list[int] = []
        path_set: set[int] = set()
        current = start

        while True:
            if current in visited:
                break
            if current in path_set:
                # サイクル発見
                cycle_start_idx = path.index(current)
                cycles.append(path[cycle_start_idx:])
                for node in path[cycle_start_idx:]:
                    visited.add(node)
                break
            path.append(current)
            path_set.add(current)
            current = points_to[current]

    return cycles


def _print_state(
    remaining: set[int],
    endowment: list[int],
    data: TTCInput,
) -> None:
    al = data.agent_label
    ol = data.object_label
    agents_str = ", ".join(f"{al}{a+1}" for a in sorted(remaining))
    print(f"  残存エージェント: {agents_str}")



def _print_preferences(data: TTCInput) -> None:
    al = data.agent_label
    ol = data.object_label
    print("【エージェントの選好】")
    for i, pref in enumerate(data.preferences):
        row = " ".join(f"{ol}{x}" for x in pref)
        print(f"  {al}{i+1}: {row}")
    print()
    print("【初期保有】")
    for i, e in enumerate(data.initial_endowment):
        print(f"  {al}{i+1}: {ol}{e}")
    print()


def _print_result(result: TTCResult, data: TTCInput) -> None:
    al = data.agent_label
    ol = data.object_label
    print("【配分結果】")
    for i, obj in enumerate(result.allocation):
        print(f"  {al}{i+1}: {ol}{obj+1}")
    print()


# ---------------------------------------------------------------------------
# 学校選択問題 TTC
# ---------------------------------------------------------------------------

@dataclass
class SchoolChoiceTTCInput:
    """
    学校選択問題のTTC用入力。DAInputと同じ構造なので入力データを共用できる。
    """
    student_prefs: list[list[int]]   # 学生 i の学校選好リスト（1-indexed）
    school_prefs: list[list[int]]    # 学校 j の学生優先順位リスト（1-indexed）
    capacities: list[int] | None = None
    student_label: str = "S"
    school_label: str = "C"

    @property
    def n_students(self) -> int:
        return len(self.student_prefs)

    @property
    def n_schools(self) -> int:
        return len(self.school_prefs)

    def get_capacities(self) -> list[int]:
        if self.capacities is None:
            return [1] * self.n_schools
        return self.capacities


@dataclass
class SchoolChoiceTTCResult:
    student_match: list[int]         # student_match[i] = 学校の0-index (-1 = 未配分)
    school_match: list[list[int]]    # school_match[j] = 学生の0-indexリスト


def school_choice_ttc(data: SchoolChoiceTTCInput, verbose: bool = True) -> SchoolChoiceTTCResult:
    """
    学校選択問題に対するTTCアルゴリズム（二部グラフTTC）。

    各ラウンドで:
      1. 各学生は残存学校の中で最も好きな学校を指す
      2. 各学校は残存学生の中で優先順位が最も高い学生を指す
      3. 学生→学校→学生 と合成して学生間のサイクルを検出する
      4. サイクル内の各学生が自分の指した学校に確定配分される
      5. 配分済み学生を除外し，定員が尽きた学校も除外して繰り返す

    参考: Abdulkadiroğlu & Sönmez (2003) "School Choice: A Mechanism Design Approach"
    """
    S = data.n_students
    C = data.n_schools
    caps = data.get_capacities()[:]
    sl = data.student_label
    cl = data.school_label

    if verbose:
        _print_preferences_sc(data)
        print("=== TTC（学校選択）アルゴリズム 開始 ===\n")

    student_match: list[int] = [-1] * S
    school_match: list[list[int]] = [[] for _ in range(C)]

    remaining_students: set[int] = set(range(S))
    remaining_schools: set[int] = set(range(C))

    round_num = 1

    while remaining_students:
        if not remaining_schools:
            if verbose:
                unmatched = ", ".join(f"{sl}{s+1}" for s in sorted(remaining_students))
                print(f"  学校の定員がなくなりました。未配分: {unmatched}\n")
            break

        if verbose:
            print(f"--- ラウンド {round_num} ---")
            students_str = ", ".join(f"{sl}{s+1}" for s in sorted(remaining_students))
            schools_str = ", ".join(
                f"{cl}{c+1}(定員{caps[c]})" for c in sorted(remaining_schools)
            )
            print(f"  残存学生: {students_str}")
            print(f"  残存学校: {schools_str}\n")

        # 各学生が最も希望する残存学校を指す
        student_points_to: dict[int, int] = {}
        for s in remaining_students:
            student_points_to[s] = _top_remaining_object(s, data.student_prefs, remaining_schools)

        # 各学校が最も優先度の高い残存学生を指す
        school_points_to: dict[int, int] = {}
        for c in remaining_schools:
            school_points_to[c] = _top_priority_sc(c, data.school_prefs, remaining_students)

        if verbose:
            for s in sorted(remaining_students):
                c = student_points_to[s]
                print(f"  {sl}{s+1} → {cl}{c+1}")
            print()
            for c in sorted(remaining_schools):
                s = school_points_to[c]
                print(f"  {cl}{c+1} → {sl}{s+1}")
            print()

        # 学生→学校→学生 と合成してサイクル検出
        student_to_student: dict[int, int] = {
            s: school_points_to[student_points_to[s]]
            for s in remaining_students
        }
        cycles = _find_cycles(student_to_student, remaining_students)

        if verbose:
            for cycle in cycles:
                parts: list[str] = []
                for s in cycle:
                    parts.append(f"{sl}{s+1}")
                    parts.append(f"{cl}{student_points_to[s]+1}")
                print(f"  サイクル: {' → '.join(parts)} → {sl}{cycle[0]+1}")
            print()

        for cycle in cycles:
            for s in cycle:
                c = student_points_to[s]
                student_match[s] = c
                school_match[c].append(s)
                remaining_students.discard(s)
                if verbose:
                    print(f"  {sl}{s+1} が {cl}{c+1} に確定配分")
                caps[c] -= 1
                if caps[c] == 0:
                    remaining_schools.discard(c)

        if verbose:
            print()

        round_num += 1

    result = SchoolChoiceTTCResult(student_match=student_match, school_match=school_match)

    print("=== TTC（学校選択）アルゴリズム 終了 ===\n")
    _print_result_sc(result, data)

    return result


def _top_priority_sc(
    school: int,
    school_prefs: list[list[int]],
    remaining_students: set[int],
) -> int:
    for s_1indexed in school_prefs[school]:
        s = s_1indexed - 1
        if s in remaining_students:
            return s
    raise ValueError(f"学校 {school+1} の優先リストに残存学生がありません")


def _print_preferences_sc(data: SchoolChoiceTTCInput) -> None:
    sl = data.student_label
    cl = data.school_label
    print(f"【{sl} の選好】")
    for i, pref in enumerate(data.student_prefs):
        row = " ".join(f"{cl}{x}" for x in pref)
        print(f"  {sl}{i+1}: {row}")
    print()
    print(f"【{cl} の優先順位】")
    for j, pref in enumerate(data.school_prefs):
        row = " ".join(f"{sl}{x}" for x in pref)
        print(f"  {cl}{j+1}: {row}")
    caps = data.get_capacities()
    if any(c != 1 for c in caps):
        print()
        print(f"【{cl} の定員】")
        for j, c in enumerate(caps):
            print(f"  {cl}{j+1}: {c}")
    print()


def _print_result_sc(result: SchoolChoiceTTCResult, data: SchoolChoiceTTCInput) -> None:
    sl = data.student_label
    cl = data.school_label
    print("【配分結果】")
    for i, c in enumerate(result.student_match):
        partner = f"{cl}{c+1}" if c != -1 else "未配分"
        print(f"  {sl}{i+1}: {partner}")
    print()
