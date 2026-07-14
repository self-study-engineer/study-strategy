import numpy as np
from scipy.stats import binom
import matplotlib.pyplot as plt

def condorcet_jury_theorem(p, max_n=101):
    """
    コンドルセの陪審定理の計算
    p: 各個人の正解確率 (0.5 < p <= 1.0)
    max_n: 最大の人数（奇数）
    """
    results = []
    # 奇数人数でシミュレーション
    n_values = range(1, max_n + 1, 2)
    
    for n in n_values:
        # 多数決で正解する最小人数 (n/2 を超える最小の整数)
        threshold = n // 2 + 1
        
        # 2項分布の累積分布関数を使用して、
        # threshold人以上が正解する確率を計算
        # 1 - binom.cdf(k, n, p) は、k以下の確率を引くので、
        # 0からk人まで(k人未満)の確率を引く
        prob_majority_correct = 1 - binom.cdf(threshold - 1, n, p)
        results.append(prob_majority_correct)
        
    return list(n_values), results

# --- 設定 ---
individual_p = 0.53  # 個人の正解確率が0.55の場合
max_n = 101
n_values, jury_probs = condorcet_jury_theorem(individual_p, max_n)

# --- 結果の表示 ---
print(f"個人の正解確率: {individual_p}")
print(f"人数 | 多数決の正解確率")
print("-" * 25)
for n, prob in zip(n_values[:10], jury_probs[:10]):
    print(f"{n:4d} | {prob:.4f}")
print("...")

# --- グラフ描画 ---
filepath = f"./{individual_p}_{max_n}.png";
plt.figure(figsize=(8, 5))
plt.plot(n_values, jury_probs, marker='o', linestyle='-', label=f'p={individual_p}')
plt.axhline(y=1, color='r', linestyle='--')
plt.axhline(y=0.5, color='gray', linestyle='-')
plt.title("Condorcet's Jury Theorem")
plt.xlabel("Number of Jury Members (n)")
plt.ylabel("Probability of Correct Decision")
plt.grid(True)
plt.legend()
plt.savefig(filepath)
print(filepath)