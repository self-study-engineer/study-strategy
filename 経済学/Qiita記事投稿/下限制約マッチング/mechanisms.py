"""
mechanisms.py — 下限制約マッチング: メカニズム実装

参考文献:
    Goto et al. (2016) "Strategyproof matching with regional minimum and maximum quotas"
    Artificial Intelligence 235, 40-57.

実装するメカニズム:
    - Mechanism 1: 一般化 DA (Generalized Deferred Acceptance)
    - Definition 11: PLDA-RQ の選択関数 Ch_C
    - Definition 12: RSDA-RQ の選択関数 Ch_C
    - ACDA: 人工キャップ DA（比較ベースライン）

性質の保証:
    - PLDA-RQ: strategyproof, fair, PL-nonwasteful, PL-fair (Theorems 5-9)
    - RSDA-RQ: strategyproof, fair, school-equitably-nonwasteful (Theorems 10-12)
"""

from __future__ import annotations
from model import Market, RegionTree, RegionNode
from feasibility import expected_min_count_all


# ─────────────────────────────────────────────────────────────────────────────
# 学生側の選択関数 Ch_S
# ─────────────────────────────────────────────────────────────────────────────

def ch_students(
    available: frozenset[tuple[int, int]],
    market: Market,
) -> frozenset[tuple[int, int]]:
    """
    各学生が利用可能なコントラクトの中から最善の学校を選ぶ。

    Ch_S(X') = ∪_s Ch_s(X')
    Ch_s(X') = {(s, c)} where c is s's most preferred school in X'_s
    """
    chosen = set()
    # 学生ごとに利用可能なコントラクトを収集
    by_student: dict[int, list[int]] = {s: [] for s in range(market.n_students)}
    for (s, c) in available:
        by_student[s].append(c)

    for s, schools in by_student.items():
        if not schools:
            continue
        # 最善の学校 = 選好リストで最も前にある学校
        best_c = min(schools, key=lambda c: market.student_rank(s, c))
        chosen.add((s, best_c))

    return frozenset(chosen)


# ─────────────────────────────────────────────────────────────────────────────
# PLDA-RQ の選択関数 Ch_C (Definition 11)
# ─────────────────────────────────────────────────────────────────────────────

def ch_c_plda(
    X_prime: frozenset[tuple[int, int]],
    market: Market,
    priority_list: list[tuple[int, int]],
    verbose: bool = False,
) -> frozenset[tuple[int, int]]:
    """
    PLDA-RQ の学校側選択関数 Ch_C (Definition 11)。

    アルゴリズム:
      1. Y = ∅
      2. X' を PL 順にソート
      3. (s, c) を PL 順に処理:
           e_r(Y ∪ {(s, c)}) ≤ q_r (全 r) なら Y に追加
      4. Y を返す

    Parameters
    ----------
    X_prime       : 学生が選んだコントラクト集合
    market        : 市場情報
    priority_list : 全コントラクトの PL 順リスト（market.priority_list() で生成）
    verbose       : True なら採否ログを出力

    Returns
    -------
    frozenset : Ch_C(X')
    """
    tree = market.region_tree
    # X' に含まれるコントラクトを PL 順でフィルタ
    pl_rank = {contract: i for i, contract in enumerate(priority_list)}
    sorted_contracts = sorted(X_prime, key=lambda x: pl_rank.get(x, len(priority_list)))

    Y: frozenset[tuple[int, int]] = frozenset()

    for contract in sorted_contracts:
        Y_candidate = Y | {contract}
        e_vals = expected_min_count_all(Y_candidate, tree)
        if all(e <= node.max_quota for node, e in e_vals.items()):
            Y = Y_candidate
            if verbose:
                s, c = contract
                print(f"    ✓ 採用: ({market.s_name(s)}, {market.c_name(c)})")
        else:
            if verbose:
                s, c = contract
                # どの地域で違反したか
                violations = [
                    (node.name, e, node.max_quota)
                    for node, e in e_vals.items()
                    if e > node.max_quota
                ]
                print(f"    ✗ 却下: ({market.s_name(s)}, {market.c_name(c)}) "
                      f"— 違反地域: {violations}")

    return Y


# ─────────────────────────────────────────────────────────────────────────────
# RSDA-RQ の選択関数 Ch_C (Definition 12)
# ─────────────────────────────────────────────────────────────────────────────

