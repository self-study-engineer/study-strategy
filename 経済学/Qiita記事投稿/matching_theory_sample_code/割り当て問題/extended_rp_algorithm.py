"""
拡張 Random Priority (RP) Mechanism — 制約付き均等確率優先順位メカニズム
"""

from __future__ import annotations
import random
import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import permutations

# 「どの財も受け取らない」ことを表す特別な財 ∅（供給数は無制限）
EMPTY = "∅"


# ─────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class Constraint:
    """上限制約集合 S：ペア (個人 i, 財 a) の集合とその和の上限 q̄_S。【拡張で追加】"""

    pairs: frozenset[tuple[int, str]]
    upper: int
    label: str = ""


@dataclass
class ConstrainedInput:
    """確率的割り当て問題の入力（基本版 Input に上限制約と名前を追加）。

    - constraints: 追加の上限制約のリスト（財の供給数は capacities で別途扱う）。
    - agent_names: 表示用の名前（省略時は agent_label + 番号）。
    """

    prefs: list[list[str]]
    capacities: dict[str, int]
    constraints: list[Constraint] = field(default_factory=list)
    agent_names: list[str] | None = None
    agent_label: str = "個人"
    object_label: str = "財"
    goods: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.goods:
            self.goods = list(self.capacities.keys())

    @property
    def n_agents(self) -> int:
        return len(self.prefs)

    def columns(self) -> list[str]:
        """確率行列の列順（財 → 最後に ∅）。"""
        return [*self.goods, EMPTY]

    def acceptable_pref(self, agent: int) -> list[str]:
        """個人 agent の選好を ∅ までで切り出し，末尾に ∅ を保証して返す。"""
        cut: list[str] = []
        for item in self.prefs[agent]:
            cut.append(item)
            if item == EMPTY:
                return cut
        cut.append(EMPTY)
        return cut

    def name(self, agent: int) -> str:
        """個人 agent の表示名（agent_names があればそれ，なければ agent_label + 番号）。"""
        if self.agent_names:
            return self.agent_names[agent]
        return f"{self.agent_label}{agent + 1}"


@dataclass
class ProbabilityMatrix:
    """期待行列（各成分は Fraction）。行＝個人，列＝財（末尾が ∅）。"""

    columns: list[str]
    rows: list[list[Fraction]]
    agent_label: str = "個人"


@dataclass
class CheckResult:
    """制約充足チェックの結果。【拡張で追加】"""

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
# メインアルゴリズム
# ─────────────────────────────────────────────

def extended_random_priority(
    data: ConstrainedInput,
    *,
    n_samples: int | None = None,
    seed: int | None = None,
    verbose: bool = True,
) -> ProbabilityMatrix:
    """拡張RPメカニズムが定める期待行列を返す。

    rp_algorithm.random_priority を上限制約付きに拡張したもの。各人は優先順位順に
    「供給に空きがあり，かつ上限制約を破らない」財だけを取る点が異なる。

    - data:
        制約付き割り当て問題の入力（選好・供給数・上限制約）。
    - n_samples:
        None なら全 n! 通りの優先順位を列挙して厳密値を計算。
        整数ならその回数だけ優先順位を無作為抽出してモンテカルロ近似する。
    - seed:
        モンテカルロ近似時の乱数シード。
    - verbose:
        True のとき選好・結果を表示する。
    """
    columns = data.columns()
    col_index = {c: k for k, c in enumerate(columns)}
    n = data.n_agents

    if verbose:
        print_input(data)
        print("=== 拡張RPメカニズム ===\n")

    # 優先順位の並び（全 n! 通り or 無作為抽出）を用意する
    if n_samples is None:
        orders = permutations(range(n))
    else:
        rng = random.Random(seed)
        orders = (tuple(rng.sample(range(n), n)) for _ in range(n_samples))

    # 【確率計算】各優先順位で「制約を満たす範囲で」逐次独裁制を行い，平均する
    counts = [[Fraction(0) for _ in columns] for _ in range(n)]
    total = 0
    for order in orders:
        remaining = dict(data.capacities)          # 残りの供給数（整数）
        csum = [0] * len(data.constraints)         # 各上限制約の現在の整数和【拡張で追加】
        alloc = [EMPTY] * n
        for agent in order:                        # 優先順位の高い人から確定的に取る
            for item in data.acceptable_pref(agent):
                if item == EMPTY:
                    break
                if remaining.get(item, 0) > 0 and _feasible(data, agent, item, csum):
                    alloc[agent] = item
                    remaining[item] -= 1
                    for idx, S in enumerate(data.constraints):   # 制約の整数和を更新【拡張で追加】
                        if (agent, item) in S.pairs:
                            csum[idx] += 1
                    break
        for i, good in enumerate(alloc):
            counts[i][col_index[good]] += 1
        total += 1
    rows = [[count / total for count in row] for row in counts]

    matrix = ProbabilityMatrix(columns=columns, rows=rows, agent_label=data.agent_label)
    if verbose:
        print_result(data, matrix, "拡張RPメカニズムの期待行列")
    return matrix


