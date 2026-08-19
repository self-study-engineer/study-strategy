"""
一般化 Birkhoff–von Neumann 定理（Budish, Che, Kojima and Milgrom 2013, AER 103(2)）
  制約構造つきの期待割当行列 → 制約を満たす「純割当」上のくじ への分解

────────────────────────────────────────────────────────────
理論の要約
────────────────────────────────────────────────────────────
【設定】個人集合 N と対象集合 O。純割当 X̲ = [x̲_ia] は整数行列（x̲_ia は個人 i が
対象 a を受け取る個数）。制約集合 S ⊆ N×O ごとに下限 q_S と上限 q̄_S（整数）を与え、

    q_S ≤ Σ_{(i,a)∈S} x̲_ia ≤ q̄_S        （すべての S ∈ H）

を満たすとき X̲ は実行可能。H を制約構造と呼び、すべての単集合 {(i,a)} を含むと仮定する。

【期待割当】X = [x_ia]（実数行列）。同じ不等式を満たすとき「X は q を満たす」という。

【実装可能性 (implementability)】X が、q を満たす純割当の凸結合として書けること。

【階層 (hierarchy / laminar family)】H の任意の2元 S, S' について
    S ⊆ S'  または  S' ⊆ S  または  S ∩ S' = ∅
【二重階層 (bihierarchy)】H = H1 ∪ H2（H1 ∩ H2 = ∅）で H1, H2 がともに階層。

【定理1（十分性）】H が bihierarchy なら、H は「普遍的実装可能」である。すなわち
  任意の整数クォータ q に対し、q を満たす任意の期待割当が実装可能。
  証明の骨子: ポリトープ {X' : ⌊x_S⌋ ≤ Σ_S x'_ia ≤ ⌈x_S⌉, ∀S∈H} の接合行列（incidence
  matrix）が bihierarchy のとき完全単模（totally unimodular, Edmonds 1970）であり、
  Hoffman–Kruskal (1956) よりこのポリトープの頂点はすべて整数点。X はその凸結合。

【定理2（必要性）】「正準二部制約構造」（すべての行 {i}×O とすべての列 N×{a} を含む）
  が bihierarchy でないなら、普遍的実装可能でない。
  → 二部（片側割当・両側マッチング）の世界では bihierarchy は必要十分。

【補題1（奇サイクル）】H が「奇サイクル」を含むなら普遍的実装可能でない。
  奇サイクルとは、奇数個の制約集合 (S_1,…,S_l) と対 (s_1,…,s_l) の列で
      s_i ∈ S_i ∩ S_{i+1}（添字は巡回）かつ s_i ∉ S_j （j ≠ i, i+1）
  を満たすもの。定理12（3部マッチング）・定理13（ルームメイト問題）の不可能性は
  すべてこの補題から出る。

────────────────────────────────────────────────────────────
本モジュールが提供するもの
────────────────────────────────────────────────────────────
  * ConstraintSet / ConstraintStructure : 制約構造のデータ構造
  * is_hierarchy / find_bihierarchy     : 階層判定・二重階層への分割（交差グラフの2彩色）
  * find_odd_cycle                      : 長さ3の奇サイクル探索（実装不可能性の証拠）
  * satisfies_quotas                    : 期待割当がクォータを満たすかの検査
  * generalized_bvn                     : 期待割当 → 純割当の凸結合（Fraction で厳密計算）
  * upper_contour_constraints           : 定理9（効用保証）の人工制約を生成

分解アルゴリズム（定理1の構成的証明・online Appendix B の考え方）:
  1. 整数になっているセルは固定し、分数セルだけを動かす方向 d を探す。
     このとき「S ごとの和 x_S がすでに整数である制約」は和を変えない（Σ_{S} d = 0）。
  2. そのような d ≠ 0 が存在しなければ X はポリトープの頂点。TU 性よりこの頂点は
     整数点、つまり X はすでに純割当。
  3. d ≠ 0 なら X+αd と X−βd が実行可能となる最大の α, β>0 を取り、
     γ = β/(α+β) として X = γ(X+αd) + (1−γ)(X−βd)。
     α（β）の定め方から、少なくとも1つの制約集合の和が新たに整数になる。
     整数だった制約集合は整数のまま。よって有限回で純割当に到達する。
  4. 両枝を再帰的に分解し、重みを掛け合わせて併合する。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations

Cell = tuple[int, int]           # (個人 index, 対象 index)
Matrix = list[list[Fraction]]


# ─────────────────────────────────────────────
# 制約構造
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class ConstraintSet:
    """制約集合 S とそのクォータ (q_S, q̄_S)。

    cells: S に含まれる (個人, 対象) の組。
    floor / ceil: 下限・上限（整数）。ceil=None は上限なし。
    name: 表示用ラベル。
    """

    cells: frozenset[Cell]
    floor: int = 0
    ceil: int | None = None
    name: str = ""

    def total(self, X: Matrix) -> Fraction:
        return sum((X[i][a] for (i, a) in self.cells), Fraction(0))

    def label(self) -> str:
        return self.name or f"S{sorted(self.cells)}"


@dataclass
class ConstraintStructure:
    """制約構造 H。単集合制約は自動で補われる。"""

    n_agents: int
    n_objects: int
    sets: list[ConstraintSet] = field(default_factory=list)

    def with_singletons(self, floor: int = 0, ceil: int | None = 1) -> "ConstraintStructure":
        """すべての単集合 {(i,a)} を（未登録なら）追加した新しい構造を返す。"""
        existing = {cs.cells for cs in self.sets}
        extra = [
            ConstraintSet(frozenset({(i, a)}), floor, ceil, name=f"単集合({i},{a})")
            for i in range(self.n_agents)
            for a in range(self.n_objects)
            if frozenset({(i, a)}) not in existing
        ]
        return ConstraintStructure(self.n_agents, self.n_objects, self.sets + extra)


# ── 制約集合を作るヘルパ ──────────────────────

def row(i: int, n_objects: int, floor: int, ceil: int | None, name: str = "") -> ConstraintSet:
    """行制約 {i}×O（個人 i の合計）。"""
    return ConstraintSet(
        frozenset((i, a) for a in range(n_objects)), floor, ceil, name or f"行{i}"
    )


def column(a: int, n_agents: int, floor: int, ceil: int | None, name: str = "") -> ConstraintSet:
    """列制約 N×{a}（対象 a の合計）。"""
    return ConstraintSet(
        frozenset((i, a) for i in range(n_agents)), floor, ceil, name or f"列{a}"
    )


def subcolumn(
    a: int, agents: list[int], floor: int, ceil: int | None, name: str = ""
) -> ConstraintSet:
    """部分列制約 N'×{a}（対象 a のうち特定グループの合計）。グループ別クォータに対応。"""
    return ConstraintSet(
        frozenset((i, a) for i in agents), floor, ceil, name or f"部分列{a}{agents}"
    )


