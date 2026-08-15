# -*- coding: utf-8 -*-
"""
部署配属マッチングの実行例（【応用編】社内の部署配属 記事用）

社内の部署配属を題材に、制約の複雑さに応じて
DA → FDA → CA を使い分ける6つの実行例を収録する。

  例1: DA  — 新卒配属（定員制約のみ、5名 → 3部署）
  例2: FDA — 本部上限付き配属（14名 → 2本部5課、地域上限制約の社内版）
  例3: CA  — 兼務メンバーの工数配分（12名 → 3製品チーム、稼働量制約）
  例4: CA  — NGペアの分離＋配属禁止（16名 → 4チーム、定員＋回避制約＋受入不可能）
  例5: CA  — 若手の偏り防止（20名 → 4グループ、定員＋属性人数制約）
  例6: CA  — 総合演習（24名 → 5チーム、定員＋稼働量＋回避制約）
"""

from da_algorithm import Input as DAInput, deferred_acceptance
from fda_algorithm import Input as FDAInput, flexible_deferred_acceptance
from ca_algorithm import (
    Input as CAInput,
    cutoff_adjustment,
    capacity_constraint,
    budget_constraint,
    collision_avoidance_constraint,
    combined_constraint,
)
from matching_check import (
    check_stability,
    check_weak_stability,
    check_fairness,
    check_efficiency,
    check_individual_rationality,
)


# ─────────────────────────────────────────────
# 追加の制約ユーティリティ
# ─────────────────────────────────────────────

def group_quota_constraint(group: set[int], quota: int):
    """属性人数制約: group（例: 入社3年以内の社員）に属するメンバーが quota 人以下。

    遺伝的（部分集合でも実行可能）なので CA でそのまま扱える。
    """
    return lambda members: sum(1 for m in members if m in group) <= quota


def apply_forbidden_assignments(
    proposer_prefs: list[list[int]],
    receiver_prefs: list[list[int]],
    forbidden: dict[int, int],
) -> tuple[list[list[int]], list[list[int]]]:
    """配属禁止（社員 i を部署 j に配属してはならない）を選好リストの除外で表現する。

    forbidden: {社員idx: 禁止部署idx}（いずれも 0-indexed）

    【重要】配属禁止を CA の制約関数で表現してはならない。
    禁止対象者が部署の優先順位上位にいる場合、カットオフがその順位を
    超えるまで上がり、それより下位の応募者全員を巻き添えで排除してしまう。
    「受け入れ不可能（unacceptable）」として双方の選好リストから除外するのが
    理論的にも正しいモデリングである（個人合理性で保証される）。
    """
    pprefs = [list(p) for p in proposer_prefs]
    rprefs = [list(r) for r in receiver_prefs]
    for i, j in forbidden.items():
        pprefs[i] = [t for t in pprefs[i] if t != j + 1]
        rprefs[j] = [p for p in rprefs[j] if p != i + 1]
    return pprefs, rprefs


# ─────────────────────────────────────────────
# 例1: DA — 新卒配属（定員制約のみ）
# ─────────────────────────────────────────────

def example1(verbose=True):
    """例1: 新卒5名を3部署（開発部・インフラ部・データ分析部）へ配属"""
    print("=" * 65)
    print("例1【DA】新卒配属（定員制約のみ、5名 → 3部署）")
    print("=" * 65)

    p_names = ["佐藤", "鈴木", "高橋", "田中", "伊藤"]
    r_names = ["開発部", "インフラ部", "データ分析部"]

    # 新卒の希望順位（1=開発部, 2=インフラ部, 3=データ分析部）
    proposer_prefs = [
        [1, 3, 2],  # 佐藤
        [1, 2, 3],  # 鈴木
        [3, 1, 2],  # 高橋
        [2, 1, 3],  # 田中
        [1, 2, 3],  # 伊藤
    ]
    # 部署側の優先順位（面接評価順、1=佐藤, ..., 5=伊藤）
    receiver_prefs = [
        [2, 1, 5, 3, 4],  # 開発部
        [4, 5, 2, 1, 3],  # インフラ部
        [3, 1, 4, 2, 5],  # データ分析部
    ]
    capacities = [2, 2, 1]

    data = DAInput(proposer_prefs, receiver_prefs, capacities, p_names, r_names)
    result = deferred_acceptance(data, verbose)

    # 性質検証: DA は安定性（個人合理性＋ブロッキングペアなし）を保証する
    check_stability(proposer_prefs, receiver_prefs,
                    result.proposer_match, result.receiver_match,
                    capacities, p_names, r_names)
    check_efficiency(proposer_prefs, receiver_prefs,
                     result.proposer_match, result.receiver_match,
                     capacities, p_names, r_names)
    print()
    return result


