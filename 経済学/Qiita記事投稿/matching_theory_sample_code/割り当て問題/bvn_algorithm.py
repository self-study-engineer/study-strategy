"""
Birkhoff–von Neumann（バーコフ＝フォン・ノイマン）の定理
  二重確率行列 → 置換行列の凸結合（＝確定的な割り当て上のくじ）への分解

定理（『マッチング理論とマーケットデザイン』第9章）:
  どんな二重確率行列（すべての成分が非負で，各行の和・各列の和がすべて 1 の
  正方行列）も，置換行列の凸結合で表現できる。

適用条件:
  本実装の入力は「正方の二重確率行列」に限る。PS の出力を分解できるのは，
  個人数＝財数・全財の供給数1・全員が全財を受け入れ可能（∅ 消費なし）で，
  ∅ 列を除いた部分行列がそのまま二重確率行列になる場合（bvn_algorithm_exec の
  連携例）。一般の PS 出力（∅ 消費や供給数2以上がある場合）には，財を供給数の
  分だけ複製し ∅ 用のダミー列を加えて正方化してから適用する必要がある。
  上限制約付きの期待行列の分解には一般化 BvN 定理（Budish, Che, Kojima and
  Milgrom 2013, 定理1: bihierarchy 制約構造）を参照。
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

Matrix = list[list[Fraction]]


# ─────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────

@dataclass
class BvNTerm:
    """分解の1項：重み λ と置換行列（行 i に対応する列を perm[i] で持つ）。"""

    weight: Fraction
    perm: list[int]  # perm[i] = 行 i で 1 が立つ列

    def as_matrix(self, n: int) -> Matrix:
        mat = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i, j in enumerate(self.perm):
            mat[i][j] = Fraction(1)
        return mat


# ─────────────────────────────────────────────
# メインアルゴリズム
# ─────────────────────────────────────────────

def birkhoff_von_neumann(matrix: list[list], *, verbose: bool = True) -> list[BvNTerm]:
    """二重確率行列を置換行列の凸結合に分解する。

    matrix: 二重確率行列（int / float / Fraction / 分数文字列 を成分に取れる）。
    verbose: True のとき分解の各項を表示する。
    返り値: BvNTerm のリスト（weight の総和は 1）。
    """
    P = [[Fraction(x) for x in row] for row in matrix]
    n = len(P)
    _validate_doubly_stochastic(P)

    residual = [row[:] for row in P]
    terms: list[BvNTerm] = []

    if verbose:
        print("=== バーコフ＝フォン・ノイマン分解 ===\n")
        print("【入力（二重確率行列 P）】")
        _print_matrix(P)
        print()

    while any(residual[i][j] != 0 for i in range(n) for j in range(n)):
        perm = _find_permutation_in_support(residual, n)
        if perm is None:  # 二重確率行列なら理論上ここには来ない
            raise RuntimeError("support に完全マッチングが見つかりません（入力を確認してください）")

        weight = min(residual[i][perm[i]] for i in range(n))
        for i in range(n):
            residual[i][perm[i]] -= weight
        terms.append(BvNTerm(weight=weight, perm=perm))

        if verbose:
            print(f"【第{len(terms)}項】 λ = {frac_str(weight)}")
            _print_matrix(BvNTerm(weight, perm).as_matrix(n))
            print()

    if verbose:
        total = sum((t.weight for t in terms), Fraction(0))
        print(f"分解された置換行列の数: {len(terms)}　/　重みの総和: {frac_str(total)}")
        print()

    return terms


def _find_permutation_in_support(residual: Matrix, n: int) -> list[int] | None:
    """残差行列の非零成分（support）の中で完全マッチング（置換）を1つ探す。

    行＝個人，列＝財の二部グラフで residual[i][j] > 0 の辺だけを使い，
    増加道法（augmenting path）で完全マッチングを構成する。
    """
    match_col = [-1] * n  # 列 j に割り当てられた行（-1 は未割当）
    result = [-1] * n     # result[i] = 行 i に割り当てられた列

    def try_assign(row: int, visited: list[bool]) -> bool:
        for col in range(n):
            if residual[row][col] > 0 and not visited[col]:
                visited[col] = True
                if match_col[col] == -1 or try_assign(match_col[col], visited):
                    match_col[col] = row
                    result[row] = col
                    return True
        return False

    for row in range(n):
        if not try_assign(row, [False] * n):
            return None
    return result


def reconstruct(terms: list[BvNTerm], n: int) -> Matrix:
    """分解結果から元の行列を再構成する（検証用）。"""
    out = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for term in terms:
        for i, j in enumerate(term.perm):
            out[i][j] += term.weight
    return out


# ─────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────

def _validate_doubly_stochastic(P: Matrix) -> None:
    n = len(P)
    if any(len(row) != n for row in P):
        raise ValueError("正方行列ではありません。")
    for i in range(n):
        row_sum = sum(P[i], Fraction(0))
        if row_sum != 1:
            raise ValueError(f"第{i + 1}行の和が1ではありません（和 = {frac_str(row_sum)}）。")
    for j in range(n):
        col_sum = sum((P[i][j] for i in range(n)), Fraction(0))
        if col_sum != 1:
            raise ValueError(f"第{j + 1}列の和が1ではありません（和 = {frac_str(col_sum)}）。")
    if any(P[i][j] < 0 for i in range(n) for j in range(n)):
        raise ValueError("負の成分があります。")


def frac_str(x: Fraction) -> str:
    if x == 0:
        return "0"
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def _print_matrix(mat: Matrix) -> None:
    for row in mat:
        print("  [ " + "  ".join(f"{frac_str(x):>4}" for x in row) + " ]")