def ch_c_rsda(
    X_prime: frozenset[tuple[int, int]],
    market: Market,
    round_robin_order: list[int],
    verbose: bool = False,
) -> frozenset[tuple[int, int]]:
    """
    RSDA-RQ の学校側選択関数 Ch_C (Definition 12)。

    アルゴリズム:
      1. Y = ∅, rejected = ∅
      2. 全コントラクトが Y か rejected に入ったら Y を返す
      3. ラウンドロビン順で学校 c を選ぶ
      4. c に関して Y にも rejected にもない最高優先度の学生 s を選ぶ
      5. e_r(Y ∪ {(s,c)}) ≤ q_r なら Y に追加、そうでなければ rejected に追加
      6. ステップ2へ

    Parameters
    ----------
    X_prime           : 学生が選んだコントラクト集合
    market            : 市場情報
    round_robin_order : 学校インデックスのラウンドロビン順
    verbose           : True なら採否ログを出力
    """
    tree = market.region_tree

    # 学校別にコントラクトを学校の優先順位でソート
    by_school: dict[int, list[tuple[int, int]]] = {c: [] for c in range(market.n_schools)}
    for contract in X_prime:
        s, c = contract
        by_school[c].append(contract)
    for c in range(market.n_schools):
        by_school[c].sort(key=lambda sc: market.school_rank(sc[1], sc[0]))

    Y: frozenset[tuple[int, int]] = frozenset()
    rejected: set[tuple[int, int]] = set()
    decided_count = 0
    total = len(X_prime)

    m = len(round_robin_order)
    round_idx = 0

    while decided_count < total:
        c = round_robin_order[round_idx % m]
        round_idx += 1

        # c に関して未決定のコントラクトを取得（優先順位順）
        available = [
            sc for sc in by_school[c]
            if sc not in Y and sc not in rejected
        ]
        if not available:
            # このラウンドで c の全コントラクトが決定済みならスキップ
            # 全学校が skip 状態ならループ終了（安全のため）
            if round_idx > total * m + m:
                break
            continue

        # 最高優先度のコントラクトを処理
        contract = available[0]
        s, _ = contract
        Y_candidate = Y | {contract}
        e_vals = expected_min_count_all(Y_candidate, tree)

        if all(e <= node.max_quota for node, e in e_vals.items()):
            Y = Y_candidate
            decided_count += 1
            if verbose:
                print(f"    ✓ 採用: ({market.s_name(s)}, {market.c_name(c)})")
        else:
            rejected.add(contract)
            decided_count += 1
            if verbose:
                violations = [
                    (node.name, e, node.max_quota)
                    for node, e in e_vals.items()
                    if e > node.max_quota
                ]
                print(f"    ✗ 却下: ({market.s_name(s)}, {market.c_name(c)}) "
                      f"— 違反地域: {violations}")

    return Y


# ─────────────────────────────────────────────────────────────────────────────
# 一般化 DA (Mechanism 1)
# ─────────────────────────────────────────────────────────────────────────────

def generalized_da(
    market: Market,
    ch_c_func,
    verbose: bool = False,
) -> frozenset[tuple[int, int]]:
    """
    一般化 Deferred Acceptance アルゴリズム (Mechanism 1)。

    アルゴリズム:
      1. Re = ∅
      2. X' = Ch_S(X \ Re),  X'' = Ch_C(X')
      3. X' = X'' なら X' を返す; そうでなければ Re ← Re ∪ (X' \ X''), ステップ2へ

    Parameters
    ----------
    market       : 市場情報
    ch_c_func    : 学校側選択関数 (X_prime, ...) → frozenset
    verbose      : True なら各ラウンドの詳細を出力
    """
    all_contracts = frozenset(
        (s, c)
        for s in range(market.n_students)
        for c in range(market.n_schools)
    )
    Re: frozenset[tuple[int, int]] = frozenset()

    round_num = 1
    while True:
        if verbose:
            print(f"\n--- ラウンド {round_num} ---")

        # 学生が選択
        X_prime = ch_students(all_contracts - Re, market)
        if verbose:
            contracts_str = ", ".join(
                f"({market.s_name(s)}, {market.c_name(c)})"
                for s, c in sorted(X_prime)
            )
            print(f"  学生選択 X': {{{contracts_str}}}")

        # 学校が選択
        X_double_prime = ch_c_func(X_prime)
        if verbose:
            accepted_str = ", ".join(
                f"({market.s_name(s)}, {market.c_name(c)})"
                for s, c in sorted(X_double_prime)
            )
            print(f"  学校選択 X'': {{{accepted_str}}}")

        # 収束判定
        if X_prime == X_double_prime:
            if verbose:
                print(f"\n  収束: X' = X'' → 終了")
            return X_prime

        # 却下されたコントラクトを Re に追加
        newly_rejected = X_prime - X_double_prime
        Re = Re | newly_rejected
        if verbose:
            rejected_str = ", ".join(
                f"({market.s_name(s)}, {market.c_name(c)})"
                for s, c in sorted(newly_rejected)
            )
            print(f"  新規却下: {{{rejected_str}}}")

        round_num += 1