# ─────────────────────────────────────────────
# 例2: FDA — 本部上限付き配属（地域上限制約の社内版）
# ─────────────────────────────────────────────

# 中途・新卒合わせて14名
EX2_PROPOSERS = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本",
                 "中村", "小林", "加藤", "吉田", "山田", "佐々木", "山口"]
# 開発本部（第1〜第3開発課）と業務本部（業務推進課・顧客サポート課）
EX2_RECEIVERS = ["第1開発課", "第2開発課", "第3開発課", "業務推進課", "顧客サポート課"]

# 各メンバーの希望順位（1=第1開発課, ..., 5=顧客サポート課）
EX2_PROPOSER_PREFS = [
    [2, 3, 5, 1, 4],  # 佐藤
    [3, 1, 4, 2, 5],  # 鈴木
    [1, 2, 3, 5, 4],  # 高橋
    [1, 5, 4, 3, 2],  # 田中
    [1, 2, 4, 3, 5],  # 伊藤
    [1, 2, 4, 3, 5],  # 渡辺
    [2, 3, 1, 5, 4],  # 山本
    [1, 5, 4, 3, 2],  # 中村
    [2, 1, 3, 4, 5],  # 小林
    [2, 5, 1, 4, 3],  # 加藤
    [1, 2, 5, 3, 4],  # 吉田
    [2, 1, 4, 5, 3],  # 山田
    [1, 2, 5, 4, 3],  # 佐々木
    [1, 2, 3, 5, 4],  # 山口
]
# 各課の優先順位（社内公募の選考評価順、1=佐藤, ..., 14=山口）
EX2_RECEIVER_PREFS = [
    [14, 2, 13, 10, 4, 12, 1, 7, 3, 6, 9, 11, 5, 8],   # 第1開発課
    [14, 5, 13, 6, 7, 2, 11, 8, 3, 1, 9, 4, 10, 12],   # 第2開発課
    [3, 4, 10, 13, 5, 12, 8, 1, 14, 7, 6, 11, 9, 2],   # 第3開発課
    [14, 4, 10, 1, 13, 12, 5, 6, 9, 3, 7, 11, 2, 8],   # 業務推進課
    [13, 6, 3, 1, 11, 4, 5, 14, 8, 12, 10, 7, 2, 9],   # 顧客サポート課
]
EX2_CAPACITIES    = [2, 2, 2, 3, 3]  # 各課の目標定員（計12 < 14名）
EX2_MAX_CAPS      = [5, 4, 4, 4, 4]  # 各課の設置上限（座席・指導体制の物理上限）
EX2_REGIONS       = [0, 0, 0, 1, 1]  # 0=開発本部, 1=業務本部
EX2_REGIONAL_CAPS = [8, 6]           # 本部ごとの総受入上限（人件費予算枠）


def example2_da_fails(verbose=True):
    """例2(前半): 目標定員のままDAで解くと、本部に余力があるのに未配属が出る"""
    print("=" * 65)
    print("例2【DAの失敗】目標定員でDAを実行（14名 → 5課）")
    print("=" * 65)

    data = DAInput(EX2_PROPOSER_PREFS, EX2_RECEIVER_PREFS, EX2_CAPACITIES,
                   EX2_PROPOSERS, EX2_RECEIVERS)
    result = deferred_acceptance(data, verbose)

    unmatched = [EX2_PROPOSERS[i] for i, m in enumerate(result.proposer_match) if m == -1]
    print(f"未配属者: {unmatched}（目標定員の合計12 < 14名のため必ず2名あぶれる）")
    print()
    return result


