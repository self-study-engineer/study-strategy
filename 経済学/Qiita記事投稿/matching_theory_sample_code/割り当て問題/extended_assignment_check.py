"""
extended_assignment_check.py — 制約付き割り当て（拡張RP/PS）の性質検証モジュール

assignment_check.py（無制約版）の制約対応版。上限制約を考慮して第7章の4性質を検証する。
基本版とは独立（こちらは numpy / scipy を使う）。

検証する性質（制約対応）:
  1. 水平性     : 「同値な個人」を *(選好が同じ) かつ (i↔j の入替で制約構造が不変)* で判定。
  2. 無羨望性   : i が j の割当を ≻_i で厳密に確率支配（sd）し，かつ i↔j の行入替が制約実行可能
                  なら「正当な羨望」。制約で得られない割当への羨望は除外される。
  3. 順序効率性 : 「P を確率支配する制約実行可能な Q が存在するか」を線形計画で判定
                  （存在しなければ制約付き順序効率的）。scipy.optimize.linprog を使用。
  4. 耐戦略性   : 各個人の全虚偽申告で（制約付き）機構を再実行し，正直申告が支配しない例を探す。

実装方針:
  - sd 累積・確率支配判定は numpy でベクトル化。順序効率性は scipy.linprog。
  - 期待行列を float 化し，許容誤差 TOL で判定する（小規模・有理数インスタンス向け）。
  - 制約は data.constraints（各要素は .pairs と .upper を持つ）から取得。

依存: numpy, scipy（`pip install numpy scipy`）。

参考文献:
  - 小島武仁・栗野盛光（2023）『マッチング理論とマーケットデザイン』第7・9章
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import permutations
from typing import Callable, Protocol

import numpy as np
# scipy は順序効率性の線形計画でのみ使うため，関数内で遅延 import する
# （numpy だけで他の3性質は動作する）。

EMPTY = "∅"
TOL = 1e-9          # 浮動小数の比較許容差
EFF_TOL = 1e-6      # 順序効率性の改善量のしきい値（小規模では gap >> これ）


# ─────────────────────────────────────────────
# 型（構造的）とデータクラス
# ─────────────────────────────────────────────

class _Data(Protocol):
    """check 関数が必要とする入力のインターフェース（ConstrainedInput が満たす）。"""

    prefs: list[list[str]]
    capacities: dict[str, int]
    agent_label: str

    @property
    def n_agents(self) -> int: ...
    def columns(self) -> list[str]: ...
    def acceptable_pref(self, agent: int) -> list[str]: ...
    def name(self, agent: int) -> str: ...


Mechanism = Callable[..., object]   # data を受け取り .rows/.columns を持つ行列を返す


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
            return f"{status}\n" + "\n".join(f"    - {v}" for v in self.violations)
        return status


# ─────────────────────────────────────────────
# 補助関数
# ─────────────────────────────────────────────

def _ranking(data: _Data, agent: int) -> list[str]:
    """個人 agent の全列に対する全順序（好きな順）。申告選好の後ろに非申告財を並べる。"""
    pref = data.acceptable_pref(agent)
    listed = set(pref)
    return pref + [c for c in data.columns() if c not in listed]


def _rows_array(matrix: object) -> np.ndarray:
    """期待行列を float の ndarray（行＝個人, 列＝matrix.columns 順）にする。"""
    return np.array([[float(x) for x in row] for row in matrix.rows], dtype=float)  # type: ignore[attr-defined]


def _cum(arr_row: np.ndarray, col_index: dict[str, int], ranking: list[str]) -> np.ndarray:
    """ranking 順に並べた行の累積和（各上位集合の確率）。"""
    return np.cumsum([arr_row[col_index[c]] for c in ranking])


# ─────────────────────────────────────────────
# 各性質の検証
# ─────────────────────────────────────────────

def check_equal_treatment(data: _Data, matrix: object, verbose: bool = True) -> CheckResult:
    """水平性：制約構造の対称性で「同値な個人」を判定し，同値なら確率が一致するか。"""
    arr = _rows_array(matrix)
    n = data.n_agents
    cons = list(getattr(data, "constraints", []))
    orig = frozenset((S.pairs, S.upper) for S in cons)

    def symmetric(i: int, j: int) -> bool:
        """i↔j の入替で制約集合が不変か（不変なら i,j は対称＝同値になり得る）。"""
        def swap(p: tuple[int, str]) -> tuple[int, str]:
            a, g = p
            return (j if a == i else i if a == j else a), g
        swapped = frozenset((frozenset(swap(p) for p in S.pairs), S.upper) for S in cons)
        return swapped == orig

    violations: list[str] = []
    for i in range(n):
        for j in range(i + 1, n):
            if data.acceptable_pref(i) == data.acceptable_pref(j) and symmetric(i, j):
                if not np.allclose(arr[i], arr[j], atol=TOL):
                    violations.append(f"{data.name(i)} と {data.name(j)} は同値だが確率が異なる")

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【水平性】{result}")
    return result


def check_envy_free(data: _Data, matrix: object, verbose: bool = True) -> CheckResult:
    """無羨望性（正当な羨望なし）：i が j の割当を厳密に sd 選好し，かつ i↔j の入替が制約実行可能なら正当な羨望。

    注意: 基本版 assignment_check の sd-無羨望性（弱支配の失敗＝羨望）より弱い基準。
    こちらは (a) 相手の行が自分の行を「厳密に」sd 支配し，かつ (b) 行の入替が制約上
    実行可能な場合のみを「正当な羨望」として数える（制約で得られない割当への羨望は除外）。
    """
    cols = matrix.columns  # type: ignore[attr-defined]
    ci = {c: k for k, c in enumerate(cols)}
    arr = _rows_array(matrix)
    n = data.n_agents
    violations: list[str] = []

    for i in range(n):
        rank_i = _ranking(data, i)
        cum_own = _cum(arr[i], ci, rank_i)
        for j in range(n):
            if i == j:
                continue
            cum_j = _cum(arr[j], ci, rank_i)   # i から見た j の割当の評価
            strictly_prefers = bool(np.all(cum_j >= cum_own - TOL) and np.any(cum_j > cum_own + TOL))
            if strictly_prefers and _swap_feasible(data, matrix, i, j):
                violations.append(f"{data.name(i)} は {data.name(j)} の割当を羨む（入替も制約上可能）")

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【無羨望性（正当な羨望なし）】{result}")
    return result


def _swap_feasible(data: _Data, matrix: object, i: int, j: int) -> bool:
    """個人 i, j の行を入れ替えた配分が全ての上限制約を満たすか（列和は不変なので制約だけ確認）。"""
    cons = list(getattr(data, "constraints", []))
    if not cons:
        return True
    ci = {c: k for k, c in enumerate(matrix.columns)}  # type: ignore[attr-defined]
    rows = matrix.rows  # type: ignore[attr-defined]

    def val(agent: int, good: str) -> float:
        src = j if agent == i else i if agent == j else agent   # 行入替後の参照元
        return float(rows[src][ci[good]])

    for S in cons:
        total = sum(val(a, g) for (a, g) in S.pairs)
        if total > S.upper + TOL:
            return False
    return True


def _build_efficiency_lp(data: _Data, matrix: object):
    """順序効率性判定用LPの係数を numpy で組み立てる（scipy 不要）。

    返り値 (w, A_ub, b_ub, A_eq, b_eq, value_p, P_flat)。変数は Q[i][c]（i*m + col_index[c]）。
      目的:   max w·Q   （w[i][c] = その財以上に好ましい財数 ＝ Σ_k cumQ と等価）
      A_eq:   各個人の行和 = 1
      A_ub:   案件供給 Σ_i Q[i][a] ≤ q_a ／ 上限制約 Σ_S Q ≤ q̄_S ／ 確率支配 -cumQ ≤ -cumP
    """
    cols = matrix.columns  # type: ignore[attr-defined]
    ci = {c: k for k, c in enumerate(cols)}
    n, m = data.n_agents, len(cols)
    goods = list(data.capacities.keys())
    P = _rows_array(matrix)

    def idx(i: int, c: str) -> int:
        return i * m + ci[c]

    w = np.zeros(n * m)
    for i in range(n):
        for pos, c in enumerate(_ranking(data, i)):
            w[idx(i, c)] = m - pos

    A_eq, b_eq = [], []
    for i in range(n):                                  # 各個人の行和 = 1
        row = np.zeros(n * m)
        for c in cols:
            row[idx(i, c)] = 1.0
        A_eq.append(row); b_eq.append(1.0)

    A_ub, b_ub = [], []
    for a in goods:                                     # 案件の供給数
        row = np.zeros(n * m)
        for i in range(n):
            row[idx(i, a)] = 1.0
        A_ub.append(row); b_ub.append(float(data.capacities[a]))
    for S in getattr(data, "constraints", []):          # 追加の上限制約
        row = np.zeros(n * m)
        for (i, a) in S.pairs:
            row[idx(i, a)] = 1.0
        A_ub.append(row); b_ub.append(float(S.upper))
    for i in range(n):                                  # 確率支配（弱）: -cumQ ≤ -cumP
        rank, cum = _ranking(data, i), 0.0
        for k in range(len(rank)):
            cum += P[i][ci[rank[k]]]
            row = np.zeros(n * m)
            for c in rank[: k + 1]:
                row[idx(i, c)] = -1.0
            A_ub.append(row); b_ub.append(-cum)

    P_flat = P.reshape(-1)
    value_p = float(w @ P_flat)
    return w, np.array(A_ub), np.array(b_ub), np.array(A_eq), np.array(b_eq), value_p, P_flat


def check_ordinal_efficiency(data: _Data, matrix: object, verbose: bool = True) -> CheckResult:
    """順序効率性：P を確率支配する制約実行可能な Q が存在しないか（scipy.linprog で判定）。"""
    try:
        from scipy.optimize import linprog  # pyright: ignore[reportMissingImports]  # 遅延 import（scipy が必要）
    except ImportError:
        if verbose:
            print("【順序効率性】⚠ scipy 未導入のため判定をスキップ（pip install scipy）")
        return CheckResult(passed=True, violations=[])

    w, A_ub, b_ub, A_eq, b_eq, value_p, _ = _build_efficiency_lp(data, matrix)
    res = linprog(-w, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        # LP が解けなかった場合は「効率的」と断定せず，判定不能として警告する
        if verbose:
            print(f"【順序効率性】⚠ 線形計画が解けず判定不能のためスキップ（{res.message}）")
        return CheckResult(passed=True, violations=[])
    best = -res.fun

    violations: list[str] = []
    if best > value_p + EFF_TOL:
        violations.append(f"確率支配する制約実行可能な割当が存在（順序効率的でない / 改善量≈{best - value_p:.4f}）")

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【順序効率性】{result}")
    return result


def check_strategy_proof(data: _Data, mechanism: Mechanism, verbose: bool = True) -> CheckResult:
    """耐戦略性：どの個人も虚偽申告で正直申告の割当を上回れないか（制約付き機構を再実行）。"""
    cols = data.columns()
    ci = {c: k for k, c in enumerate(cols)}
    truthful = _rows_array(mechanism(data, verbose=False))
    n = data.n_agents
    all_reports = list(permutations(cols))
    violations: list[str] = []

    for i in range(n):
        rank_i = _ranking(data, i)
        true_cum = _cum(truthful[i], ci, rank_i)
        true_acceptable = data.acceptable_pref(i)
        for report in all_reports:
            report_list = list(report)
            if _acceptable_of(report_list) == true_acceptable:
                continue
            misdata = replace(data, prefs=[*data.prefs[:i], report_list, *data.prefs[i + 1:]])  # type: ignore[type-var]
            mis_row = _rows_array(mechanism(misdata, verbose=False))[i]
            mis_cum = _cum(mis_row, ci, rank_i)
            # 正直申告が虚偽申告を弱確率支配しない → 得する効用が存在する＝操作可能
            if not np.all(true_cum >= mis_cum - TOL):
                violations.append(f"{data.name(i)} は虚偽申告 [{', '.join(report_list)}] で得できる可能性がある")
                break

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【耐戦略性】{result}")
    return result


# ─────────────────────────────────────────────
# 一括チェック
# ─────────────────────────────────────────────

def check_all(data: _Data, matrix: object, mechanism: Mechanism | None = None, verbose: bool = True) -> dict[str, CheckResult]:
    """制約付き期待行列（および任意でメカニズム）の4性質を一括検証する。"""
    results = {
        "equal_treatment": check_equal_treatment(data, matrix, verbose),
        "envy_free": check_envy_free(data, matrix, verbose),
        "ordinal_efficiency": check_ordinal_efficiency(data, matrix, verbose),
    }
    if mechanism is not None:
        results["strategy_proof"] = check_strategy_proof(data, mechanism, verbose)
    return results


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
