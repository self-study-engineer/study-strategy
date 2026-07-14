import statistics

def input_data():
    N = 3
    a = [1, 2, 3]  # 異質なプレーヤー
    return N, a

def calculate_cost_share(N):
    return [1 / N] * N

def calculate_reported_supply(N, a, q):
    x = [0] * N
    for i in range(N):
        x[i] = (1 - q[i]) / a[i]
    return x

def determine_public_good(x):
    return statistics.median(x)

def calculate_payoff(N, a, G, q):
    payoff = [0] * N
    for i in range(N):
        payoff[i] = G - 0.5 * a[i] * G**2 - q[i] * G
    return payoff

# =========================
# 出力（main）
# =========================
def main():
    print('ボーエン・メカニズム\n')

    # 1. 入力データ取得
    N, a = input_data()

    # 2. 費用負担割合の決定
    q = calculate_cost_share(N)

    # 3. 表明供給水準の計算
    x = calculate_reported_supply(N, a, q)

    # 4. 公共財供給水準（中央値）の決定
    G = determine_public_good(x)

    # 5. 利得の計算
    payoff = calculate_payoff(N, a, G, q)

    # 6. 結果出力
    for i in range(N):
        print(f'プレーヤー {i+1} の費用負担割合 = {q[i]}')
    print()
    for i in range(N):
        print(f'プレーヤー {i+1} の表明する公共財供給水準 = {x[i]}')
    print()
    print(f'公共財供給水準 = {G}\n')
    for i in range(N):
        print(f'プレーヤー {i+1} の利得 = {payoff[i]}')

if __name__ == "__main__":
    main()