def example2(verbose=True):
    """例2(後半): FDAなら本部上限の範囲内で目標定員を柔軟に超過できる"""
    print("=" * 65)
    print("例2【FDA】本部上限付き配属（14名 → 2本部5課）")
    print("=" * 65)

    data = FDAInput(
        proposer_prefs=EX2_PROPOSER_PREFS,
        receiver_prefs=EX2_RECEIVER_PREFS,
        capacities=EX2_CAPACITIES,
        max_caps=EX2_MAX_CAPS,
        regions=EX2_REGIONS,
        regional_caps=EX2_REGIONAL_CAPS,
        nomination_order=[0, 1, 2, 3, 4],  # 指名順序: 第1開発課 → ... → 顧客サポート課
        proposer_names=EX2_PROPOSERS,
        receiver_names=EX2_RECEIVERS,
    )
    result = flexible_deferred_acceptance(data, verbose)

    # 本部別の受入人数を集計
    regional_count = [0, 0]
    for j, members in enumerate(result.receiver_match):
        regional_count[EX2_REGIONS[j]] += len(members)
    print(f"本部別人数: 開発本部 {regional_count[0]}/{EX2_REGIONAL_CAPS[0]}, "
          f"業務本部 {regional_count[1]}/{EX2_REGIONAL_CAPS[1]}")
    unmatched = [EX2_PROPOSERS[i] for i, m in enumerate(result.proposer_match) if m == -1]
    print(f"未配属者: {unmatched if unmatched else 'なし（全員配属）'}\n")

    # 性質検証: FDA は弱安定性を保証する（安定性は保証しない）
    check_stability(EX2_PROPOSER_PREFS, EX2_RECEIVER_PREFS,
                    result.proposer_match, result.receiver_match,
                    EX2_MAX_CAPS, EX2_PROPOSERS, EX2_RECEIVERS)
    check_weak_stability(EX2_PROPOSER_PREFS, EX2_RECEIVER_PREFS,
                         result.proposer_match, result.receiver_match,
                         EX2_MAX_CAPS, EX2_PROPOSERS, EX2_RECEIVERS,
                         regions=EX2_REGIONS, regional_caps=EX2_REGIONAL_CAPS)
    print()
    return result


# ─────────────────────────────────────────────
# 例3: CA — 兼務メンバーの工数配分（稼働量制約）
# ─────────────────────────────────────────────

EX3_PROPOSERS = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺",
                 "山本", "中村", "小林", "加藤", "吉田", "山田"]
EX3_RECEIVERS = ["製品Alpha", "製品Beta", "製品Gamma"]

# 各メンバーの希望順位（1=Alpha, 2=Beta, 3=Gamma）
EX3_PROPOSER_PREFS = [
    [1, 2, 3],  # 佐藤
    [2, 1, 3],  # 鈴木
    [1, 3, 2],  # 高橋
    [3, 2, 1],  # 田中
    [2, 1, 3],  # 伊藤
    [3, 1, 2],  # 渡辺
    [3, 1, 2],  # 山本
    [1, 2, 3],  # 中村
    [1, 2, 3],  # 小林
    [2, 3, 1],  # 加藤
    [1, 2, 3],  # 吉田
    [3, 1, 2],  # 山田
]
# 各製品チームの優先順位（スキルマッチ度順、1=佐藤, ..., 12=山田）
EX3_RECEIVER_PREFS = [
    [7, 10, 12, 9, 6, 1, 8, 11, 5, 3, 4, 2],   # 製品Alpha
    [3, 4, 11, 10, 7, 2, 5, 12, 6, 8, 9, 1],   # 製品Beta
    [9, 11, 3, 10, 12, 7, 1, 6, 2, 8, 4, 5],   # 製品Gamma
]
# 各メンバーが提供できる工数（人月）。1.0=専任、それ以外は兼務
EX3_LOADS = [1.0, 0.5, 0.8, 1.0, 0.4, 0.6, 1.0, 0.5, 0.8, 0.3, 0.6, 1.0]
# 各製品チームが受け入れられる工数の上限（人月）
EX3_MAX_WORKLOADS = [3.5, 2.5, 2.0]


