"""
Random Priority (RP) Mechanism — 均等確率優先順位メカニズム
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

def random_priority(
    data: Input,
    *,
    n_samples: int | None = None,
    seed: int | None = None,
    verbose: bool = True,
) -> ProbabilityMatrix:
    """RPメカニズムが定める確率行列を返す。

    - data:
        割り当て問題の入力（各個人の選好と各財の供給数）。
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
        print("=== RPメカニズム ===\n")

    # 優先順位の並び（全 n! 通り or 無作為抽出）を用意する
    if n_samples is None:
        orders = permutations(range(n))
    else:
        rng = random.Random(seed)
        orders = (tuple(rng.sample(range(n), n)) for _ in range(n_samples))

    # 【確率計算】各優先順位で逐次独裁制（高優先の人から残存財の最善を取る）を行い，平均する
    counts = [[Fraction(0) for _ in columns] for _ in range(n)]
    total = 0
    for order in orders:
        remaining = dict(data.capacities)          # 残りの供給数（整数）
        alloc = [EMPTY] * n
        for agent in order:                        # 優先順位の高い人から確定的に取る
            for item in data.acceptable_pref(agent):
                if item == EMPTY:
                    break
                if remaining.get(item, 0) > 0:
                    alloc[agent] = item
                    remaining[item] -= 1
                    break
        for i, good in enumerate(alloc):
            counts[i][col_index[good]] += 1
        total += 1
    rows = [[count / total for count in row] for row in counts]

    matrix = ProbabilityMatrix(columns=columns, rows=rows, agent_label=data.agent_label, agent_names=data.agent_names)
    if verbose:
        print_result(data, matrix, "RPメカニズムの確率行列")
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
