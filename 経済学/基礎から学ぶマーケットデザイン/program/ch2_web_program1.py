def input_data():
    N = 15                      # プレーヤー数
    w = [N] * N                 # 各プレーヤーの初期保有（全員同一）
    x = [i for i in range(N)]   # 貢献額（例：0,1,2,...,N-1）
    a = 0.6                     # 限界便益
    return N, w, x, a

def calculate_public_good(x):
    G = sum(x)
    return G

def calculate_payoff(N, w, x, a, G):
    payoff = [0] * N
    for i in range(N):
        payoff[i] = w[i] - x[i] + a * G
    return payoff

# =========================
# main
# =========================
def main():
    print('公共財自発的供給メカニズム\n')

    # 1. 入力データ取得
    N, w, x, a = input_data()

    # 2. 貢献額の表示
    for i in range(N):
        print(f'プレーヤー {i+1} の貢献額 = {x[i]}')
    print()

    # 3. 公共財供給水準の計算
    G = calculate_public_good(x)

    # 4. 利得の計算
    payoff = calculate_payoff(N, w, x, a, G)

    # 5. 結果の出力
    print(f'公共財供給水準 = {G}')
    print(f'1人あたりの便益 = {G / N}\n')
    for i in range(N):
        print(f'プレーヤー {i+1} の利得 = {payoff[i]}')

if __name__ == "__main__":
    main()