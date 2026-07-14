def input_data():
    N = 3
    x = [2, 2, 2]
    v = [3, 1, -2]  # 真の便益
    w = [3, 1, -2]  # 表明（ここでは真実報告を仮定）
    return N, x, v, w

def determine_public_good(w):
    return 1 if sum(w) >= 0 else 0

def calculate_clarke_tax(N, w):
    total = sum(w)
    t = [0] * N

    for i in range(N):
        sum_i = total - w[i]
        if total * sum_i < 0:
            t[i] = abs(sum_i)
        else:
            t[i] = 0

    return t

def calculate_payoff(N, x, v, G, t):
    payoff = [0] * N
    for i in range(N):
        payoff[i] = x[i] + v[i] * G - t[i]
    return payoff

# =========================
# 出力（main）
# =========================
def main():
    print('ピボタル・メカニズム\n')

    # 1. 入力データ取得
    N, x, v, w = input_data()

    # 2. 便益（真・表明）の表示
    for i in range(N):
        print(f'プレーヤー {i+1} の公共財に対する真の便益 = {v[i]}')
    print()
    for i in range(N):
        print(f'プレーヤー {i+1} の表明する公共財の便益 = {w[i]}')
    print()

    # 3. 公共財供給の決定
    G = determine_public_good(w)

    # 4. クラーク税の計算
    t = calculate_clarke_tax(N, w)

    # 5. 利得の計算
    payoff = calculate_payoff(N, x, v, G, t)

    # 6. 結果出力
    print(f'公共財供給水準 = {G}\n')
    for i in range(N):
        print(f'プレーヤー {i+1} のクラーク税 = {t[i]}')
    print()
    for i in range(N):
        print(f'プレーヤー {i+1} の利得 = {payoff[i]}')

if __name__ == "__main__":
    main()