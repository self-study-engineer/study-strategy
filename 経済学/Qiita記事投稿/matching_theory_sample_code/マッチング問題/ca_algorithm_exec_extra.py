"""
CA アルゴリズムの実行例

ca_algorithm.py のアルゴリズムを3パターンで動作確認する。
  例4: 部→課→係 の3階層定員制約（30社員・10係）
  例5: 定員制約 ∧ 回避制約の組み合わせ（安定性❌ / 公平性✅）
  例6: 稼働量制約 ∧ 課レベル回避制約（ca_algorithm_custom.py を使用）
"""

import math
from ca_algorithm_custom import WorkloadInput, cutoff_adjustment_workload
from ca_algorithm import (
    Input,
    capacity_constraint,
    budget_constraint,
    collision_avoidance_constraint,
    combined_constraint,
    cutoff_adjustment,
)
from matching_check import check_all, check_individual_rationality, check_fairness, check_stability, check_weak_stability


def example1(verbose=True):
    """例1: 学生と大学のマッチング（定員制約のみ）— DA と同じ結果になることを確認"""
    print("=" * 65)
    print("例1: 学生と大学の CA マッチング（定員制約のみ）")
    print("=" * 65)
    print()

    data = Input(
        proposer_prefs=[
            [1, 2, 3, 4],   # 田中: 東工大 > 早稲田 > 慶應 > 明治
            [1, 3, 2, 4],   # 鈴木: 東工大 > 慶應 > 早稲田 > 明治
            [2, 1, 3, 4],   # 佐藤: 早稲田 > 東工大 > 慶應 > 明治
            [3, 2, 1, 4],   # 高橋: 慶應 > 早稲田 > 東工大 > 明治
        ],
        receiver_prefs=[
            [2, 1, 3, 4],   # 東工大: 鈴木 > 田中 > 佐藤 > 高橋
            [1, 2, 4, 3],   # 早稲田: 田中 > 鈴木 > 高橋 > 佐藤
            [4, 3, 1, 2],   # 慶應:   高橋 > 佐藤 > 田中 > 鈴木
            [3, 4, 2, 1],   # 明治:   佐藤 > 高橋 > 鈴木 > 田中
        ],
        constraints=[
            capacity_constraint(1),
            capacity_constraint(1),
            capacity_constraint(1),
            capacity_constraint(1),
        ],
        proposer_names=["田中", "鈴木", "佐藤", "高橋"],
        receiver_names=["東工大", "早稲田", "慶應", "明治"],
    )

    result = cutoff_adjustment(data)
    check_all(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        capacities=[1, 1, 1, 1],
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )


