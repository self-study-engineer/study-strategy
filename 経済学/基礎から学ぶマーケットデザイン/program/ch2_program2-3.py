import numpy as np

def input_data():
    N = 3
    a = [1, 1, 1]
    Q = 1
    return N, a, Q

def calculate_cost_share(N, Q):
    return [Q / N] * N

def solve_linear_system(q):
    A = np.array([
        [1, 0, 2],
        [2, 1, 0],
        [0, 2, 1]
    ])

    B = np.array([
        [1.0 - q[0]],
        [1.0 - q[1]],
        [1.0 - q[2]]
    ])

    s = np.linalg.solve(A, B)
    return [s[i, 0] for i in range(len(q))]

def determine_public_good(x):
    return sum(x)

def calculate_additional_tax(N, x):
    t = [0] * N
    for i in range(N):
        left = (i + 1) % N
        right = (i - 1) % N
        t[i] = x[right] - x[left]
    return t

def calculate_payoff(N, a, G, q, t):
    payoff = [0] * N
    for i in range(N):
        payoff[i] = G - 0.5 * a[i] * G**2 - (q[i] + t[i]) * G
    return payoff

# =========================
# 出力（main）
# =========================
def main():
    print('ウォーカー・メカニズム\n')

    # 1. 入力データ取得
    N, a, Q = input_data()

    # 2. 基本費用負担の決定
    q = calculate_cost_share(N, Q)

    # 3. 連立方程式を解いて均衡需要を取得
    x = solve_linear_system(q)

    # 4. 公共財供給水準の決定
    G = determine_public_good(x)

    # 5. 追加費用負担の計算
    t = calculate_additional_tax(N, x)

    # 6. 利得の計算
    payoff = calculate_payoff(N, a, G, q, t)

    # 7. 結果出力
    for i in range(N):
        print(f'プレーヤー {i+1} の費用負担割合 = {q[i]}')
    print()
    for i in range(N):
        print(f'プレーヤー {i+1} の表明する公共財追加需要 = {x[i]}')
    print()
    print(f'公共財供給水準 = {G}\n')
    for i in range(N):
        print(f'プレーヤー {i+1} の追加費用負担割合 = {t[i]}')
    print()
    for i in range(N):
        print(f'プレーヤー {i+1} の利得 = {payoff[i]}')


if __name__ == "__main__":
    main()