def example3(verbose=True):
    """例3: 兼務メンバー12名の工数を3製品チームへ配分（稼働量制約）"""
    print("=" * 65)
    print("例3【CA】兼務メンバーの工数配分（12名 → 3製品チーム）")
    print("=" * 65)

    # 稼働量制約: チーム j に配属されたメンバーの工数合計 <= 上限
    costs = {i: EX3_LOADS[i] for i in range(len(EX3_PROPOSERS))}
    constraints = [budget_constraint(costs, b) for b in EX3_MAX_WORKLOADS]

    data = CAInput(EX3_PROPOSER_PREFS, EX3_RECEIVER_PREFS, constraints,
                   EX3_PROPOSERS, EX3_RECEIVERS)
    result = cutoff_adjustment(data, verbose)

    # チーム別の工数集計
    for j, members in enumerate(result.receiver_match):
        total = sum(EX3_LOADS[i] for i in members)
        names = ", ".join(EX3_PROPOSERS[i] for i in members)
        print(f"  {EX3_RECEIVERS[j]}: [{names}] "
              f"工数計 {total:.1f}/{EX3_MAX_WORKLOADS[j]} 人月")
    unmatched = [EX3_PROPOSERS[i] for i, m in enumerate(result.proposer_match) if m == -1]
    print(f"  未配分（現所属で継続）: {unmatched if unmatched else 'なし'}\n")

    # 性質検証: CA は公平性を保証する（効率性は保証しない）
    check_fairness(EX3_PROPOSER_PREFS, EX3_RECEIVER_PREFS,
                   result.proposer_match, result.receiver_match,
                   EX3_PROPOSERS, EX3_RECEIVERS)
    print()
    return result


# ─────────────────────────────────────────────
# 例4: CA — NGペアの分離＋配属禁止（定員＋回避制約＋受入不可能）
# ─────────────────────────────────────────────

EX4_PROPOSERS = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
                 "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上"]
EX4_RECEIVERS = ["第1チーム", "第2チーム", "第3チーム", "第4チーム"]

# 各メンバーの希望順位（1=第1チーム, ..., 4=第4チーム）
EX4_PROPOSER_PREFS = [
    [2, 1, 3, 4],  # 佐藤
    [2, 3, 1, 4],  # 鈴木
    [3, 2, 4, 1],  # 高橋
    [4, 2, 1, 3],  # 田中
    [3, 1, 4, 2],  # 伊藤
    [1, 4, 2, 3],  # 渡辺
    [4, 1, 3, 2],  # 山本
    [1, 3, 2, 4],  # 中村
    [3, 4, 1, 2],  # 小林
    [3, 2, 1, 4],  # 加藤
    [4, 1, 2, 3],  # 吉田
    [2, 3, 1, 4],  # 山田
    [1, 2, 3, 4],  # 佐々木
    [2, 4, 1, 3],  # 山口
    [3, 1, 2, 4],  # 松本
    [1, 4, 3, 2],  # 井上
]
# 各チームの優先順位（1=佐藤, ..., 16=井上）
EX4_RECEIVER_PREFS = [
    [8, 10, 6, 7, 15, 11, 13, 9, 2, 3, 14, 16, 5, 12, 1, 4],   # 第1チーム
    [6, 2, 14, 13, 3, 5, 16, 11, 7, 12, 4, 15, 1, 10, 9, 8],   # 第2チーム
    [13, 8, 1, 12, 15, 9, 14, 10, 7, 16, 2, 6, 4, 3, 5, 11],   # 第3チーム
    [3, 11, 8, 13, 14, 1, 12, 16, 6, 10, 5, 9, 2, 7, 15, 4],   # 第4チーム
]
EX4_CAPACITIES = [5, 5, 4, 4]
# 同一チームに配属してはならないペア（0-indexed）
#   佐藤(0)-鈴木(1): 兼業先が競合関係（利益相反）
#   伊藤(4)-加藤(9): 過去のハラスメント事案
#   佐々木(12)-井上(15): 夫婦（社内規程により同一チーム不可）
EX4_CONFLICT_PAIRS = [(0, 1), (4, 9), (12, 15)]
# 特定チームへの配属禁止（社員idx → 禁止チームidx、いずれも0-indexed）
#   高橋(2) → 第2チーム: 直前まで第2チーム案件の内部監査を担当（独立性の確保）
#   渡辺(5) → 第1チーム: 第1チームの主要取引先に近親者が在籍（利益相反）
#   吉田(10) → 第4チーム: 夜間オンコール免除措置中（第4チームはオンコール必須）
EX4_FORBIDDEN = {2: 1, 5: 0, 10: 3}


