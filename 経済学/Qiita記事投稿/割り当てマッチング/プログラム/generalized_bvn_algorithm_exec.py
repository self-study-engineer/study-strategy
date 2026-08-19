"""
一般化 BvN 定理の実行例
  Budish, Che, Kojima and Milgrom (2013) "Designing Random Allocation Mechanisms:
  Theory and Applications," American Economic Review, 103(2), pp.585-623 の
  図・例をそのまま再現する。

実行:
    python3 generalized_bvn_algorithm_exec.py
"""

from __future__ import annotations

from fractions import Fraction

from generalized_bvn_algorithm import (
    ConstraintSet,
    ConstraintStructure,
    Term,
    column,
    find_bihierarchy,
    find_odd_cycle,
    frac_str,
    generalized_bvn,
    is_hierarchy,
    print_decomposition,
    print_matrix,
    row,
    subcolumn,
    upper_contour_constraints,
    verify,
)

F = Fraction


def header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def report(X, structure, *, check_bihierarchy=True, max_terms=12):
    """分解して表示・検証まで行う共通処理。"""
    split = find_bihierarchy(structure)
    if split is None:
        print("  → bihierarchy ではない")
        odd = find_odd_cycle(structure)
        if odd:
            print("  → 奇サイクルを検出（補題1: 普遍的実装可能でない）")
            for s in odd:
                print(f"      {s.label()} = {sorted(s.cells)}")
    else:
        h1, h2 = split
        print(f"  → bihierarchy（H1: {len(h1)}集合 / H2: {len(h2)}集合）")
        assert is_hierarchy(h1) and is_hierarchy(h2)

    try:
        terms = generalized_bvn(X, structure, check_bihierarchy=check_bihierarchy)
    except (ValueError, RuntimeError) as e:
        print(f"  → 分解できません: {e}")
        return None

    print_decomposition(terms, max_terms=max_terms)
    problems = verify(terms, X, structure)
    print("  検証: " + ("すべて OK（再構成一致・全項が制約を満たす）" if not problems
                        else "\n        ".join(problems)))
    return terms


# ─────────────────────────────────────────────
# 例1: 1対1割当 = BvN 定理（系1）
# ─────────────────────────────────────────────

def example_one_to_one() -> None:
    header("例1: 1対1割当 —— BvN 定理は bihierarchy の特殊ケース（系1）")
    print("""
n人にn個の対象を1つずつ。行の和＝1、列の和＝1。
行同士は互いに素 → 階層 H1。列同士も互いに素 → 階層 H2。
よって H1∪H2 は bihierarchy であり、定理1から
「任意の二重確率行列は置換行列の凸結合」（＝BvN定理）が従う。
""".strip())

    n = 3
    X = [
        [F(1, 2), F(1, 3), F(1, 6)],
        [F(1, 3), F(1, 3), F(1, 3)],
        [F(1, 6), F(1, 3), F(1, 2)],
    ]
    print("\n【期待割当 X（二重確率行列）】")
    print_matrix(X)

    structure = ConstraintStructure(
        n, n,
        [row(i, n, 1, 1) for i in range(n)] + [column(a, n, 1, 1) for a in range(n)],
    ).with_singletons(0, 1)

    print()
    report(X, structure)


# ─────────────────────────────────────────────
# 例2: 多対1割当（論文 Figure 1 の設定）
# ─────────────────────────────────────────────

def example_many_to_one() -> None:
    header("例2: 多対1割当 —— 学校選択（論文 Figure 1 / Section I）")
    print("""
学生 4人 (i0..i3) × 学校 3校 (o0,o1,o2)。
  ・各学生はちょうど1校に配属        → 行制約（下限=上限=1）
  ・o0 の定員は2、o1・o2 の定員は1  → 列制約
  ・o0 は {i0,i1} からちょうど1人取る → 部分列制約（アファーマティブ・アクション型）

ここが「1対1」との決定的な違い:
  ・列の上限が1でなくなる（多対1）
  ・列の"部分"にも制約が付く（グループ別クォータ）
どちらも列側の階層 H2 の中に、互いに素または入れ子の関係で収まる。
→ bihierarchy のままなので、定理1により期待割当は必ず実装可能。
""".strip())

    n, m = 4, 3
    X = [
        [F(1, 2), F(1, 5), F(3, 10)],
        [F(1, 2), F(1, 2), F(0)],
        [F(4, 5), F(0), F(1, 5)],
        [F(1, 5), F(3, 10), F(1, 2)],
    ]
    print("\n【期待割当 X（論文 p.591 の例）】")
    print_matrix(X)

    structure = ConstraintStructure(
        n, m,
        [row(i, m, 1, 1) for i in range(n)]
        + [column(0, n, 0, 2), column(1, n, 0, 1), column(2, n, 0, 1)]
        + [subcolumn(0, [0, 1], 1, 1, name="部分列 o0×{i0,i1}")],
    ).with_singletons(0, 1)

    print()
    report(X, structure)


