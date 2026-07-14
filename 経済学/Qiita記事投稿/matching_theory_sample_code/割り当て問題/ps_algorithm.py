"""
Probabilistic Serial (PS) Mechanism — 同時確率消費メカニズム
"""

from __future__ import annotations
import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction

# 「どの財も受け取らない」ことを表す特別な財 ∅（供給数は無制限）
EMPTY = "∅"


# ─────────────────────────────────────────────
# データクラス（RP / PS 共通）
# ─────────────────────────────────────────────

@dataclass
class Input:
    """確率的割り当て問題の入力（RP / PS 共通の形式）"""

    prefs: list[list[str]]
    capacities: dict[str, int]
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
    """確率行列（各成分は Fraction）。行＝個人，列＝財（末尾が ∅）。"""

    columns: list[str]
    rows: list[list[Fraction]]
    agent_label: str = "個人"
    agent_names: list[str] | None = None

    def row_of(self, agent: int) -> list[Fraction]:
        return self.rows[agent]

    def name(self, agent: int) -> str:
        if self.agent_names:
            return self.agent_names[agent]
        return f"{self.agent_label}{agent + 1}"

    def __str__(self) -> str:
        name_w = max((len(self.name(i)) for i in range(len(self.rows))), default=4)
        header = " " * (name_w + 2) + "  ".join(f"{c:>6}" for c in self.columns)
        lines = [header]
        for i, row in enumerate(self.rows):
            cells = "  ".join(f"{frac_str(p):>6}" for p in row)
            lines.append(f"{self.name(i):<{name_w}}  {cells}")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# メインアルゴリズム
# ─────────────────────────────────────────────

def probabilistic_serial(
    data: Input,
    *,
    verbose: bool = True,
) -> ProbabilityMatrix:
    """PSメカニズムが定める確率行列を返す。

    - data:
        割り当て問題の入力（各個人の選好と各財の供給数）。
    - verbose:
        True のとき選好・結果を表示する。
    """
    columns = data.columns()
    col_index = {c: k for k, c in enumerate(columns)}
    n = data.n_agents

    if verbose:
        print_input(data)
        print("=== PSメカニズム ===\n")

    # 残量（∅ は無制限なので None で表す）
    remaining: dict[str, Fraction | None] = {g: Fraction(q) for g, q in data.capacities.items()}
    remaining[EMPTY] = None

    # 【確率計算】各局面で全員が同時に残存財の最善を食べ，食べた量（時間）を積み上げる
    rows = [[Fraction(0) for _ in columns] for _ in range(n)]
    t, end = Fraction(0), Fraction(1)
    while t < end:
        alloc = [EMPTY] * n
        for agent in range(n):                     # 各人がいま食べる残存財の最善を選ぶ
            for item in data.acceptable_pref(agent):
                if item == EMPTY:
                    break
                amt = remaining.get(item)          # 供給に無い財は None → 無視（RP版の .get と同挙動）
                if amt is not None and amt > 0:
                    alloc[agent] = item
                    break
        # 次にどれかの財が食べ尽くされるまでの時間 Δt（上限は t=1 までの残り）
        dt = end - t
        for good in set(alloc):
            amt = remaining[good]
            if amt is not None:
                dt = min(dt, amt / alloc.count(good))
        for i, good in enumerate(alloc):
            rows[i][col_index[good]] += dt
        for good in set(alloc):                    # 食べた分だけ残量を減らす（∅ は減らない）
            amt = remaining[good]
            if amt is not None:
                remaining[good] = amt - alloc.count(good) * dt
        t += dt

    matrix = ProbabilityMatrix(columns=columns, rows=rows, agent_label=data.agent_label, agent_names=data.agent_names)
    if verbose:
        print_result(data, matrix, "PSメカニズムの確率行列")
    return matrix


# ─────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────

def frac_str(x: Fraction) -> str:
    """Fraction を読みやすい文字列にする（0 や整数はそのまま）。"""
    if x == 0:
        return "0"
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def print_input(data: Input) -> None:
    print(f"【{data.agent_label}の選好（左ほど好き）】")
    for i, pref in enumerate(data.prefs):
        print(f"  {data.name(i)}: {', '.join(pref)}")
    print()
    print("【財の供給数】")
    print("  " + ", ".join(f"{g}: {q}" for g, q in data.capacities.items()))
    print()


def _disp_width(s: str) -> int:
    """文字列の表示幅（全角文字=2, 半角文字=1）。コンソールでの桁揃えに使う。"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _pad_label(s: str, width: int) -> str:
    """s を表示幅 width まで右側にスペースを足して左揃えにする。"""
    return s + " " * (width - _disp_width(s))


def print_result(data: Input, matrix: ProbabilityMatrix, title: str, *, as_float: bool = False) -> None:
    col_index = {c: k for k, c in enumerate(matrix.columns)}
    n = data.n_agents
    # 行ラベル（各個人名 + 「期待人数」）を表示幅でそろえる
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
