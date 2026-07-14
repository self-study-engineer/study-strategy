"""
assignment_check.py — 確率的割り当て（RP / PS）の性質検証・比較モジュール

検証する性質（『マッチング理論とマーケットデザイン』第7章）:
  1. 水平性     （Equal Treatment of Equals）: 同じ選好を申告した個人には同じ確率。
  2. 無羨望性   （Envy-freeness）            : 各個人が自分の割り当てを，他人の割り当て
                                               より（自分の選好で）弱確率支配する。
  3. 順序効率性 （Ordinal / sd-Efficiency）  : 他のどんな割り当てにも確率支配されない。
                                               「確率を融通し合っても誰も得できない」状態。
  4. 耐戦略性   （Strategy-proofness）        : どんな虚偽申告をしても，正直申告の割り当てを
                                               上回れない（メカニズム単位の性質）。

実装方針:
  - すべて Fraction で厳密に判定する。
  - 順序効率性は「非浪費性 ∧ 関係 τ_P の非巡回性」で判定する。
    Bogomolnaia–Moulin (2001) の特徴づけ「τ_P が非巡回 ⟺ 順序効率的」は
    外部オプションや余剰供給のない（全財が完全配分される）設定のものであり，
    ∅ や供給の余りがある本設定では「非浪費性」（余っている財より好みの劣る
    対象を正の確率で消費していないこと）を併せて確認する必要がある。
    τ_P: 財 a→b ⟺ ある個人 i が a を正の確率で消費し（P_{ia}>0），かつ b≻_i a。
    巡回があれば，その個人たちで確率を交換して全員が得できる＝非効率。
  - 耐戦略性は，各個人の全虚偽申告（O∪{∅} の全順序）を列挙してメカニズムを
    再実行し，正直申告が虚偽申告を弱確率支配しないケースを探す。
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction
from itertools import permutations
from typing import Callable

from rp_algorithm import EMPTY, Input, ProbabilityMatrix

# メカニズム = 入力を受け取り確率行列を返す関数
Mechanism = Callable[..., ProbabilityMatrix]


# ─────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────

@dataclass
class CheckResult:
    """性質検証の結果。"""

    passed: bool
    violations: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.passed

    def __str__(self) -> str:
        status = "✅ 成立" if self.passed else "❌ 不成立"
        if self.violations:
            detail = "\n".join(f"    - {v}" for v in self.violations)
            return f"{status}\n{detail}"
        return status


# ─────────────────────────────────────────────
# 確率支配（first-order stochastic dominance）の補助関数
# ─────────────────────────────────────────────

def _full_ranking(data: Input, agent: int) -> list[str]:
    """個人 agent の全列（財＋∅）に対する全順序（好きな順）を返す。

    申告選好（∅ まで）の後ろに，申告しなかった財（＝∅ より下位）を並べる。
    """
    pref = data.acceptable_pref(agent)
    listed = set(pref)
    rest = [c for c in data.columns() if c not in listed]
    return pref + rest


def _cumulative(row: list[Fraction], columns: list[str], ranking: list[str]) -> list[Fraction]:
    """ranking の各接頭辞（上位集合）に対する累積確率を返す。

    cumulative[k] = ranking[:k+1] に含まれる財を受け取る確率の和
                  = 「ranking[k] 以上に好ましい財を得る確率」。
    """
    col_index = {c: k for k, c in enumerate(columns)}
    cums: list[Fraction] = []
    s = Fraction(0)
    for obj in ranking:
        s += row[col_index[obj]]
        cums.append(s)
    return cums


def _weakly_sd_dominates(
    row_x: list[Fraction],
    row_y: list[Fraction],
    columns: list[str],
    ranking: list[str],
) -> bool:
    """ranking（ある個人の選好）のもとで row_x が row_y を弱確率支配するか。

    すべての上位集合について累積確率が row_x ≥ row_y であれば True。
    """
    cx = _cumulative(row_x, columns, ranking)
    cy = _cumulative(row_y, columns, ranking)
    return all(a >= b for a, b in zip(cx, cy))


# ─────────────────────────────────────────────
# 各性質の検証
# ─────────────────────────────────────────────

def check_equal_treatment(data: Input, matrix: ProbabilityMatrix, verbose: bool = True) -> CheckResult:
    """水平性：同じ選好を申告した個人には同じ確率が割り当てられているか。"""
    violations: list[str] = []
    groups: dict[tuple[str, ...], list[int]] = {}
    for i in range(data.n_agents):
        groups.setdefault(tuple(data.acceptable_pref(i)), []).append(i)

    for members in groups.values():
        base = members[0]
        for other in members[1:]:
            if matrix.rows[base] != matrix.rows[other]:
                violations.append(
                    f"{data.name(base)} と {data.name(other)} は同じ選好だが確率が異なる"
                )

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【水平性】{result}")
    return result


def check_envy_free(data: Input, matrix: ProbabilityMatrix, verbose: bool = True) -> CheckResult:
    """無羨望性（sd基準）：各個人の割り当てが他人の割り当てを弱確率支配するか。

    ここでの定義は sd-無羨望性（Bogomolnaia–Moulin 2001）：自分の行が相手の行を
    弱確率支配しなければ「羨望あり」とみなす。支配関係が付かない（効用の取り方に
    よっては羨む）ケースも羨望に含む点で，extended_assignment_check の
    「正当な羨望なし」（相手の行が自分を厳密に支配する場合のみ羨望）より強い基準。
    """
    cols = matrix.columns
    violations: list[str] = []

    for i in range(data.n_agents):
        ranking_i = _full_ranking(data, i)
        for j in range(data.n_agents):
            if i == j:
                continue
            # i が自分の割り当て P_i で他人 P_j を弱確率支配しないなら，i は j を羨む
            if not _weakly_sd_dominates(matrix.rows[i], matrix.rows[j], cols, ranking_i):
                violations.append(f"{data.name(i)} は {data.name(j)} の割り当てを羨む（確率支配されない）")

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【無羨望性（sd基準）】{result}")
    return result


def check_ordinal_efficiency(data: Input, matrix: ProbabilityMatrix, verbose: bool = True) -> CheckResult:
    """順序効率性：非浪費性 と 関係 τ_P（消費している財より好きな財への矢印）の非巡回性で判定。

    τ_P の非巡回性だけでは「余っている財があるのに，それより好みの劣る対象を
    正の確率で消費している」浪費（waste）を検出できないため，先に非浪費性を確認する。
    """
    cols = matrix.columns
    col_index = {c: k for k, c in enumerate(cols)}

    # 各個人の財に対する順位（小さいほど好き）
    rank = []
    for i in range(data.n_agents):
        r = {obj: pos for pos, obj in enumerate(_full_ranking(data, i))}
        rank.append(r)

    violations: list[str] = []

    # (1) 非浪費性：財 a に余剰供給があるのに，a より下位の対象 b を正の確率で
    #     消費している個人 i がいれば，i の確率を b から a へ移すだけで改善できる＝浪費
    for a in data.goods:
        used = sum((matrix.rows[i][col_index[a]] for i in range(data.n_agents)), Fraction(0))
        if used >= data.capacities[a]:
            continue  # 余剰供給なし
        for i in range(data.n_agents):
            for b in cols:
                if matrix.rows[i][col_index[b]] > 0 and rank[i][a] < rank[i][b]:
                    violations.append(
                        f"浪費: {a} に余剰供給があるのに {data.name(i)} は下位の {b} を正の確率で消費"
                    )
                    break  # この個人については1つ見つければ十分

    # (2) 有向グラフ：a→b ⟺ ある個人 i が a を正の確率で消費し，かつ b≻_i a
    adj: dict[str, set[str]] = {c: set() for c in cols}
    for i in range(data.n_agents):
        row = matrix.rows[i]
        for a in cols:
            if row[col_index[a]] > 0:
                for b in cols:
                    if rank[i][b] < rank[i][a]:  # b の方が a より好き
                        adj[a].add(b)

    cycle = _find_cycle(adj, cols)
    if cycle is not None:
        path = " → ".join(cycle)
        violations.append(
            f"確率支配する改善サイクルが存在: {path}（このサイクル上で確率を交換すれば全員得する）"
        )

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【順序効率性】{result}")
    return result


def check_strategy_proof(
    data: Input,
    mechanism: Mechanism,
    verbose: bool = True,
) -> CheckResult:
    """耐戦略性：どの個人も虚偽申告で正直申告の割り当てを上回れないか（メカニズム単位）。

    各個人について O∪{∅} の全順序を虚偽申告として試し，正直申告の割り当てが
    その虚偽申告の割り当てを弱確率支配しない（＝得する効用が存在する）ケースを探す。
    """
    cols = data.columns()
    truthful = mechanism(data, verbose=False)
    violations: list[str] = []

    all_reports = list(permutations(cols))  # O∪{∅} の全順序

    for i in range(data.n_agents):
        ranking_i = _full_ranking(data, i)  # 真の選好で評価する
        true_row = truthful.rows[i]
        true_acceptable = data.acceptable_pref(i)

        for report in all_reports:
            report_list = list(report)
            # 申告として真の選好と同じ振る舞いになるものはスキップ
            if _acceptable_of(report_list) == true_acceptable:
                continue
            misdata = replace(data, prefs=[*data.prefs[:i], report_list, *data.prefs[i + 1:]])
            mis_row = mechanism(misdata, verbose=False).rows[i]
            # 正直申告が虚偽申告を弱確率支配しない → 得する効用が存在する＝操作可能
            if not _weakly_sd_dominates(true_row, mis_row, cols, ranking_i):
                violations.append(
                    f"{data.name(i)} は虚偽申告 [{', '.join(report_list)}] で得できる可能性がある"
                )
                break  # この個人については1つ見つければ十分

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【耐戦略性】{result}")
    return result


# ─────────────────────────────────────────────
# 一括チェックと比較
# ─────────────────────────────────────────────

def check_all(
    data: Input,
    matrix: ProbabilityMatrix,
    mechanism: Mechanism | None = None,
    verbose: bool = True,
) -> dict[str, CheckResult]:
    """確率行列（および任意でメカニズム）の性質を一括検証する。"""
    results = {
        "equal_treatment": check_equal_treatment(data, matrix, verbose),
        "envy_free": check_envy_free(data, matrix, verbose),
        "ordinal_efficiency": check_ordinal_efficiency(data, matrix, verbose),
    }
    if mechanism is not None:
        results["strategy_proof"] = check_strategy_proof(data, mechanism, verbose)
    return results


def compare_mechanisms(
    data: Input,
    mechanisms: list[tuple[str, Mechanism]],
    verbose: bool = True,
) -> dict[str, dict[str, CheckResult]]:
    """複数メカニズム（RP / PS など）を同一入力で実行し，性質を表で比較する。"""
    if verbose:
        from rp_algorithm import print_input
        print_input(data)

    matrices: dict[str, ProbabilityMatrix] = {}
    all_results: dict[str, dict[str, CheckResult]] = {}

    for name, func in mechanisms:
        matrix = func(data, verbose=False)
        matrices[name] = matrix
        all_results[name] = check_all(data, matrix, mechanism=func, verbose=False)

    if verbose:
        for name, matrix in matrices.items():
            print(f"=== {name} が定める確率行列 ===")
            print(matrix)
            print()
        _print_comparison_table(mechanisms, all_results)

    return all_results


# ─────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────

def _acceptable_of(report: list[str]) -> list[str]:
    """申告 report を ∅ までで切り出す（acceptable_pref と同じ規則）。"""
    cut: list[str] = []
    for item in report:
        cut.append(item)
        if item == EMPTY:
            return cut
    cut.append(EMPTY)
    return cut


def _find_cycle(adj: dict[str, set[str]], nodes: list[str]) -> list[str] | None:
    """有向グラフに巡回があれば，その閉路（ノード列）を1つ返す。なければ None。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    stack: list[str] = []

    def dfs(u: str) -> list[str] | None:
        color[u] = GRAY
        stack.append(u)
        for v in adj[u]:
            if color[v] == GRAY:  # 後退辺 → 閉路発見
                idx = stack.index(v)
                return stack[idx:] + [v]
            if color[v] == WHITE:
                found = dfs(v)
                if found is not None:
                    return found
        stack.pop()
        color[u] = BLACK
        return None

    for n in nodes:
        if color[n] == WHITE:
            found = dfs(n)
            if found is not None:
                return found
    return None


_PROPERTY_LABELS = [
    ("strategy_proof", "耐戦略性"),
    ("equal_treatment", "水平性"),
    ("envy_free", "無羨望性"),
    ("ordinal_efficiency", "順序効率性"),
]


def _print_comparison_table(
    mechanisms: list[tuple[str, Mechanism]],
    all_results: dict[str, dict[str, CheckResult]],
) -> None:
    names = [name for name, _ in mechanisms]
    print("=== 性質の比較表 ===\n")
    header = f"{'性質':<12}" + "".join(f"{name:^8}" for name in names)
    print(header)
    print("-" * len(header))
    for key, label in _PROPERTY_LABELS:
        cells = ""
        for name in names:
            res = all_results[name].get(key)
            mark = "—" if res is None else ("○" if res.passed else "×")
            cells += f"{mark:^8}"
        print(f"{label:<12}{cells}")
    print()
    print("（○=満たす / ×=満たさない / —=未検証）")
    print()