def example4(verbose=True):
    """例4: 16名を4チームへ配属（定員＋回避制約＋配属禁止3名）"""
    print("=" * 65)
    print("例4【CA】NGペアの分離＋配属禁止（16名 → 4チーム）")
    print("=" * 65)

    # 配属禁止は「受け入れ不可能」として双方の選好リストから除外する
    pprefs, rprefs = apply_forbidden_assignments(
        EX4_PROPOSER_PREFS, EX4_RECEIVER_PREFS, EX4_FORBIDDEN)

    # NGペアの分離は回避制約（定員制約との複合）で表現する
    constraints = [combined_constraint(c, EX4_CONFLICT_PAIRS) for c in EX4_CAPACITIES]

    data = CAInput(pprefs, rprefs, constraints, EX4_PROPOSERS, EX4_RECEIVERS)
    result = cutoff_adjustment(data, verbose)

    # NGペアが分離されたか確認
    for a, b in EX4_CONFLICT_PAIRS:
        same = (result.proposer_match[a] == result.proposer_match[b]
                and result.proposer_match[a] != -1)
        status = "❌ 同一チーム" if same else "✅ 分離"
        print(f"  NGペア（{EX4_PROPOSERS[a]}, {EX4_PROPOSERS[b]}）: {status}")
    # 配属禁止が守られたか確認
    for i, j in EX4_FORBIDDEN.items():
        ok = result.proposer_match[i] != j
        actual = (EX4_RECEIVERS[result.proposer_match[i]]
                  if result.proposer_match[i] != -1 else "未配属")
        status = "✅ 回避" if ok else "❌ 違反"
        print(f"  配属禁止（{EX4_PROPOSERS[i]} → {EX4_RECEIVERS[j]}）: "
              f"{status}（実際の配属: {actual}）")
    unmatched = [EX4_PROPOSERS[i] for i, m in enumerate(result.proposer_match) if m == -1]
    print(f"  未配属者: {unmatched if unmatched else 'なし（全員配属）'}\n")

    # 性質検証（除外後の選好リストに対して検証する）
    check_individual_rationality(pprefs, rprefs,
                                 result.proposer_match, result.receiver_match,
                                 EX4_PROPOSERS, EX4_RECEIVERS)
    check_fairness(pprefs, rprefs,
                   result.proposer_match, result.receiver_match,
                   EX4_PROPOSERS, EX4_RECEIVERS)
    print()
    return result


# ─────────────────────────────────────────────
# 例5: CA — 若手の偏り防止（定員＋属性人数制約）
# ─────────────────────────────────────────────

EX5_PROPOSERS = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
                 "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上",
                 "木村", "林", "斎藤", "清水"]
EX5_RECEIVERS = ["第1グループ", "第2グループ", "第3グループ", "第4グループ"]