# ─────────────────────────────────────────────
# 例3: 一般化 PS の出力を実装する（論文 Example 2）
# ─────────────────────────────────────────────

def example_generalized_ps() -> None:
    header("例3: 一般化 PS メカニズムの期待割当を実装する（論文 Example 2）")
    print("""
学生 4人 × 学校 {a, b, ∅}。a は定員2、b は定員1、∅ は無制限。
さらに a には {1,2,3} 向けの部分列クォータ 1。
選好: 学生1,2 は a ≻ b ≻ ∅、学生3,4 は b ≻ a ≻ ∅。

一般化PSのイーティング:
  t=0   学生1,2 が a を、学生3,4 が b を食べ始める
  t=1/2 部分列 S={(1,a),(2,a),(3,a)} の上限1 と b の定員1 が同時に拘束
  t>1/2 学生4 だけが a を食べられる（4 は S に属さないため）、他は ∅

得られる期待割当は下記。定理1（系2）より必ず実装可能。
一方 RP（ランダム逐次独裁）の帰結は制約付きの意味でも順序効率的でない（論文 p.602）。
""".strip())

    # 対象の並び: [a, b, ∅]
    n, m = 4, 3
    X = [
        [F(1, 2), F(0), F(1, 2)],
        [F(1, 2), F(0), F(1, 2)],
        [F(0), F(1, 2), F(1, 2)],
        [F(1, 2), F(1, 2), F(0)],
    ]
    print("\n【一般化PSの期待割当 PS(≻)】（列は a, b, ∅ の順）")
    print_matrix(X)

    structure = ConstraintStructure(
        n, m,
        [row(i, m, 1, 1) for i in range(n)]
        + [column(0, n, 0, 2, name="列 a(定員2)"), column(1, n, 0, 1, name="列 b(定員1)")]
        + [subcolumn(0, [0, 1, 2], 0, 1, name="部分列 a×{1,2,3}")],
        # ∅ 列は上限なし（列制約を課さない）
    ).with_singletons(0, 1)

    print()
    report(X, structure)


# ─────────────────────────────────────────────
# 例4: bihierarchy でない場合（論文 Example 1・補題1）
# ─────────────────────────────────────────────

def example_odd_cycle() -> None:
    header("例4: bihierarchy でない制約構造 —— 実装不可能（論文 Example 1）")
    print("""
2人 × 2対象。制約は
  第1行 {(0,0),(0,1)}、第1列 {(0,0),(1,0)}、対角集合 {(0,1),(1,0)}
のいずれも下限=上限=1。3つはどの2つも交差するので、同じ階層に入れられない
（bihierarchy でない）。しかも長さ3の奇サイクルを成す。

X = [[1/2, 1/2], [1/2, 1/2]] はクォータを期待値では満たすが実装不可能:
  x̲(0,0)=1 となる純割当が正の確率で選ばれねばならない
  → 行の上限1より x̲(0,1)=0 → 対角集合の下限1より x̲(1,0)=1
  → 第1列の和が 2 となり上限1に違反。矛盾。
""".strip())

    n, m = 2, 2
    X = [[F(1, 2), F(1, 2)], [F(1, 2), F(1, 2)]]
    print("\n【期待割当 X】")
    print_matrix(X)

    structure = ConstraintStructure(
        n, m,
        [
            ConstraintSet(frozenset({(0, 0), (0, 1)}), 1, 1, name="第1行"),
            ConstraintSet(frozenset({(0, 0), (1, 0)}), 1, 1, name="第1列"),
            ConstraintSet(frozenset({(0, 1), (1, 0)}), 1, 1, name="対角集合"),
        ],
    ).with_singletons(0, 1)

    print()
    report(X, structure)


