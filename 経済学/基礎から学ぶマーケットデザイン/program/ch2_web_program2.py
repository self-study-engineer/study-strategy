def input_data():
    N = 10
    a = [i + 1 for i in range(N)]  # a_i = i+1
    return N, a

def calculate_public_good(N, a):
    return (N - 1) / sum(a)


def calculate_cost_share(N, a, G):
    q = [0] * N
    for i in range(N):
        q[i] = 1 - a[i] * G
    return q


def calculate_payoff(N, a, G, q):
    payoff = [0] * N
    for i in range(N):
        payoff[i] = G - 0.5 * a[i] * G**2 - q[i] * G
    return payoff

# =========================
# 出力（main）
# =========================
def main():
    print('リンダール・メカニズム\n')

    # 1. 入力データ取得
    N, a = input_data()

    # 2. 公共財供給水準の計算
    G = calculate_public_good(N, a)

    # 3. 費用負担割合の計算
    q = calculate_cost_share(N, a, G)

    # 4. 利得の計算
    payoff = calculate_payoff(N, a, G, q)

    # 5. 結果出力
    print(f'公共財供給水準 = {G}\n')
    for i in range(N):
        print(f'プレーヤー {i+1} の費用負担割合 = {q[i]}')
    print()
    for i in range(N):
        print(f'プレーヤー {i+1} の利得 = {payoff[i]}')

if __name__ == "__main__":
    main()