def _feasible(data: ConstrainedInput, agent: int, item: str, csum: list[int]) -> bool:
    """(agent, item) を含む全ての上限制約をまだ破らないか。"""
    for idx, S in enumerate(data.constraints):
        if (agent, item) in S.pairs and csum[idx] >= S.upper:
            return False
    return True


# ─────────────────────────────────────────────
# 制約ビルダー（会社の案件割り当て向け）
# ─────────────────────────────────────────────

def forbid_pair(agent_i: int, agent_j: int, goods: list[str], names: tuple[str, str] | None = None) -> list[Constraint]:
    """社員 i, j を同じ案件に入れない制約を，各案件について1つずつ作る。"""
    who = f"{names[0]}と{names[1]}" if names else f"社員{agent_i + 1}と社員{agent_j + 1}"
    return [
        Constraint(pairs=frozenset({(agent_i, a), (agent_j, a)}), upper=1, label=f"{who}を案件{a}で同席させない")
        for a in goods
    ]


def at_most_juniors(juniors: list[int], good: str, cap: int, *, label: str | None = None) -> Constraint:
    """案件 good に入れる若手（juniors）の人数を cap 人までに制限する制約。

    cap = 案件の供給数 − 1 とすれば「若手だけで埋めない（非若手を最低1人確保）」になる。
    """
    return Constraint(
        pairs=frozenset((i, good) for i in juniors),
        upper=cap,
        label=label or f"案件{good}の若手は最大{cap}人（若手だけで埋めない）",
    )


# ─────────────────────────────────────────────
# ユーティリティ（制約充足チェック・表示）
# ─────────────────────────────────────────────

def frac_str(x: Fraction) -> str:
    """Fraction を読みやすい文字列にする（0 や整数はそのまま）。"""
    if x == 0:
        return "0"
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def check_constraints(data: ConstrainedInput, matrix: ProbabilityMatrix, verbose: bool = True) -> CheckResult:
    """期待行列がすべての制約（供給数・1人1案件・追加の上限制約）を満たすか検証する。"""
    col_index = {c: k for k, c in enumerate(matrix.columns)}
    n = data.n_agents
    violations: list[str] = []

    for a in data.goods:
        total = sum((matrix.rows[i][col_index[a]] for i in range(n)), Fraction(0))
        if total > data.capacities[a]:
            violations.append(f"案件{a} の割当期待値 {frac_str(total)} が供給数 {data.capacities[a]} を超過")

    for i in range(n):
        total = sum((matrix.rows[i][col_index[a]] for a in data.goods), Fraction(0))
        if total > 1:
            violations.append(f"{data.name(i)} の実案件割当合計 {frac_str(total)} が 1 を超過")

    for S in data.constraints:
        total = sum((matrix.rows[i][col_index[a]] for (i, a) in S.pairs), Fraction(0))
        if total > S.upper:
            violations.append(f"制約「{S.label}」違反: 和 {frac_str(total)} > 上限 {S.upper}")

    result = CheckResult(passed=not violations, violations=violations)
    if verbose:
        print(f"【制約充足】{result}")
    return result


def print_input(data: ConstrainedInput) -> None:
    print(f"【{data.agent_label}の選好（左ほど希望が高い）】")
    for i in range(data.n_agents):
        print(f"  {data.name(i)}: {', '.join(data.prefs[i])}")
    print()
    print(f"【{data.object_label}の供給数（必要人数）】")
    print("  " + ", ".join(f"{a}: {q}人" for a, q in data.capacities.items()))
    if data.constraints:
        print()
        print("【追加の制約】")
        for S in data.constraints:
            print(f"  - {S.label}")
    print()


def _disp_width(s: str) -> int:
    """文字列の表示幅（全角文字=2, 半角文字=1）。コンソールでの桁揃えに使う。"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _pad_label(s: str, width: int) -> str:
    """s を表示幅 width まで右側にスペースを足して左揃えにする。"""
    return s + " " * (width - _disp_width(s))


def print_result(data: ConstrainedInput, matrix: ProbabilityMatrix, title: str, *, as_float: bool = False) -> None:
    col_index = {c: k for k, c in enumerate(matrix.columns)}
    n = data.n_agents
    # 行ラベル（各社員名 + 「期待人数」）を表示幅でそろえる
    labels = [data.name(i) for i in range(n)] + ["期待人数"]
    label_w = max(_disp_width(s) for s in labels)
    fmt = (lambda x: f"{float(x):.3f}") if as_float else frac_str   # as_float=True で小数表示

    print(f"=== {title} ===")
    header = " " * (label_w + 2) + "  ".join(f"{c:>6}" for c in matrix.columns)
    print(header)
    for i in range(n):
        cells = "  ".join(f"{fmt(matrix.rows[i][col_index[c]]):>6}" for c in matrix.columns)
        print(f"{_pad_label(data.name(i), label_w)}  {cells}")
    print("  " + "-" * (len(header) - 2))
    sums = [fmt(sum((matrix.rows[i][col_index[c]] for i in range(n)), Fraction(0))) for c in matrix.columns]
    print(f"{_pad_label('期待人数', label_w)}  " + "  ".join(f"{s:>6}" for s in sums))
    print()