# ─────────────────────────────────────────────
# 例5: 効用保証（論文 Theorem 9 / Figure 3）
# ─────────────────────────────────────────────

def example_utility_guarantee() -> None:
    header("例5: 効用保証 —— ex post の不公平を抑える（論文 Theorem 9 / Figure 3）")
    print("""
2人が4つの対象 a≻b≻c≻d を2つずつ分ける。全セル 0.5 の期待割当は ex ante 公平。
しかし素朴な実装だと「一方が a,b、他方が c,d」という ex post に不公平なくじになりうる。

定理9の方法: 各人の「上位k個」に人工制約 ⌊·⌋ ≤ Σ ≤ ⌈·⌉ を追加する。
  上位1個 {a}    : 0.5 → 0 以上 1 以下
  上位2個 {a,b}  : 1.0 → ちょうど 1（← これが効く）
  上位3個 {a,b,c}: 1.5 → 1 以上 2 以下
同一行内の入れ子集合なので行の階層 H1 に収まり、bihierarchy は保たれる。
結果、どの純割当でも各人は必ず {a,b} からちょうど1つを得る。
""".strip())

    n, m = 2, 4
    X = [[F(1, 2)] * 4, [F(1, 2)] * 4]
    print("\n【期待割当 X】（列は a, b, c, d）")
    print_matrix(X)

    base_sets = [row(i, m, 2, 2) for i in range(n)] + [column(a, n, 1, 1) for a in range(m)]
    naive = ConstraintStructure(n, m, base_sets).with_singletons(0, 1)
    values = [4, 3, 2, 1]

    def utility_range(terms) -> tuple[int, int]:
        us = [sum(t.assignment[0][a] * values[a] for a in range(m)) for t in terms]
        return min(us), max(us)

    print("\n─── (1) 人工制約なしでも「実装可能」な、ex post に不公平なくじ ───")
    print("""
確率1/2で 個人0←{a,b}, 個人1←{c,d} ／ 確率1/2で 個人0←{c,d}, 個人1←{a,b}。
これは行・列制約をすべて満たす正当な実装。つまり定理1は「実装できる」ことしか
保証せず、どの実装が選ばれるかは制御していない。""".strip())
    unfair = [
        Term(F(1, 2), [[1, 1, 0, 0], [0, 0, 1, 1]]),
        Term(F(1, 2), [[0, 0, 1, 1], [1, 1, 0, 0]]),
    ]
    print()
    print_decomposition(unfair, max_terms=2)
    problems = verify(unfair, X, naive)
    print("  基本制約の検証: " + ("OK（確かに実装として正当）" if not problems else str(problems)))
    lo, hi = utility_range(unfair)
    print(f"  個人0の実現効用 = {lo} または {hi} → 幅 {hi - lo}（最大単位効用差 3 を超える）")

    print("\n─── (2) 上位k個の人工制約を追加（定理9）───")
    pref = [0, 1, 2, 3]
    artificial = (
        upper_contour_constraints(X, 0, pref) + upper_contour_constraints(X, 1, pref)
    )
    for cs in artificial:
        print(f"    {cs.label()}: [{cs.floor}, {cs.ceil}]  cells={sorted(cs.cells)}")
    guarded = ConstraintStructure(n, m, base_sets + artificial).with_singletons(0, 1)

    print("\n  上の不公平なくじは、この人工制約のもとでは弾かれる:")
    for v in verify(unfair, X, guarded):
        print(f"    {v}")

    print()
    terms_guarded = report(X, guarded, max_terms=6)
    if terms_guarded:
        lo, hi = utility_range(terms_guarded)
        print(f"\n  定理9の人工制約あり: 個人0の実現効用は {lo}〜{hi}（幅 {hi - lo}）")
        print("  最大単位効用差 = v(a) − v(d) = 4 − 1 = 3 → 定理9の保証（幅 ≤ 3）を満たす。")


# ─────────────────────────────────────────────
# 例6: インターリーグ対戦カード（論文 Figure 4）
# ─────────────────────────────────────────────

