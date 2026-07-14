from dataclasses import dataclass

@dataclass
class MatchingData:
    w_pref: list[list[int]]
    m_pref: list[list[int]]

    @property
    def W(self):
        return len(self.w_pref)

    @property
    def M(self):
        return len(self.m_pref)

def print_preferences(data: MatchingData):
    print('女性の選好')
    for i, prefs in enumerate(data.w_pref):
        print(f'w{i+1}:', end=' ')
        print(' '.join(f'm{x}' for x in prefs))
    print()
    print('男性の選好')
    for i, prefs in enumerate(data.m_pref):
        print(f'm{i+1}:', end=' ')
        print(' '.join(f'w{x}' for x in prefs))
    print()

def build_order_table(pref, target_size):
    """
    pref:
        [[2,1,3], ...]
    
    return:
        左から相手番号に対応した順位表
    """
    order = [[0] * target_size for _ in range(len(pref))]
    for i, row in enumerate(pref):
        for rank, target in enumerate(row):
            order[i][target - 1] = rank

    return order


def print_matching_result(w_matched):
    print('マッチング結果')
    for i, m in enumerate(w_matched):
        if m == -1:
            print(f'w{i+1}: ')
        else:
            print(f'w{i+1}: m{m+1}')
    print()

def priority_matching(data: MatchingData):
    print('順位優先方式')
    print()

    W = data.W
    M = data.M
    w_order = build_order_table(data.w_pref, M)
    m_order = build_order_table(data.m_pref, W)
    w_matched = [-1] * W
    m_matched = [-1] * M

    # 順位和の小さい順
    for score in range(M + W):
        for w in range(W):
            for m in range(M):
                if w_order[w][m] + m_order[m][w] != score:
                    continue
                if w_matched[w] != -1:
                    continue
                if m_matched[m] != -1:
                    continue
                w_matched[w] = m
                m_matched[m] = w
                print(f'w{w+1} と m{m+1} がマッチ 'f'(順位和={score})')
    print()

    return w_matched, m_matched


def deferred_acceptance(data: MatchingData):
    print('受入保留方式')
    print()

    W = data.W
    M = data.M
    m_order = build_order_table(data.m_pref, W)
    w_matched = [-1] * W
    m_matched = [-1] * M
    next_proposal = [0] * W
    free_women = set(range(W))
    step = 1

    while free_women:
        print(f'ステップ {step}')
        woman = free_women.pop()

        # 全員にプロポーズ済み
        if next_proposal[woman] >= M:
            print(f'w{woman+1} は unmatched')
            print()
            step += 1
            continue

        man = data.w_pref[woman][next_proposal[woman]] - 1
        print(f'w{woman+1} が m{man+1} にプロポーズ')
        current = m_matched[man]

        # 空き
        if current == -1:
            w_matched[woman] = man
            m_matched[man] = woman
            print(f'  w{woman+1} と m{man+1} が仮マッチ')

        else:
            # 男性が新しい女性を好む
            if m_order[man][woman] < m_order[man][current]:
                print(f'  m{man+1} が w{current+1} をリジェクト')
                w_matched[current] = -1
                free_women.add(current)
                w_matched[woman] = man
                m_matched[man] = woman
                print(f'  w{woman+1} と m{man+1} が仮マッチ')
            else:
                print(f'  m{man+1} が w{woman+1} をリジェクト')
                next_proposal[woman] += 1
                free_women.add(woman)

        print()
        step += 1

    return w_matched, m_matched


# =========================================
# 実行例
# =========================================

if __name__ == "__main__":
    data = MatchingData(
        w_pref=[
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ],
        m_pref=[
            [2, 3, 1],
            [1, 3, 2],
            [3, 2, 1],
        ]
    )

    print_preferences(data)

    w_match, m_match = priority_matching(data)
    print_matching_result(w_match)

    w_match, m_match = deferred_acceptance(data)
    print_matching_result(w_match)