def subrow(
    i: int, objects: list[int], floor: int, ceil: int | None, name: str = ""
) -> ConstraintSet:
    """部分行制約 {i}×O'（個人 i の特定科目群の合計）。時間割・カリキュラム制約に対応。"""
    return ConstraintSet(
        frozenset((i, a) for a in objects), floor, ceil, name or f"部分行{i}{objects}"
    )


# ─────────────────────────────────────────────
# 階層・二重階層の判定
# ─────────────────────────────────────────────

def crosses(s: frozenset[Cell], t: frozenset[Cell]) -> bool:
    """S と T が「交差する」（共通部分を持つがどちらも他方を含まない）か。"""
    if s.isdisjoint(t):
        return False
    return not (s <= t or t <= s)


def is_hierarchy(sets: list[ConstraintSet]) -> bool:
    """階層（laminar family）かどうか。"""
    return not any(crosses(s.cells, t.cells) for s, t in combinations(sets, 2))


def find_bihierarchy(
    structure: ConstraintStructure,
) -> tuple[list[ConstraintSet], list[ConstraintSet]] | None:
    """H を2つの階層 H1, H2 に分割する。不可能なら None。

    「交差グラフ」（頂点＝制約集合、辺＝交差する組）を2彩色できることと
    bihierarchy であることは同値。したがって2部グラフ判定（BFS）に帰着する。
    """
    sets = structure.sets
    m = len(sets)
    adjacency: list[list[int]] = [[] for _ in range(m)]
    for u, v in combinations(range(m), 2):
        if crosses(sets[u].cells, sets[v].cells):
            adjacency[u].append(v)
            adjacency[v].append(u)

    color = [-1] * m
    for start in range(m):
        if color[start] != -1:
            continue
        color[start] = 0
        queue = [start]
        while queue:
            u = queue.pop()
            for v in adjacency[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return None  # 奇数長の閉路 → 2彩色不能
    return (
        [s for s, c in zip(sets, color) if c == 0],
        [s for s, c in zip(sets, color) if c == 1],
    )


def find_odd_cycle(structure: ConstraintStructure) -> list[ConstraintSet] | None:
    """長さ3の奇サイクル（定義4）を1つ探す。見つかれば普遍的実装可能でない（補題1）。

    3つ組 (S1,S2,S3) が、S1∩S2\\S3, S2∩S3\\S1, S1∩S3\\S2 のいずれも非空なら奇サイクル。
    注: 長さ5以上の奇サイクルは探索しないので、None は「奇サイクルなし」を意味しない。
    """
    for s1, s2, s3 in combinations(structure.sets, 3):
        a, b, c = s1.cells, s2.cells, s3.cells
        if (a & b) - c and (b & c) - a and (a & c) - b:
            return [s1, s2, s3]
    return None


# ─────────────────────────────────────────────
# クォータ検査
# ─────────────────────────────────────────────

def satisfies_quotas(X: Matrix, structure: ConstraintStructure) -> list[str]:
    """X が違反している制約のラベル一覧を返す（空なら適合）。"""
    violations = []
    for cs in structure.sets:
        total = cs.total(X)
        if total < cs.floor or (cs.ceil is not None and total > cs.ceil):
            violations.append(f"{cs.label()}: 和={frac_str(total)} ∉ [{cs.floor}, {cs.ceil}]")
    return violations


# ─────────────────────────────────────────────
# 一般化 BvN 分解
# ─────────────────────────────────────────────

@dataclass
class Term:
    """分解の1項：重み λ と純割当（整数行列）。"""

    weight: Fraction
    assignment: list[list[int]]


def generalized_bvn(
    matrix: list[list],
    structure: ConstraintStructure,
    *,
    check_bihierarchy: bool = True,
    verbose: bool = False,
) -> list[Term]:
    """期待割当 X を、制約を満たす純割当の凸結合に分解する。

    matrix: 期待割当（int / float / Fraction / "1/3" 形式の文字列を成分に取れる）。
    structure: 制約構造（単集合制約を含めておくこと。with_singletons() が便利）。
    check_bihierarchy: True なら bihierarchy でない場合に例外を投げる。
                       （bihierarchy は十分条件であって必要条件ではないので、
                         False にすれば試行はできる。分解不能なら実行時に例外。）
    返り値: Term のリスト（weight の総和は 1）。
    """
    X: Matrix = [[Fraction(str(x)) if isinstance(x, float) else Fraction(x) for x in r]
                 for r in matrix]
    n, m = len(X), len(X[0])
    if (n, m) != (structure.n_agents, structure.n_objects):
        raise ValueError("行列の形と制約構造の (n_agents, n_objects) が一致しません。")

    violations = satisfies_quotas(X, structure)
    if violations:
        raise ValueError("期待割当がクォータを満たしていません:\n  " + "\n  ".join(violations))

    if check_bihierarchy:
        split = find_bihierarchy(structure)
        if split is None:
            odd = find_odd_cycle(structure)
            msg = "制約構造が bihierarchy ではありません（定理1の十分条件を満たさない）。"
            if odd:
                msg += "\n  奇サイクルを検出（補題1より普遍的実装可能でない）: " + ", ".join(
                    s.label() for s in odd
                )
            raise ValueError(msg)
        if verbose:
            h1, h2 = split
            print(f"bihierarchy に分割: H1={len(h1)}個, H2={len(h2)}個")

    terms: list[Term] = []
    _decompose(X, structure, Fraction(1), terms, verbose)
    return _merge(terms)


def _decompose(
    X: Matrix,
    structure: ConstraintStructure,
    weight: Fraction,
    out: list[Term],
    verbose: bool,
) -> None:
    """X を再帰的に分解し、純割当と重みを out に積む。"""
    direction = _find_direction(X, structure)
    if direction is None:
        out.append(Term(weight, [[int(x) for x in r] for r in X]))
        if verbose:
            print(f"  純割当に到達（λ={frac_str(weight)}）")
        return

    alpha = _max_step(X, structure, direction, +1)
    beta = _max_step(X, structure, direction, -1)
    if alpha == 0 and beta == 0:
        raise RuntimeError("移動可能な方向が見つかりません（制約構造を確認してください）。")

    gamma = beta / (alpha + beta)
    x_plus = _shift(X, direction, alpha)
    x_minus = _shift(X, direction, -beta)

    _decompose(x_plus, structure, weight * gamma, out, verbose)
    _decompose(x_minus, structure, weight * (1 - gamma), out, verbose)


def _find_direction(X: Matrix, structure: ConstraintStructure) -> dict[Cell, Fraction] | None:
    """整数セルを固定し、整数和の制約を保つ移動方向 d ≠ 0 を1つ返す。無ければ None。"""
    free = [(i, a) for i in range(len(X)) for a in range(len(X[0]))
            if X[i][a].denominator != 1]
    if not free:
        return None
    index = {cell: k for k, cell in enumerate(free)}

    # 和がすでに整数の制約 → その和を変えない（等式制約）
    rows: list[list[Fraction]] = []
    for cs in structure.sets:
        if cs.total(X).denominator != 1:
            continue
        vec = [Fraction(0)] * len(free)
        touched = False
        for cell in cs.cells:
            if cell in index:
                vec[index[cell]] = Fraction(1)
                touched = True
        if touched:
            rows.append(vec)

    null = _null_space_vector(rows, len(free))
    if null is None:
        return None
    return {cell: null[k] for k, cell in enumerate(free) if null[k] != 0}


def _null_space_vector(rows: list[list[Fraction]], n_vars: int) -> list[Fraction] | None:
    """有理数の厳密ガウス消去で Ax=0 の非零解を1つ返す。自明解のみなら None。"""
    A = [r[:] for r in rows]
    pivot_of_col: dict[int, int] = {}
    r = 0
    for c in range(n_vars):
        piv = next((k for k in range(r, len(A)) if A[k][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = A[r][c]
        A[r] = [v / inv for v in A[r]]
        for k in range(len(A)):
            if k != r and A[k][c] != 0:
                f = A[k][c]
                A[k] = [v - f * w for v, w in zip(A[k], A[r])]
        pivot_of_col[c] = r
        r += 1
        if r == len(A):
            break

    freecols = [c for c in range(n_vars) if c not in pivot_of_col]
    if not freecols:
        return None
    target = freecols[0]
    vec = [Fraction(0)] * n_vars
    vec[target] = Fraction(1)
    for c, pr in pivot_of_col.items():
        vec[c] = -A[pr][target]
    return vec


def _max_step(
    X: Matrix, structure: ConstraintStructure, d: dict[Cell, Fraction], sign: int
) -> Fraction:
    """X + sign·t·d が ⌊x_S⌋ ≤ · ≤ ⌈x_S⌉ を保つ最大の t。"""
    best: Fraction | None = None
    for cs in structure.sets:
        delta = sum((d.get(cell, Fraction(0)) for cell in cs.cells), Fraction(0)) * sign
        if delta == 0:
            continue
        total = cs.total(X)
        if delta > 0:
            bound = (Fraction(math.ceil(total)) - total) / delta
        else:
            bound = (Fraction(math.floor(total)) - total) / delta
        best = bound if best is None else min(best, bound)
    return best if best is not None else Fraction(0)


def _shift(X: Matrix, d: dict[Cell, Fraction], t: Fraction) -> Matrix:
    Y = [r[:] for r in X]
    for (i, a), v in d.items():
        Y[i][a] += t * v
    return Y


def _merge(terms: list[Term]) -> list[Term]:
    """同一の純割当をまとめ、重みの大きい順に並べる。"""
    bucket: dict[tuple, Fraction] = {}
    for t in terms:
        key = tuple(tuple(r) for r in t.assignment)
        bucket[key] = bucket.get(key, Fraction(0)) + t.weight
    merged = [Term(w, [list(r) for r in k]) for k, w in bucket.items() if w != 0]
    merged.sort(key=lambda t: -t.weight)
    return merged


def reconstruct(terms: list[Term]) -> Matrix:
    """分解結果から期待割当を再構成する（検証用）。"""
    n = len(terms[0].assignment)
    m = len(terms[0].assignment[0])
    out = [[Fraction(0)] * m for _ in range(n)]
    for t in terms:
        for i in range(n):
            for a in range(m):
                out[i][a] += t.weight * t.assignment[i][a]
    return out


def verify(terms: list[Term], X: list[list], structure: ConstraintStructure) -> list[str]:
    """分解の妥当性を検査し、問題点のリストを返す（空なら正常）。"""
    problems: list[str] = []
    total = sum((t.weight for t in terms), Fraction(0))
    if total != 1:
        problems.append(f"重みの総和が1でない: {frac_str(total)}")

    target = [[Fraction(str(x)) if isinstance(x, float) else Fraction(x) for x in r] for r in X]
    back = reconstruct(terms)
    if back != target:
        problems.append("再構成した行列が元の期待割当と一致しない")

    for k, t in enumerate(terms, 1):
        pure: Matrix = [[Fraction(v) for v in r] for r in t.assignment]
        for v in satisfies_quotas(pure, structure):
            problems.append(f"第{k}項が制約違反 → {v}")
    return problems


# ─────────────────────────────────────────────
# 定理9（効用保証）用の人工制約
# ─────────────────────────────────────────────

def upper_contour_constraints(
    X: list[list], i: int, preference: list[int], name_prefix: str = ""
) -> list[ConstraintSet]:
    """個人 i の「上位 k 個」制約（定理9の人工制約）を生成する。

    preference: 個人 i の対象 index を好ましい順に並べたリスト。
    各 k について S_ik = {(i, 第1位), …, (i, 第k位)} を作り、
    下限 ⌊x_{S_ik}⌋・上限 ⌈x_{S_ik}⌉ を課す。これらは同一行内の入れ子集合なので
    行の階層 H1 に入れても階層性は壊れず、bihierarchy が保たれる（定理9の証明の要）。

    効果: どの純割当でも「上位 k 個からの取得数」が期待値の切り上げ・切り下げに収まり、
    実現効用のばらつきが最大単位効用差（最も価値の高い分数割当対象と最も低いそれの差）
    以内に抑えられる。
    """
    Xf = [[Fraction(str(v)) if isinstance(v, float) else Fraction(v) for v in r] for r in X]
    out = []
    for k in range(1, len(preference)):
        cells = frozenset((i, a) for a in preference[:k])
        total = sum((Xf[i][a] for a in preference[:k]), Fraction(0))
        out.append(
            ConstraintSet(
                cells,
                math.floor(total),
                math.ceil(total),
                name=f"{name_prefix}上位{k}({i})",
            )
        )
    return out


# ─────────────────────────────────────────────
# 表示ユーティリティ
# ─────────────────────────────────────────────

def frac_str(x: Fraction) -> str:
    if x == 0:
        return "0"
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def print_matrix(mat, indent: str = "  ") -> None:
    for r in mat:
        cells = [frac_str(Fraction(v)) if not isinstance(v, str) else v for v in r]
        print(indent + "[ " + "  ".join(f"{c:>5}" for c in cells) + " ]")


def print_decomposition(terms: list[Term], max_terms: int = 12) -> None:
    print(f"  分解された純割当の数: {len(terms)}")
    for k, t in enumerate(terms[:max_terms], 1):
        print(f"  【第{k}項】 λ = {frac_str(t.weight)}")
        print_matrix(t.assignment, indent="    ")
    if len(terms) > max_terms:
        print(f"  …（残り {len(terms) - max_terms} 項は省略）")
