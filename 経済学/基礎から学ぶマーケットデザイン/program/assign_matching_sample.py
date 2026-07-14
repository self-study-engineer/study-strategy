from dataclasses import dataclass

@dataclass
class MatchingData:
    s_pref: list[list[int]]
    c_pref: list[list[int]]
    capacity: list[int]

    @property
    def S(self) -> int:
        return len(self.s_pref)

    @property
    def C(self) -> int:
        return len(self.c_pref)


def print_preferences(data: MatchingData) -> None:
    print('学生の選好')
    for i, pref in enumerate(data.s_pref):
        print(f's{i+1}:', end=' ')
        print(' '.join(f'c{x}' for x in pref))
    print()
    print('研究室の選好')
    for i, pref in enumerate(data.c_pref):
        print(f'c{i+1}:', end=' ')
        print(' '.join(f's{x}' for x in pref))
    print()
    print('研究室の定員')
    for i, cap in enumerate(data.capacity):
        print(f'c{i+1}: {cap}')
    print()


def build_order_table(
    pref: list[list[int]],
    target_size: int,
) -> list[list[int]]:
    order = [[0] * target_size for _ in range(len(pref))]
    for i, row in enumerate(pref):
        for rank, target in enumerate(row):
            order[i][target - 1] = rank

    return order


def print_matching_result(
    s_matched: list[int],
) -> None:

    print('マッチング結果')
    for i, c in enumerate(s_matched):
        if c == -1:
            print(f's{i+1}:')
        else:
            print(f's{i+1}: c{c+1}')
    print()


def find_worst_student(
    lab: int,
    candidates: list[int],
    c_order: list[list[int]],
) -> int:
    worst_student = candidates[0]
    worst_rank = c_order[lab][worst_student]

    for student in candidates[1:]:
        rank = c_order[lab][student]
        if rank > worst_rank:
            worst_rank = rank
            worst_student = student

    return worst_student


# =========================================
# 即時受入方式
# =========================================

def immediate_acceptance(
    data: MatchingData,
) -> list[int]:
    print('即時受入方式')
    print()

    S = data.S
    C = data.C
    c_order = build_order_table(data.c_pref, S)
    s_matched = [-1] * S

    # 学生が次に応募する志望順位
    next_choice = [0] * S

    # 研究室ごとの確定学生
    c_matched: list[list[int]] = [[] for _ in range(C)]
    unmatched: set[int] = set(range(S))
    step = 1

    while unmatched:
        print(f'ステップ {step}')
        current_proposals: dict[int, list[int]] = {}

        # =====================================
        # proposal
        # =====================================
        for student in list(unmatched):
            # 全研究室へ応募済み
            if next_choice[student] >= C:
                unmatched.remove(student)
                continue
            lab = (data.s_pref[student][next_choice[student]] - 1)
            print(f's{student+1} が 'f'c{lab+1} にプロポーズ')
            current_proposals.setdefault(lab, []).append(student)
        print()

        # =====================================
        # acceptance
        # =====================================
        for lab, proposers in current_proposals.items():
            # 残席
            remaining_capacity = (data.capacity[lab] - len(c_matched[lab]))

            # 今回応募者のみ比較
            sorted_proposers = sorted(proposers, key=lambda s: c_order[lab][s])
            accepted_this_round = (sorted_proposers[:remaining_capacity])

            # accept
            for student in accepted_this_round:
                c_matched[lab].append(student)
                s_matched[student] = lab
                unmatched.discard(student)
                print(f'  s{student+1} と 'f'c{lab+1} がマッチ')

            # reject
            for student in proposers:
                if student not in accepted_this_round:
                    next_choice[student] += 1
                    print(f'  c{lab+1} が 'f's{student+1} をリジェクト')
                    # 全研究室に応募済み
                    if next_choice[student] >= C:
                        unmatched.discard(student)
            print()
        step += 1

    return s_matched


# =========================================
# 受入保留方式
# =========================================

def deferred_acceptance(
    data: MatchingData,
) -> list[int]:
    print('受入保留方式')
    print()

    S = data.S
    C = data.C
    c_order = build_order_table(data.c_pref, S)
    s_matched = [-1] * S
    next_choice = [0] * S

    # 仮マッチ
    c_matched: list[list[int]] = [[] for _ in range(C)]
    free_students: set[int] = set(range(S))
    step = 1

    while free_students:
        print(f'ステップ {step}')
        student = free_students.pop()

        # 全研究室へ応募済み
        if next_choice[student] >= C:
            print(f's{student+1} は unmatched')
            print()
            step += 1
            continue

        lab = (data.s_pref[student][next_choice[student]]- 1)
        print(f's{student+1} が 'f'c{lab+1} にプロポーズ')

        # 現在の仮マッチ + 新応募
        candidates = (c_matched[lab]+ [student])

        # 定員以内
        if len(candidates) <= data.capacity[lab]:
            c_matched[lab].append(student)
            s_matched[student] = lab
            print(f'  s{student+1} と 'f'c{lab+1} が仮マッチ')
        else:
            rejected = find_worst_student(lab, candidates, c_order,)

            # 新応募者が reject
            if rejected == student:
                next_choice[student] += 1
                free_students.add(student)
                print(f'  c{lab+1} が ' f's{student+1} をリジェクト')
            else:
                # 古い学生を追い出す
                c_matched[lab].remove(rejected)
                c_matched[lab].append(student)
                s_matched[student] = lab
                s_matched[rejected] = -1
                next_choice[rejected] += 1
                free_students.add(rejected)
                print(f'  c{lab+1} が 'f's{rejected+1} をリジェクト')
                print(f'  s{student+1} と 'f'c{lab+1} が仮マッチ')
        print()
        step += 1

    return s_matched


# =========================================
# 実行例
# =========================================

if __name__ == "__main__":
    data = MatchingData(
        s_pref=[
            [1, 2, 3],
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ],
        c_pref=[
            [1, 2, 3, 4],
            [2, 3, 4, 1],
            [4, 1, 2, 3],
        ],
        capacity=[1, 1, 2],
    )

    print_preferences(data)

    result = immediate_acceptance(data)
    print_matching_result(result)

    result = deferred_acceptance(data)
    print_matching_result(result)