def example2(verbose=True):
    """
    例2: 予算制約による保育園マッチング
    ※ CA は定員制約ではなく予算制約を直接扱えるため、「誰を入れるか」という構成を考慮した最適配分を行う
    """
    print("=" * 65)
    print("例2: 予算制約による保育園マッチング")
    print("=" * 65)
    print()

    child_names = ["みらい", "はるか", "ゆうと", "みさき", "けんた"]
    # コスト（CA アルゴリズムは 0-indexed 提案者番号を使うため 0-indexed で定義）
    costs = {
        0: 1/3,  # みらい（0歳）
        1: 1/3,  # はるか（0歳）
        2: 1/6,  # ゆうと（1歳）
        3: 1/6,  # みさき（1歳）
        4: 1/6,  # けんた（1歳）
    }

    print("【児童と年齢コスト】")
    for i, name in enumerate(child_names):
        print(f"  {name}: コスト {costs[i]:.3f}")
    print(f"  保育士1人の予算: 1.0人分")
    print()

    data = Input(
        proposer_prefs=[[1]] * 5,              # 全員がひまわり保育園のみ
        receiver_prefs=[[1, 2, 3, 4, 5]],      # ひまわり保育園: みらい>はるか>...>けんた
        constraints=[budget_constraint(costs, budget=1.0)],
        proposer_names=child_names,
        receiver_names=["ひまわり保育園"],
    )

    result = cutoff_adjustment(data, verbose=verbose)

    # 予算制約は Callable であり整数の capacities で表現できないため、
    # 個人合理性・公平性のみ check 関数で検証し、
    # 効率性（無駄なし）は制約関数で直接確認する。
    check_individual_rationality(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_stability(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_fairness(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    print()

    # 入園した児童のコスト合計を表示
    matched = sorted(result.receiver_match[0])
    total_cost = sum(costs[p] for p in matched)
    names_str = "、".join(data.p_name(p) for p in matched)
    print(f"【配分結果】{names_str}（コスト合計: {total_cost:.3f} / 予算: 1.0）")
    print()


def example3(verbose=True):
    """例3: 回避制約（同一クラスへの配属禁止ペア4組）"""
    print("=" * 65)
    print("例3: 回避制約（同一クラスへの配属禁止ペア）")
    print("=" * 65)
    print()

    # 同一クラスに配属してはならないペア（0-indexed）
    conflict_pairs = [(0, 1), (2, 3), (4, 5), (6, 7)]

    print("【配属禁止ペア】（同じクラスに配属してはならない）")
    pair_labels = [("学生1", "学生2"), ("学生3", "学生4"),
                   ("学生5", "学生6"), ("学生7", "学生8")]
    reasons = ["前校のトラブル", "競合プロジェクト", "学業上の利益相反", "親族関係"]
    for (a, b), reason in zip(pair_labels, reasons):
        print(f"  ({a}, {b}) : {reason}")
    print()

    data = Input(
        proposer_prefs=[
            [1, 2, 3, 4],   # 学生1: クラスA > クラスB > クラスC > クラスD
            [1, 3, 2, 4],   # 学生2: クラスA > クラスC > クラスB > クラスD  ← 学生1と第1志望が衝突
            [2, 1, 3, 4],   # 学生3: クラスB > クラスA > クラスC > クラスD
            [2, 4, 3, 1],   # 学生4: クラスB > クラスD > クラスC > クラスA  ← 学生3と第1志望が衝突
            [3, 2, 1, 4],   # 学生5: クラスC > クラスB > クラスA > クラスD
            [3, 4, 2, 1],   # 学生6: クラスC > クラスD > クラスB > クラスA  ← 学生5と第1志望が衝突
            [4, 1, 3, 2],   # 学生7: クラスD > クラスA > クラスC > クラスB
            [4, 2, 1, 3],   # 学生8: クラスD > クラスB > クラスA > クラスC  ← 学生7と第1志望が衝突
        ],
        receiver_prefs=[
            [1, 3, 5, 7, 6, 4, 8, 2],  # クラスA: 学生2 が最下位（禁止ペアの下位方）
            [3, 1, 5, 7, 6, 2, 8, 4],  # クラスB: 学生4 が最下位
            [5, 3, 1, 7, 2, 8, 4, 6],  # クラスC: 学生6 が最下位
            [7, 5, 3, 1, 4, 2, 6, 8],  # クラスD: 学生8 が最下位
        ],
        constraints=[
            collision_avoidance_constraint(conflict_pairs),  # クラスA
            collision_avoidance_constraint(conflict_pairs),  # クラスB
            collision_avoidance_constraint(conflict_pairs),  # クラスC
            collision_avoidance_constraint(conflict_pairs),  # クラスD
        ],
        proposer_names=["学生1","学生2","学生3","学生4","学生5","学生6","学生7","学生8"],
        receiver_names=["クラスA","クラスB","クラスC","クラスD"],
    )

    result = cutoff_adjustment(data, verbose=verbose)

    check_individual_rationality(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_stability(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_weak_stability(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_fairness(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    print()

    print("【配属禁止ペアの分離確認】")
    pair_separated = True
    for a, b in conflict_pairs:
        ra = result.proposer_match[a]
        rb = result.proposer_match[b]
        same = (ra == rb and ra != -1)
        status = "❌ 同一クラスに配属（制約違反）" if same else "✅ 別々のクラスに配属"
        print(f"  ({data.p_name(a)}, {data.p_name(b)}): "
              f"{data.r_name(ra) if ra != -1 else '未配分'} / "
              f"{data.r_name(rb) if rb != -1 else '未配分'} → {status}")
        if same:
            pair_separated = False
    print()


def example4(verbose=True):
    """例4: 部→課→係 の3階層定員制約によるマッチング"""
    print("=" * 65)
    print("例4: 部→課→係 の3階層定員制約によるマッチング")
    print("=" * 65)
    print()

    # ─── 組織構造の定義 ───────────────────────────────────────────────────────
    ka_names = ["第1課", "第2課", "第3課", "第4課", "第5課"]
    ka_caps  = [5, 4, 6, 7, 8]

    kakari_names = []
    kakari_caps  = []
    for i, cap in enumerate(ka_caps):
        k1 = math.ceil(cap / 2)    # 1係: 奇数なら多い方
        k2 = math.floor(cap / 2)   # 2係: 奇数なら少ない方
        kakari_names.append(f"{ka_names[i]}1係")
        kakari_names.append(f"{ka_names[i]}2係")
        kakari_caps.extend([k1, k2])
    # kakari_caps = [3, 2, 2, 2, 3, 3, 4, 3, 4, 4]  合計=30

    R = len(kakari_caps)  # 10係

    print("【係の定員】（合計=%d人）" % sum(kakari_caps))
    for i in range(0, R, 2):
        ka_idx = i // 2
        print(f"  {ka_names[ka_idx]}（上限{ka_caps[ka_idx]}人）: "
              f"{kakari_names[i]}=上限{kakari_caps[i]}人, "
              f"{kakari_names[i+1]}=上限{kakari_caps[i+1]}人")
    print()

    # ─── 社員30人の名前 ─────────────────────────────────────────────────────
    employee_names = [f"社員{i+1:02d}" for i in range(30)]

    # ─── 選好リスト（1-indexed 係番号） ──────────────────────────────────────
    #   係1=第1課1係, 係2=第1課2係, 係3=第2課1係, 係4=第2課2係,
    #   係5=第3課1係, 係6=第3課2係, 係7=第4課1係, 係8=第4課2係,
    #   係9=第5課1係, 係10=第5課2係
    proposer_prefs = []
    # 第1課希望: 社員01〜07（7人 vs 定員5人）
    for _ in range(5): proposer_prefs.append([1, 2, 9, 10, 5, 6, 7, 8, 3, 4])  # 1係優先
    for _ in range(2): proposer_prefs.append([2, 1, 10, 9, 6, 5, 8, 7, 4, 3])  # 2係優先
    # 第2課希望: 社員08〜11（4人 vs 定員4人）
    for _ in range(2): proposer_prefs.append([3, 4, 9, 10, 1, 2, 5, 6, 7, 8])
    for _ in range(2): proposer_prefs.append([4, 3, 10, 9, 2, 1, 6, 5, 8, 7])
    # 第3課希望: 社員12〜19（8人 vs 定員6人）
    for _ in range(4): proposer_prefs.append([5, 6, 9, 10, 7, 8, 1, 2, 3, 4])
    for _ in range(4): proposer_prefs.append([6, 5, 10, 9, 8, 7, 2, 1, 4, 3])
    # 第4課希望: 社員20〜27（8人 vs 定員7人）
    for _ in range(4): proposer_prefs.append([7, 8, 9, 10, 5, 6, 3, 4, 1, 2])
    for _ in range(4): proposer_prefs.append([8, 7, 10, 9, 6, 5, 4, 3, 2, 1])
    # 第5課希望: 社員28〜30（3人 vs 定員8人）
    for _ in range(2): proposer_prefs.append([9, 10, 7, 8, 5, 6, 3, 4, 1, 2])
    proposer_prefs.append([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])

    # 全係共通の優先順位: 社員番号が小さいほど優先
    receiver_prefs = [list(range(1, 31))] * R

    data = Input(
        proposer_prefs=proposer_prefs,
        receiver_prefs=receiver_prefs,
        constraints=[capacity_constraint(cap) for cap in kakari_caps],
        proposer_names=employee_names,
        receiver_names=kakari_names,
    )

    result = cutoff_adjustment(data, verbose=verbose)  # 30人×10係の反復は省略

    check_all(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        capacities=kakari_caps,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )

    # ─── 部→課→係 の階層別表示 ─────────────────────────────────────────────
    print("【部→課→係 の階層別マッチング結果】")
    total = sum(1 for r in result.proposer_match if r != -1)
    print(f"  部 合計: {total}人 / 上限{sum(kakari_caps)}人")
    print()

    for ka_idx, (ka_name, ka_cap) in enumerate(zip(ka_names, ka_caps)):
        k1_idx = ka_idx * 2
        k2_idx = ka_idx * 2 + 1
        k1 = sorted(result.receiver_match[k1_idx])
        k2 = sorted(result.receiver_match[k2_idx])
        print(f"  {ka_name}（{len(k1)+len(k2)}/{ka_cap}人）")
        print(f"    {kakari_names[k1_idx]}（{len(k1)}/{kakari_caps[k1_idx]}人）: "
              f"{', '.join(employee_names[p] for p in k1) or '（なし）'}")
        print(f"    {kakari_names[k2_idx]}（{len(k2)}/{kakari_caps[k2_idx]}人）: "
              f"{', '.join(employee_names[p] for p in k2) or '（なし）'}")
    print()

    print("【第1希望以外に配属された社員】")
    for p, r in enumerate(result.proposer_match):
        first_choice = proposer_prefs[p][0] - 1
        if r != first_choice and r != -1:
            print(f"  {employee_names[p]}: 第1希望={kakari_names[first_choice]} "
                  f"→ 実際={kakari_names[r]}")


def example5(verbose=True):
    """例5: 定員制約 ∧ 回避制約の組み合わせ（安定性❌ / 公平性✅）— 制約組み合わせで安定性が崩れる典型例"""
    print("=" * 65)
    print("例5: 定員制約 ∧ 回避制約の組み合わせ（安定性❌ / 公平性✅）")
    print("=" * 65)
    print()

    # 禁止グループ（0-indexed）
    #   3人組: 社員01(0), 社員02(1), 社員03(2) → 3通りのペアすべてを登録
    #   2人組B: 社員04(3), 社員05(4)
    #   2人組C: 社員06(5), 社員07(6)
    conflict_pairs = [(0,1), (0,2), (1,2), (3,4), (5,6)]

    print("【配属禁止グループ】")
    print("  3人組: (社員01, 社員02, 社員03) ← 3人のうち2人が同じ課に入れない")
    print("  2人組B: (社員04, 社員05)")
    print("  2人組C: (社員06, 社員07)")
    print()

    data = Input(
        proposer_prefs=[
            # 3人組: 全員 第1課 を第1志望
            [1,2,3,4],   # 社員01: 第1課 > 第2課 > 第3課 > 第4課
            [1,2,3,4],   # 社員02: 第1課 > 第2課 > 第3課 > 第4課  ← 01と同課不可
            [1,3,2,4],   # 社員03: 第1課 > 第3課 > 第2課 > 第4課  ← 01,02と同課不可
            # 2人組B: 全員 第2課 を第1志望
            [2,1,3,4],   # 社員04: 第2課 > 第1課 > 第3課 > 第4課
            [2,3,1,4],   # 社員05: 第2課 > 第3課 > 第1課 > 第4課  ← 04と同課不可
            # 2人組C: 全員 第3課 を第1志望
            [3,1,2,4],   # 社員06: 第3課 > 第1課 > 第2課 > 第4課
            [3,4,1,2],   # 社員07: 第3課 > 第4課 > 第1課 > 第2課  ← 06と同課不可
            # その他 11名
            [1,2,3,4],   # 社員08: 第1課 > ...
            [1,2,3,4],   # 社員09: 第1課 > ...
            [2,1,3,4],   # 社員10: 第2課 > ...
            [2,3,1,4],   # 社員11: 第2課 > ...
            [2,1,3,4],   # 社員12: 第2課 > ...
            [3,2,1,4],   # 社員13: 第3課 > ...
            [3,1,2,4],   # 社員14: 第3課 > ...
            [3,2,1,4],   # 社員15: 第3課 > ...
            [4,1,2,3],   # 社員16: 第4課 > ...
            [4,2,1,3],   # 社員17: 第4課 > ...
            [4,1,3,2],   # 社員18: 第4課 > ...
        ],
        receiver_prefs=[
            # 第1課(定員5): 社員01>08>09が上位, 社員02・03は最下位
            [1,8,9,4,5,6,7,10,11,12,13,14,15,16,17,18,2,3],
            # 第2課(定員6): 社員04>10>11>12が上位, 社員05は最下位
            [4,10,11,12,1,2,3,8,9,6,7,13,14,15,16,17,18,5],
            # 第3課(定員5): 社員06>13>14>15が上位, 社員05・07は最下位
            [6,13,14,15,1,2,3,4,8,9,10,11,12,16,17,18,5,7],
            # 第4課(定員3): 社員16>17>18が上位, 社員07は最下位
            [16,17,18,1,2,3,4,5,6,8,9,10,11,12,13,14,15,7],
        ],
        constraints=[
            combined_constraint(5, conflict_pairs),  # 第1課: 定員5 ∧ 回避制約
            combined_constraint(6, conflict_pairs),  # 第2課: 定員6 ∧ 回避制約
            combined_constraint(5, conflict_pairs),  # 第3課: 定員5 ∧ 回避制約
            combined_constraint(3, conflict_pairs),  # 第4課: 定員3 ∧ 回避制約
        ],
        proposer_names=[f"社員{i+1:02d}" for i in range(18)],
        receiver_names=["第1課","第2課","第3課","第4課"],
    )

    result = cutoff_adjustment(data, verbose=verbose)

    print("─" * 65)
    print("【性質の検証】capacities = [5, 6, 5, 3]（数値定員ベース）")
    print("─" * 65)
    check_individual_rationality(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_stability(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        capacities=[5, 6, 5, 3],
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_weak_stability(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        capacities=[5, 6, 5, 3],
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )
    check_fairness(
        data.proposer_prefs, data.receiver_prefs,
        result.proposer_match, result.receiver_match,
        proposer_names=data.proposer_names,
        receiver_names=data.receiver_names,
    )

    print()
    print("【解説】社員05 の配属経路")
    print("  第1志望 第2課: 社員04 との回避制約で入れない（カットオフで除外）")
    print("  第2志望 第3課: 競争率が高くカットオフで除外")
    print("  第3志望 第1課: 配属決定 ← 第3志望での配属")
    print()
    print("  第2課: 定員6に対して5人 → 空き定員あり")
    print("  数値定員ベースでは (社員05, 第2課) はブロッキングペア → 安定性❌")
    print("  しかし {社員04, 社員05} は回避制約違反 → 追加は実行不可")
    print("  第2課 の社員05 優先順位: 最下位（18位） → 正当な羨望なし → 公平性✅")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# 例6: 稼働量制約 ∧ 課レベル回避制約（ca_algorithm_custom.py を使用）
# ─────────────────────────────────────────────────────────────────────────────

def example6(verbose=True):
    """
    例6: 稼働量制約 ∧ 課レベル回避制約によるマッチング

    【問題設定】
    ある部門で新プロジェクトへの担当割り当てを行う。部には4課あり、
    各課は1〜3つの担当製品を持つ。応募者（30名）は希望製品と
    各製品への可能稼働量を提出する。以下の2制約を同時に満たす必要がある。

      ① 稼働量上限制約（CA ループで処理）:
           各製品の割当稼働量合計 ≤ 製品の最大受入稼働量
      ② 課レベル回避制約（CA ループで処理）:
           3組の禁止ペアは同一課内のどの製品にも同時に配属されない
      ③ 稼働量カバレッジ制約（後処理チェック）:
           各製品の割当稼働量合計 ≥ 必要稼働量  ← 下限制約のため CA 外

    【組織構造】
      第1課: 製品A（必要 10 / 上限 18）
      第2課: 製品B（必要  8 / 上限 14）、製品C（必要  6 / 上限 12）
      第3課: 製品D（必要 12 / 上限 20）、製品E（必要  5 / 上限 10）、製品F（必要  7 / 上限 14）
      第4課: 製品G（必要  9 / 上限 16）、製品H（必要  4 / 上限  8）

    【禁止ペア（課内共存禁止）の設計意図】
      ペア1 (応募者01, 応募者02): 同課の別製品に第1希望が割れているケース
          → 応募者01: 第1希望=製品A（第1課）、応募者02: 第1希望=製品A（第1課）
          → 初期カットオフで同一製品に需要が発生 → 課レベルでペア検出 → カットオフ調整
      ペア2 (応募者11, 応募者12): 同課内の異なる製品に需要が発生するケース
          → 応募者11: 第1希望=製品B（第2課）、応募者12: 第1希望=製品C（第2課）
          → 単一製品内にはペアが共存しないが課レベルでは共存 → 既存 CA では検出不可
      ペア3 (応募者21, 応募者22): 第3課の製品D・製品Fに分かれるケース
    """
    print("=" * 70)
    print("例6: 稼働量制約 ∧ 課レベル回避制約によるマッチング")
    print("=" * 70)
    print()

    # ─── 応募者名 ────────────────────────────────────────────────────────────
    proposer_names = [f"応募者{i+1:02d}" for i in range(30)]

    # ─── 課・製品の定義 ─────────────────────────────────────────────────────
    #   製品インデックス（0-indexed）:
    #     0=製品A  第1課
    #     1=製品B  第2課
    #     2=製品C  第2課
    #     3=製品D  第3課
    #     4=製品E  第3課
    #     5=製品F  第3課
    #     6=製品G  第4課
    #     7=製品H  第4課
    department_names = ["第1課", "第2課", "第3課", "第4課"]
    product_names    = ["製品A", "製品B", "製品C", "製品D", "製品E", "製品F", "製品G", "製品H"]
    department_of    = [0, 1, 1, 2, 2, 2, 3, 3]   # 各製品が属する課（0-indexed）
    workload_required = [10,  8,  6, 12,  5,  7,  9,  4]
    #                    A    B   C   D    E   F   G   H
    # G: 応募者21 がフォールバックで流れ込む (wl=3) ため上限を広めに設定
    # H: 応募者08 がフォールバックで流れ込む (wl=2) ため上限を広めに設定
    workload_max      = [18, 14, 12, 22, 12, 16, 22, 10]

    # ─── 禁止ペア（0-indexed 応募者番号）────────────────────────────────────
    # ペア1: 応募者01(0) と 応募者02(1)  → ともに製品A(第1課)を第1希望 → 同製品内衝突
    # ペア2: 応募者11(10) と 応募者12(11) → 製品B・製品Cにそれぞれ第1希望 → 課内クロスプロダクト衝突
    # ペア3: 応募者21(20) と 応募者22(21) → 製品D・製品Fにそれぞれ第1希望 → 課内クロスプロダクト衝突
    conflict_pairs = [(0, 1), (10, 11), (20, 21)]

    # ─── 選好リストと可能稼働量 ─────────────────────────────────────────────
    # 設計原則:
    #   ① proposer_prefs には、可能稼働量（wl≥1）を提出した製品のみ列挙する
    #   ② ブロック後のフォールバック先は必ず異なる課とする
    #   ③ workload_max は、フォールバック先に複数が流れ込んでも溢れない値に設定
    #
    # 製品インデックス（0-indexed）: A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7
    # 課インデックス（0-indexed）:   第1課=0, 第2課=1, 第3課=2, 第4課=3
    proposer_prefs: list[list[int]] = []
    workload_available: dict[tuple[int, int], int] = {}

    # ── 第1課 希望グループ: 応募者01〜08（8名） ──────────────────────────
    # 全員が製品A を第1希望。定員オーバーで第2希望に溢れる。
    # 禁止ペア1: 応募者01・02 がともに製品A を第1希望 → 低優先(02)をブロック → 応募者02は製品E(第3課)へ

    proposer_prefs.append([1, 7])          # 応募者01: 製品A > 製品G    ← ペア1 高優先
    workload_available[(0, 0)] = 4         # 製品A: 4
    workload_available[(0, 6)] = 2         # 製品G: 2（フォールバック）

    proposer_prefs.append([1, 5])          # 応募者02: 製品A > 製品E    ← ペア1 低優先（Aブロック→E=第3課）
    workload_available[(1, 0)] = 3         # 製品A: 3
    workload_available[(1, 4)] = 3         # 製品E: 3

    proposer_prefs.append([1, 2])          # 応募者03: 製品A > 製品B
    workload_available[(2, 0)] = 5         # 製品A: 5
    workload_available[(2, 1)] = 3         # 製品B: 3

    proposer_prefs.append([1, 4])          # 応募者04: 製品A > 製品D
    workload_available[(3, 0)] = 4         # 製品A: 4
    workload_available[(3, 3)] = 3         # 製品D: 3

    proposer_prefs.append([1, 5])          # 応募者05: 製品A > 製品E
    workload_available[(4, 0)] = 3         # 製品A: 3
    workload_available[(4, 4)] = 2         # 製品E: 2

    proposer_prefs.append([1, 6])          # 応募者06: 製品A > 製品F
    workload_available[(5, 0)] = 2         # 製品A: 2
    workload_available[(5, 5)] = 4         # 製品F: 4

    proposer_prefs.append([1, 3])          # 応募者07: 製品A > 製品C
    workload_available[(6, 0)] = 2         # 製品A: 2
    workload_available[(6, 2)] = 3         # 製品C: 3

    proposer_prefs.append([1, 8])          # 応募者08: 製品A > 製品H
    workload_available[(7, 0)] = 2         # 製品A: 2
    workload_available[(7, 7)] = 2         # 製品H: 2

    # ── 第2課 希望グループ: 応募者09〜16（8名） ──────────────────────────
    # 禁止ペア2: 応募者11(10) → 製品B(第2課) 第1希望
    #           応募者12(11) → 製品C(第2課) 第1希望
    # → 同一課の別製品に初期需要が発生 → 課レベル衝突検出 → 低優先(11)ブロック → 応募者11は製品D(第3課)へ

    proposer_prefs.append([2, 1])          # 応募者09: 製品B > 製品A
    workload_available[(8, 1)] = 4         # 製品B: 4
    workload_available[(8, 0)] = 2         # 製品A: 2

    proposer_prefs.append([2, 3])          # 応募者10: 製品B > 製品C
    workload_available[(9, 1)] = 5         # 製品B: 5
    workload_available[(9, 2)] = 3         # 製品C: 3

    proposer_prefs.append([2, 4])          # 応募者11: 製品B > 製品D   ← ペア2 一方（Bブロック→D=第3課）
    workload_available[(10, 1)] = 4        # 製品B: 4
    workload_available[(10, 3)] = 3        # 製品D: 3

    proposer_prefs.append([3, 2])          # 応募者12: 製品C > 製品B   ← ペア2 もう一方（Cに留まる）
    workload_available[(11, 2)] = 5        # 製品C: 5
    workload_available[(11, 1)] = 2        # 製品B: 2

    proposer_prefs.append([3, 2])          # 応募者13: 製品C > 製品B
    workload_available[(12, 2)] = 4        # 製品C: 4
    workload_available[(12, 1)] = 2        # 製品B: 2

    proposer_prefs.append([2, 3])          # 応募者14: 製品B > 製品C
    workload_available[(13, 1)] = 3        # 製品B: 3
    workload_available[(13, 2)] = 3        # 製品C: 3

    proposer_prefs.append([3, 6])          # 応募者15: 製品C > 製品F
    workload_available[(14, 2)] = 3        # 製品C: 3
    workload_available[(14, 5)] = 3        # 製品F: 3

    proposer_prefs.append([2, 3])          # 応募者16: 製品B > 製品C
    workload_available[(15, 1)] = 2        # 製品B: 2
    workload_available[(15, 2)] = 2        # 製品C: 2

    # ── 第3課 希望グループ: 応募者17〜25（9名） ──────────────────────────
    # 禁止ペア3: 応募者21(20) → 製品D(第3課) 第1希望
    #           応募者22(21) → 製品F(第3課) 第1希望
    # → 同一課の別製品に初期需要が発生 → 課レベル衝突検出 → 低優先(21)ブロック → 応募者21は製品G(第4課)へ

    proposer_prefs.append([4, 3])          # 応募者17: 製品D > 製品C
    workload_available[(16, 3)] = 4        # 製品D: 4
    workload_available[(16, 2)] = 2        # 製品C: 2

    proposer_prefs.append([4, 5])          # 応募者18: 製品D > 製品E
    workload_available[(17, 3)] = 5        # 製品D: 5
    workload_available[(17, 4)] = 3        # 製品E: 3

    proposer_prefs.append([5, 4])          # 応募者19: 製品E > 製品D
    workload_available[(18, 4)] = 4        # 製品E: 4
    workload_available[(18, 3)] = 2        # 製品D: 2

    proposer_prefs.append([5, 6])          # 応募者20: 製品E > 製品F
    workload_available[(19, 4)] = 3        # 製品E: 3
    workload_available[(19, 5)] = 3        # 製品F: 3

    proposer_prefs.append([4, 7])          # 応募者21: 製品D > 製品G   ← ペア3 一方（Dブロック→G=第4課）
    workload_available[(20, 3)] = 5        # 製品D: 5
    workload_available[(20, 6)] = 3        # 製品G: 3（フォールバック先を第4課に設定）

    proposer_prefs.append([6, 4])          # 応募者22: 製品F > 製品D   ← ペア3 もう一方（Fに留まる）
    workload_available[(21, 5)] = 5        # 製品F: 5
    workload_available[(21, 3)] = 3        # 製品D: 3

    proposer_prefs.append([6, 5])          # 応募者23: 製品F > 製品E
    workload_available[(22, 5)] = 4        # 製品F: 4
    workload_available[(22, 4)] = 3        # 製品E: 3

    proposer_prefs.append([4, 6])          # 応募者24: 製品D > 製品F
    workload_available[(23, 3)] = 4        # 製品D: 4
    workload_available[(23, 5)] = 3        # 製品F: 3

    proposer_prefs.append([4, 5])          # 応募者25: 製品D > 製品E
    workload_available[(24, 3)] = 3        # 製品D: 3
    workload_available[(24, 4)] = 2        # 製品E: 2

    # ── 第4課 希望グループ: 応募者26〜30（5名） ──────────────────────────
    # 応募者21 のフォールバック先が製品G(第4課)のため、G の workload_max を広めに設定
    proposer_prefs.append([7, 4])          # 応募者26: 製品G > 製品D
    workload_available[(25, 6)] = 5        # 製品G: 5
    workload_available[(25, 3)] = 3        # 製品D: 3

    proposer_prefs.append([7, 8])          # 応募者27: 製品G > 製品H
    workload_available[(26, 6)] = 4        # 製品G: 4
    workload_available[(26, 7)] = 3        # 製品H: 3

    proposer_prefs.append([8, 7])          # 応募者28: 製品H > 製品G
    workload_available[(27, 7)] = 4        # 製品H: 4
    workload_available[(27, 6)] = 3        # 製品G: 3

    proposer_prefs.append([7, 6])          # 応募者29: 製品G > 製品F
    workload_available[(28, 6)] = 4        # 製品G: 4
    workload_available[(28, 5)] = 2        # 製品F: 2

    proposer_prefs.append([8, 7])          # 応募者30: 製品H > 製品G
    workload_available[(29, 7)] = 3        # 製品H: 3
    workload_available[(29, 6)] = 2        # 製品G: 2

    # ─── 製品の優先順位（稼働量が高い応募者を優先） ─────────────────────────
    # 稼働量を提出した応募者のみを優先順位リストに含める（wl=0 の応募者は除外）
    def build_product_prefs(
        n_products: int,
        n_proposers: int,
        workload_available: dict[tuple[int, int], int],
    ) -> list[list[int]]:
        prefs = []
        for j in range(n_products):
            # wl > 0 の応募者のみを稼働量降順で並べる（1-indexed）
            ranked = sorted(
                [p for p in range(n_proposers) if workload_available.get((p, j), 0) > 0],
                key=lambda p: -workload_available[(p, j)],
            )
            prefs.append([p + 1 for p in ranked])
        return prefs

    product_prefs = build_product_prefs(8, 30, workload_available)

    # ─── WorkloadInput を構築して実行 ────────────────────────────────────────
    data = WorkloadInput(
        proposer_prefs=proposer_prefs,
        product_prefs=product_prefs,
        workload_available=workload_available,
        workload_required=workload_required,
        workload_max=workload_max,
        department_of=department_of,
        conflict_pairs=conflict_pairs,
        department_names=department_names,
        product_names=product_names,
        proposer_names=proposer_names,
    )

    result = cutoff_adjustment_workload(data, verbose=verbose)

    # ─── 解説 ────────────────────────────────────────────────────────────────
    print("【解説: 禁止ペアの処理経路】")

    p01, p02 = 0, 1  # ペア1
    p11, p12 = 10, 11  # ペア2
    p21, p22 = 20, 21  # ペア3

    for label, a, b in [("ペア1", p01, p02), ("ペア2", p11, p12), ("ペア3", p21, p22)]:
        ja = result.proposer_match[a]
        jb = result.proposer_match[b]
        da = data.department_of[ja] if ja != -1 else -1
        db = data.department_of[jb] if jb != -1 else -1
        pref_a = data.r_name(data.proposer_prefs[a][0] - 1)
        pref_b = data.r_name(data.proposer_prefs[b][0] - 1)
        final_a = data.r_name(ja) if ja != -1 else "未配分"
        final_b = data.r_name(jb) if jb != -1 else "未配分"
        print(f"  {label}: ({data.p_name(a)}, {data.p_name(b)})")
        print(f"    第1希望: {pref_a} / {pref_b}")
        print(f"    最終配属: {final_a}({data.d_name(da) if da!=-1 else '-'}) / "
              f"{final_b}({data.d_name(db) if db!=-1 else '-'})")
    print()


if __name__ == "__main__":
    example1()
    print("\n\n")
    example2()
    print("\n\n")
    example3()
    print("\n\n")
    example4()
    print("\n\n")
    example5()
    print("\n\n")
    example6()