# 各メンバーの希望順位（1=第1G, 2=第2G, 3=第3G, 4=第4G）
# 第1グループは新規AIプロダクト担当の花形部署で、特に若手の人気が高い
EX5_PROPOSER_PREFS = [
    [1, 2, 4, 3],  # 佐藤
    [1, 3, 2, 4],  # 鈴木（若手）
    [3, 1, 2, 4],  # 高橋
    [4, 1, 3, 2],  # 田中
    [1, 4, 3, 2],  # 伊藤（若手）
    [1, 3, 4, 2],  # 渡辺
    [4, 1, 2, 3],  # 山本
    [3, 1, 4, 2],  # 中村（若手）
    [4, 1, 2, 3],  # 小林
    [4, 2, 3, 1],  # 加藤
    [1, 4, 2, 3],  # 吉田（若手）
    [2, 1, 4, 3],  # 山田
    [1, 4, 2, 3],  # 佐々木
    [1, 3, 2, 4],  # 山口（若手）
    [1, 2, 4, 3],  # 松本
    [2, 1, 3, 4],  # 井上
    [1, 2, 4, 3],  # 木村（若手）
    [3, 2, 4, 1],  # 林
    [1, 4, 3, 2],  # 斎藤（若手）
    [1, 3, 2, 4],  # 清水
]
# 各グループの優先順位（1=佐藤, ..., 20=清水）
EX5_RECEIVER_PREFS = [
    [15, 7, 18, 12, 19, 11, 4, 17, 3, 2, 1, 6, 14, 16, 13, 8, 9, 5, 20, 10],   # 第1G
    [6, 9, 14, 11, 8, 13, 7, 12, 4, 1, 3, 18, 16, 15, 19, 2, 17, 20, 10, 5],   # 第2G
    [12, 3, 16, 11, 20, 10, 1, 15, 2, 17, 14, 8, 13, 6, 19, 4, 18, 7, 9, 5],   # 第3G
    [16, 15, 1, 4, 7, 10, 5, 2, 8, 19, 6, 3, 14, 12, 9, 17, 20, 18, 11, 13],   # 第4G
]
EX5_CAPACITIES = [5, 5, 5, 5]
# 入社3年以内の社員（0-indexed）: 鈴木, 伊藤, 中村, 吉田, 山口, 木村, 斎藤 の7名
EX5_JUNIORS = {1, 4, 7, 10, 13, 16, 18}
# 各グループの若手受入上限（OJT・育成負荷の観点）
EX5_JUNIOR_QUOTA = 2


def _print_junior_distribution(result, label):
    """グループ別の若手人数を表示する"""
    for j, members in enumerate(result.receiver_match):
        n_jr = sum(1 for i in members if i in EX5_JUNIORS)
        names = ", ".join(EX5_PROPOSERS[i] + ("(若)" if i in EX5_JUNIORS else "")
                          for i in members)
        print(f"  {EX5_RECEIVERS[j]}: [{names}] 若手{n_jr}名")
    unmatched = [EX5_PROPOSERS[i] for i, m in enumerate(result.proposer_match) if m == -1]
    print(f"  未配属者: {unmatched if unmatched else 'なし（全員配属）'}（{label}）\n")


