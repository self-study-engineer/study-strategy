"""
拡張 Probabilistic Serial (PS) Mechanism — 制約付き同時確率消費メカニズム

注意（実装可能性）:
  本メカニズムが返すのは，制約を「期待値の意味で」満たす期待行列である。これを
  「制約を満たす確定的割り当ての上のくじ」として実装（分解）できることが保証される
  のは，行制約（各人1つ）・列制約（供給数）・追加の上限制約からなる制約構造が
  bihierarchy（2つの階層族の和）をなす場合である
  （Budish, Che, Kojima and Milgrom 2013, American Economic Review 103, 定理1）。
  ペア禁止制約と属性上限制約が同一の財の上で交差する場合（実行例4）などは
  bihierarchy にならず，分解可能性は保証されない。なお拡張RPは構成上つねに
  「実行可能な確定的割り当ての上のくじ」なので，この問題は生じない。
"""

from __future__ import annotations
import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction

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
    """制約充足チェックの結果"""

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

def extended_probabilistic_serial(
    data: ConstrainedInput,
    *,
    verbose: bool = True,
) -> ProbabilityMatrix:
    """拡張PSメカニズムが定める期待行列を返す。

    ps_algorithm.probabilistic_serial を上限制約付きに拡張したもの。各局面で
    「獲得可能（供給に空きがあり上限制約に余地がある）」な財だけを食べる点が異なる。

    - data:
        制約付き割り当て問題の入力（選好・供給数・上限制約）。
    - verbose:
        True のとき選好・結果を表示する。
    """
    columns = data.columns()
    col_index = {c: k for k, c in enumerate(columns)}
    n = data.n_agents

    if verbose:
        print_input(data)
        print("=== 拡張PSメカニズム ===\n")

    # 残量（∅ は無制限なので None で表す）
    remaining: dict[str, Fraction | None] = {g: Fraction(q) for g, q in data.capacities.items()}
    remaining[EMPTY] = None

    # 【確率計算】各局面で全員が同時に「獲得可能な残存財の最善」を食べ，食べた量（時間）を積み上げる
    rows = [[Fraction(0) for _ in columns] for _ in range(n)]
    t, end = Fraction(0), Fraction(1)
    while t < end:
        alloc = [EMPTY] * n
        for agent in range(n):                     # 各人がいま食べる「獲得可能な」残存財の最善を選ぶ
            for item in data.acceptable_pref(agent):
                if item == EMPTY:
                    break
                amt = remaining.get(item)          # 供給に無い財は None → 無視（RP版の .get と同挙動）
                if amt is not None and amt > 0 and _within_constraints(data, agent, item, rows, col_index):
                    alloc[agent] = item
                    break
        # 次にどれかの財が尽きる / 上限制約が飽和するまでの時間 Δt（上限は t=1 までの残り）
        dt = end - t
        for good in set(alloc):
            amt = remaining[good]
            if amt is not None:
                dt = min(dt, amt / alloc.count(good))
        for S in data.constraints:                 # 上限制約の飽和もイベントに含める【拡張で追加】
            rate = sum(1 for i, good in enumerate(alloc) if (i, good) in S.pairs)
            if rate > 0:
                cur = sum((rows[i][col_index[a]] for (i, a) in S.pairs), Fraction(0))
                dt = min(dt, (Fraction(S.upper) - cur) / rate)
        for i, good in enumerate(alloc):
            rows[i][col_index[good]] += dt
        for good in set(alloc):                    # 食べた分だけ残量を減らす（∅ は減らない）
            amt = remaining[good]
            if amt is not None:
                remaining[good] = amt - alloc.count(good) * dt
        t += dt

    matrix = ProbabilityMatrix(columns=columns, rows=rows, agent_label=data.agent_label)
    if verbose:
        print_result(data, matrix, "拡張PSメカニズムの期待行列")
    return matrix


def _within_constraints(
    data: ConstrainedInput,
    agent: int,
    item: str,
    rows: list[list[Fraction]],
    col_index: dict[str, int],
) -> bool:
    """(agent, item) を含む全ての上限制約にまだ余地があるか（獲得可能性の制約部分）。"""
    for S in data.constraints:
        if (agent, item) in S.pairs:
            cur = sum((rows[i][col_index[a]] for (i, a) in S.pairs), Fraction(0))
            if cur >= S.upper:
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
