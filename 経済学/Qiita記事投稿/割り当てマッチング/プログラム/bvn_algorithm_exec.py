"""
バーコフ＝フォン・ノイマン分解の実行例（『マッチング理論とマーケットデザイン』第9章）。

    python bvn_algorithm_exec.py
"""
# rp_algorithm の Input を ps_algorithm.probabilistic_serial に渡すため，Pyright が
# 名目的な型不一致を出すが，実行時はダックタイピングで問題ない。誤検知のみ抑制する。
# pyright: reportArgumentType=false

from rp_algorithm import EMPTY, Input
from ps_algorithm import probabilistic_serial
from bvn_algorithm import BvNTerm, birkhoff_von_neumann, reconstruct, frac_str, _print_matrix


def example_textbook() -> None:
    """例: 二重確率行列を置換行列の凸結合に分解する。"""
    print("=" * 56)
    print("例: 第9章の二重確率行列の分解")
    print("=" * 56)
    print()

    P = [
        ["1/6", "1/3", "1/2"],
        ["1/3", "2/3", "0"],
        ["1/2", "0", "1/2"],
    ]
    terms = birkhoff_von_neumann(P)
    _print_lottery_interpretation(terms)


def example_ps_to_bvn() -> None:
    """例: PSメカニズム → BvN分解の連携

    この例は個人数＝財数（3×3）・各財の供給数1・全員が全財を受け入れ可能なため，
    ∅ 列を除いた行列がちょうど二重確率行列になる特殊ケース。一般の PS 出力
    （∅ 消費や供給数2以上がある場合）をそのまま birkhoff_von_neumann に渡すことは
    できず，財の複製と ∅ ダミー列による正方化が必要になる（bvn_algorithm.py の
    「適用条件」参照）。
    """
    print("=" * 56)
    print("例: PSメカニズムの確率行列をBvN分解で実現する")
    print("=" * 56)
    print()

    data = Input(
        prefs=[
            ["a", "b", "c", EMPTY],
            ["a", "c", "b", EMPTY],
            ["b", "a", "c", EMPTY],
        ],
        capacities={"a": 1, "b": 1, "c": 1},
    )
    matrix = probabilistic_serial(data, verbose=False)

    n_goods = len(data.goods)
    sub = [row[:n_goods] for row in matrix.rows]

    print("PSが定める確率行列（∅ 列を除く，行＝個人 / 列＝a,b,c）:")
    _print_matrix(sub)
    print()

    terms = birkhoff_von_neumann(sub)
    rebuilt = reconstruct(terms, len(sub))
    print(f"分解の再構成が元の確率行列と一致: {rebuilt == sub}")
    print()
    _print_lottery_interpretation(terms)


def _print_lottery_interpretation(terms: list[BvNTerm]) -> None:
    print("【くじとしての解釈】")
    for term in terms:
        assign = ", ".join(
            f"個人{i + 1}→財{chr(ord('a') + j)}" for i, j in enumerate(term.perm)
        )
        print(f"  確率 {frac_str(term.weight)} で: {assign}")
    print()


if __name__ == "__main__":
    example_textbook()
    example_ps_to_bvn()