def example5(verbose=True):
    """例5: 20名を4グループへ配属（若手は各グループ2名まで）"""
    print("=" * 65)
    print("例5【CA】若手の偏り防止（20名 → 4グループ、若手上限2名）")
    print("=" * 65)

    # (1) まず定員制約のみで解く → 花形部署に若手が集中する
    print("--- (1) 定員制約のみ ---")
    constraints0 = [capacity_constraint(c) for c in EX5_CAPACITIES]
    data0 = CAInput(EX5_PROPOSER_PREFS, EX5_RECEIVER_PREFS, constraints0,
                    EX5_PROPOSERS, EX5_RECEIVERS)
    result0 = cutoff_adjustment(data0, verbose=False)
    _print_junior_distribution(result0, "定員のみ")

    # (2) 若手人数制約を追加して解く
    print("--- (2) 定員制約＋若手人数制約（各グループ2名まで） ---")

    def make_constraint(cap: int):
        c_cap = capacity_constraint(cap)
        c_jr  = group_quota_constraint(EX5_JUNIORS, EX5_JUNIOR_QUOTA)
        return lambda members: c_cap(members) and c_jr(members)

    constraints1 = [make_constraint(c) for c in EX5_CAPACITIES]
    data1 = CAInput(EX5_PROPOSER_PREFS, EX5_RECEIVER_PREFS, constraints1,
                    EX5_PROPOSERS, EX5_RECEIVERS)
    result1 = cutoff_adjustment(data1, verbose)
    _print_junior_distribution(result1, "若手上限あり")

    # 性質検証
    check_fairness(EX5_PROPOSER_PREFS, EX5_RECEIVER_PREFS,
                   result1.proposer_match, result1.receiver_match,
                   EX5_PROPOSERS, EX5_RECEIVERS)
    print()
    return result1


# ─────────────────────────────────────────────
# 例6: CA — 総合演習（定員＋稼働量＋回避制約）
# ─────────────────────────────────────────────

EX6_PROPOSERS = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
                 "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上",
                 "木村", "林", "斎藤", "清水", "森", "池田", "橋本", "阿部"]
EX6_RECEIVERS = ["基盤チーム", "アプリチーム", "データチーム", "SREチーム", "QAチーム"]

# 各メンバーの希望順位（1=基盤, 2=アプリ, 3=データ, 4=SRE, 5=QA）
EX6_PROPOSER_PREFS = [
    [1, 3, 2, 5, 4],  # 佐藤
    [2, 5, 1, 4, 3],  # 鈴木
    [2, 3, 4, 1, 5],  # 高橋
    [2, 5, 4, 1, 3],  # 田中
    [2, 4, 1, 5, 3],  # 伊藤
    [4, 5, 3, 1, 2],  # 渡辺
    [2, 5, 3, 4, 1],  # 山本
    [4, 3, 5, 2, 1],  # 中村
    [5, 2, 1, 3, 4],  # 小林
    [1, 5, 2, 4, 3],  # 加藤
    [1, 2, 4, 3, 5],  # 吉田
    [3, 5, 4, 2, 1],  # 山田
    [5, 3, 2, 1, 4],  # 佐々木
    [5, 3, 4, 1, 2],  # 山口
    [1, 3, 4, 2, 5],  # 松本
    [1, 4, 3, 2, 5],  # 井上
    [1, 3, 2, 5, 4],  # 木村
    [2, 5, 1, 3, 4],  # 林
    [3, 2, 5, 1, 4],  # 斎藤
    [5, 1, 3, 2, 4],  # 清水
    [2, 3, 5, 1, 4],  # 森
    [3, 4, 2, 1, 5],  # 池田
    [2, 4, 5, 3, 1],  # 橋本
    [4, 2, 1, 3, 5],  # 阿部
]
# 各チームの優先順位（1=佐藤, ..., 24=阿部）
EX6_RECEIVER_PREFS = [
    [22, 15, 11, 20, 18, 24, 4, 19, 10, 1, 8, 21, 3, 7, 13, 6, 5, 23, 14, 12, 16, 17, 2, 9],   # 基盤
    [23, 1, 22, 11, 5, 17, 12, 3, 6, 13, 18, 19, 7, 10, 15, 2, 4, 14, 20, 24, 9, 21, 8, 16],   # アプリ
    [4, 5, 13, 23, 17, 15, 16, 2, 10, 3, 20, 8, 9, 12, 24, 18, 21, 7, 1, 22, 19, 14, 6, 11],   # データ
    [16, 20, 1, 2, 11, 17, 5, 13, 15, 12, 8, 24, 4, 9, 21, 23, 6, 22, 3, 14, 19, 18, 7, 10],   # SRE
    [11, 6, 16, 8, 4, 14, 18, 22, 15, 7, 10, 21, 17, 19, 23, 5, 24, 13, 3, 9, 12, 1, 20, 2],   # QA
]
EX6_CAPACITIES = [6, 5, 5, 4, 4]  # 定員（人数）計24