# ─────────────────────────────────────────────────────────────────────────────
# PLDA-RQ (Priority List based DA with Regional Quotas)
# ─────────────────────────────────────────────────────────────────────────────

def plda_rq(
    market: Market,
    verbose: bool = False,
) -> frozenset[tuple[int, int]]:
    """
    PLDA-RQ (Priority List based Deferred Acceptance with Regional Quotas)。

    Section 5.2 の実装。
    PL 順にコントラクトを貪欲に採用する学校側選択関数を使った一般化 DA。

    性質 (Theorems 5-9):
        - Strategyproof
        - Fair (fairness)
        - PL-nonwasteful
        - PL-fair
        - 学生最適 PL-fair & PL-nonwasteful マッチングを実現
    """
    pl = market.priority_list()

    def _ch_c(X_prime: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        return ch_c_plda(X_prime, market, pl, verbose=verbose)

    return generalized_da(market, _ch_c, verbose=verbose)


# ─────────────────────────────────────────────────────────────────────────────
# RSDA-RQ (Round-robin Selection DA with Regional Quotas)
# ─────────────────────────────────────────────────────────────────────────────

def rsda_rq(
    market: Market,
    round_robin_order: list[int] | None = None,
    verbose: bool = False,
) -> frozenset[tuple[int, int]]:
    """
    RSDA-RQ (Round-robin Selection Deferred Acceptance with Regional Quotas)。

    Section 5.3 の実装。
    ラウンドロビン順で各学校が最高優先度の学生を選ぶ学校側選択関数を使った一般化 DA。

    Parameters
    ----------
    market             : 市場情報
    round_robin_order  : 学校のラウンドロビン順（None なら c1, c2, ..., cm）

    性質 (Theorems 10-12):
        - Strategyproof
        - Fair (fairness)
        - School-equitably-nonwasteful
    """
    if round_robin_order is None:
        round_robin_order = list(range(market.n_schools))

    def _ch_c(X_prime: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        return ch_c_rsda(X_prime, market, round_robin_order, verbose=verbose)

    return generalized_da(market, _ch_c, verbose=verbose)


# ─────────────────────────────────────────────────────────────────────────────
# ACDA (Artificial Cap Deferred Acceptance) — 比較ベースライン
# ─────────────────────────────────────────────────────────────────────────────

def _compute_artificial_caps(market: Market) -> tuple[list[int], list[int]]:
    """
    人工的な個別定員を計算する（ACDA 用）。

    方針:
      - 各学校の人工上限 q_c^art を、地域最高定員を各学校に比例配分して設定
      - 各学校の人工下限 p_c^art を、地域最低定員を各学校に比例配分して設定

    具体的なアルゴリズム（ボトムアップ）:
      1. 各地域 r の q_r を子の q の比率で各学校に配分
         q_c^art = min over all ancestor regions r containing c of:
                   floor(q_r * q_c / Σ_{c'∈r} q_c')
      2. 各地域 r の p_r を子の p の比率（または均等）で各学校に配分
         p_c^art = max over all ancestor regions r containing c of:
                   ceil(p_r / |r|)
    """
    n_schools = market.n_schools
    tree = market.region_tree

    # 各学校の元の個別定員
    orig_max = [market.individual_max_quota(c) for c in range(n_schools)]
    orig_min = [market.individual_min_quota(c) for c in range(n_schools)]

    art_max = list(orig_max)
    art_min = list(orig_min)

    for node in tree.all_nodes():
        schools_in_node = sorted(node.schools)
        if not schools_in_node or node.is_leaf():
            continue

        total_orig_max = sum(art_max[c] for c in schools_in_node)
        total_orig_min = sum(art_min[c] for c in schools_in_node)

        for c in schools_in_node:
            # 上限: 地域最大定員を比率配分
            if total_orig_max > 0:
                prop_max = node.max_quota * art_max[c] // total_orig_max
            else:
                prop_max = node.max_quota // len(schools_in_node)
            art_max[c] = min(art_max[c], prop_max)

            # 下限: 地域最小定員を均等配分（切り上げ）
            if total_orig_min > 0:
                prop_min = -(-node.min_quota * art_min[c] // total_orig_min)  # ceil
            else:
                prop_min = -(-node.min_quota // len(schools_in_node))
            art_min[c] = max(art_min[c], prop_min)

    # 整合性チェック: art_min ≤ art_max
    for c in range(n_schools):
        art_max[c] = max(art_max[c], art_min[c])

    return art_min, art_max


def acda(
    market: Market,
    verbose: bool = False,
) -> frozenset[tuple[int, int]]:
    """
    ACDA (Artificial Cap Deferred Acceptance) — 比較ベースライン。

    地域定員を個別定員に変換してから標準 DA を実行する。
    地域定員が自動的に満たされるよう個別定員を調整する。

    参考: Section 6 (simulation experiments)
    """
    art_min, art_max = _compute_artificial_caps(market)

    if verbose:
        print("  [ACDA] 人工定員:")
        for c in range(market.n_schools):
            print(f"    {market.c_name(c)}: min={art_min[c]}, max={art_max[c]}")

    # 人工定員を使って標準 DA (Ch_C は個別最大定員のみ参照)
    # 地域木の葉ノードの定員を一時的に置き換えて PLDA-RQ で実行
    # （地域制約なしの単純な DA と等価）
    # 元の木を複製して人工定員をセット
    def _replace_quotas(node: RegionNode, art_min, art_max) -> RegionNode:
        if node.is_leaf():
            c = next(iter(node.schools))
            return RegionNode(
                name=node.name,
                schools=node.schools,
                min_quota=art_min[c],
                max_quota=art_max[c],
                children=[],
                parent=None,
            )
        else:
            new_children = [_replace_quotas(child, art_min, art_max) for child in node.children]
            # 内部ノードの定員は子の合計から再計算（非拘束）
            sum_min = sum(c.min_quota for c in new_children)
            sum_max = sum(c.max_quota for c in new_children)
            new_node = RegionNode(
                name=node.name,
                schools=node.schools,
                min_quota=sum_min,
                max_quota=sum_max,
                children=new_children,
                parent=None,
            )
            for child in new_children:
                child.parent = new_node
            return new_node

    new_root = _replace_quotas(market.region_tree.root, art_min, art_max)
    new_tree = RegionTree(root=new_root)

    # 人工定員木で新しい市場を作成
    art_market = Market(
        student_names=market.student_names,
        school_names=market.school_names,
        student_prefs=market.student_prefs,
        school_priors=market.school_priors,
        region_tree=new_tree,
        tiebreak_order=market.tiebreak_order,
    )

    return plda_rq(art_market, verbose=verbose)


# ─────────────────────────────────────────────────────────────────────────────
# 結果の表示
# ─────────────────────────────────────────────────────────────────────────────

def print_matching(
    result: frozenset[tuple[int, int]],
    market: Market,
    title: str = "マッチング結果",
) -> None:
    """マッチング結果を見やすく表示する。"""
    assignment: dict[int, int] = {s: c for (s, c) in result}

    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

    # 学生視点
    print("\n【学生 → 学校】")
    for s in range(market.n_students):
        c = assignment.get(s, -1)
        school_str = market.c_name(c) if c != -1 else "未割当"
        print(f"  {market.s_name(s)}: {school_str}")

    # 学校視点
    print("\n【学校 → 学生一覧】")
    by_school: dict[int, list[int]] = {c: [] for c in range(market.n_schools)}
    for s, c in result:
        by_school[c].append(s)

    for c in range(market.n_schools):
        students_str = ", ".join(market.s_name(s) for s in sorted(by_school[c]))
        node = market.region_tree.node_for_school(c)
        print(f"  {market.c_name(c)} "
              f"(定員 p={node.min_quota}, q={node.max_quota}): "
              f"[{students_str}] ({len(by_school[c])}名)")