def example_interleague() -> None:
    header("例6: 両側マッチング —— インターリーグ対戦カード（論文 Figure 4 / Theorem 10）")
    print("""
2リーグ各4チーム。各チームは他リーグと計6試合。
「全チームと均等に」なら 6/4 = 1.5 試合ずつだが、これは整数でない。
行・列制約（各チーム6試合）に加えて、両側に「上位k個（強い順）」の人工制約を入れると、
対戦相手の強さの合計のばらつきを抑えた整数の対戦表が得られる。
""".strip())

    n = 4
    X = [[F(3, 2)] * n for _ in range(n)]
    print("\n【期待対戦回数 X】")
    print_matrix(X)

    sets = [row(i, n, 6, 6) for i in range(n)] + [column(a, n, 6, 6) for a in range(n)]
    # 両側に上位k個制約（チームは index 順に強いとする）
    pref = list(range(n))
    for i in range(n):
        sets += upper_contour_constraints(X, i, pref, name_prefix="N側")
    Xt = [[X[i][a] for i in range(n)] for a in range(n)]
    for a in range(n):
        for cs in upper_contour_constraints(Xt, a, pref, name_prefix="O側"):
            sets.append(
                ConstraintSet(
                    frozenset((i, a) for (_, i) in cs.cells), cs.floor, cs.ceil, cs.name
                )
            )

    structure = ConstraintStructure(n, n, sets).with_singletons(0, 3)
    print()
    terms = report(X, structure, max_terms=4)
    if terms:
        print("\n  最頻の純割当（Figure 4 Panel B に対応する形）:")
        print_matrix(terms[0].assignment, indent="    ")
        print(f"    λ = {frac_str(terms[0].weight)}")


# ─────────────────────────────────────────────
# 例7: 3部マッチングの不可能性（論文 Theorem 12）
# ─────────────────────────────────────────────

def example_three_sided() -> None:
    header("例7: 3部マッチングには一般化 BvN が存在しない（論文 Theorem 12）")
    print("""
学生 / 学校 / 放課後プログラム のように3つの側があると、割当は三つ組 (i,a,l) になる。
正準3部制約構造は S_i = {i}×O×L、S_a = N×{a}×L、S_l = N×O×{l} を必ず含む。
|N|,|O|,|L| ≥ 2 なら、i'≠i, a'≠a, l'≠l を取ると

    (i, a, l') ∈ S_i ∩ S_a \\ S_l
    (i, a', l) ∈ S_i ∩ S_l \\ S_a
    (i', a, l) ∈ S_a ∩ S_l \\ S_i

となり (S_i, S_a, S_l) は長さ3の奇サイクル。補題1より普遍的実装可能でない。
同じ論法で、ルームメイト問題（3人以上）も不可能（定理13）。
→ 「BvN 的アプローチが使えるのは本質的に二部構造まで」というのが論文の結論のひとつ。
""".strip())

    # 三つ組を 2次元に潰して表現: 行 = i, 列 = (a,l)
    N, O, L = 2, 2, 2
    n_rows, n_cols = N, O * L
    idx = lambda a, l: a * L + l  # noqa: E731

    S_i = [ConstraintSet(frozenset((i, idx(a, l)) for a in range(O) for l in range(L)),
                         1, 1, name=f"S_i{i}") for i in range(N)]
    S_a = [ConstraintSet(frozenset((i, idx(a, l)) for i in range(N) for l in range(L)),
                         1, 1, name=f"S_a{a}") for a in range(O)]
    S_l = [ConstraintSet(frozenset((i, idx(a, l)) for i in range(N) for a in range(O)),
                         1, 1, name=f"S_l{l}") for l in range(L)]

    structure = ConstraintStructure(n_rows, n_cols, S_i + S_a + S_l).with_singletons(0, 1)
    odd = find_odd_cycle(structure)
    print(f"\n  bihierarchy か: {find_bihierarchy(structure) is not None}")
    if odd:
        print("  奇サイクル検出 → 普遍的実装可能でない:")
        for s in odd:
            print(f"    {s.label()}")


if __name__ == "__main__":
    example_one_to_one()
    example_many_to_one()
    example_generalized_ps()
    example_odd_cycle()
    example_utility_guarantee()
    example_interleague()
    example_three_sided()
    print()