# 提供工数（人月）。専任=1.0、育児短時間勤務・兼務などは1.0未満
EX6_LOADS = [1.0] * 24
EX6_LOADS[2]  = 0.5  # 高橋（兼務）
EX6_LOADS[5]  = 0.8  # 渡辺（時短勤務）
EX6_LOADS[8]  = 0.5  # 小林（兼務）
EX6_LOADS[13] = 0.6  # 山口（兼務）
EX6_LOADS[17] = 0.8  # 林（時短勤務）
EX6_LOADS[20] = 0.5  # 森（兼務）
# 各チームが受け入れられる工数の上限（人月）
EX6_MAX_WORKLOADS = [5.5, 4.5, 4.5, 3.5, 3.5]

# 同一チームに配属してはならないペア（0-indexed）
#   田中(3)-中村(7): 利益相反、吉田(10)-池田(21): 親子（社内規程）
EX6_CONFLICT_PAIRS = [(3, 7), (10, 21)]


def example6(verbose=True):
    """例6: 24名を5チームへ配属（定員＋稼働量＋回避制約の組み合わせ）"""
    print("=" * 65)
    print("例6【CA】総合演習（24名 → 5チーム、定員＋稼働量＋回避制約）")
    print("=" * 65)

    costs = {i: EX6_LOADS[i] for i in range(len(EX6_PROPOSERS))}

    def make_constraint(cap: int, max_workload: float):
        """定員・稼働量・回避の3制約をすべて満たす場合のみ実行可能"""
        c_cap  = capacity_constraint(cap)
        c_load = budget_constraint(costs, max_workload)
        c_ng   = collision_avoidance_constraint(EX6_CONFLICT_PAIRS)
        return lambda members: c_cap(members) and c_load(members) and c_ng(members)

    constraints = [make_constraint(EX6_CAPACITIES[j], EX6_MAX_WORKLOADS[j])
                   for j in range(len(EX6_RECEIVERS))]

    data = CAInput(EX6_PROPOSER_PREFS, EX6_RECEIVER_PREFS, constraints,
                   EX6_PROPOSERS, EX6_RECEIVERS)
    result = cutoff_adjustment(data, verbose)

    # チーム別の集計
    for j, members in enumerate(result.receiver_match):
        total = sum(EX6_LOADS[i] for i in members)
        names = ", ".join(EX6_PROPOSERS[i] for i in members)
        print(f"  {EX6_RECEIVERS[j]}（定員{EX6_CAPACITIES[j]}・"
              f"工数上限{EX6_MAX_WORKLOADS[j]}）: [{names}] "
              f"人数{len(members)} 工数計{total:.1f}")
    for a, b in EX6_CONFLICT_PAIRS:
        same = (result.proposer_match[a] == result.proposer_match[b]
                and result.proposer_match[a] != -1)
        status = "❌ 同一チーム" if same else "✅ 分離"
        print(f"  NGペア（{EX6_PROPOSERS[a]}, {EX6_PROPOSERS[b]}）: {status}")
    unmatched = [EX6_PROPOSERS[i] for i, m in enumerate(result.proposer_match) if m == -1]
    print(f"  未配属者: {unmatched if unmatched else 'なし（全員配属）'}\n")

    # 性質検証: 制約が組み合わさっても公平性は維持される
    check_fairness(EX6_PROPOSER_PREFS, EX6_RECEIVER_PREFS,
                   result.proposer_match, result.receiver_match,
                   EX6_PROPOSERS, EX6_RECEIVERS)
    print()
    return result


if __name__ == "__main__":
    example1(verbose=True)
    example2_da_fails(verbose=False)
    example2(verbose=True)
    example3(verbose=True)
    example4(verbose=True)
    example5(verbose=True)
    example6(verbose=True)
