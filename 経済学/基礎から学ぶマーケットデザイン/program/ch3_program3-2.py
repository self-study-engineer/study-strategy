import random
import numpy as np

# プレーヤーの数
N = 5
print('参加人数 = ',N)

# シミュレーション回数
T = 1000
print('繰り返し回数 = ',T)

winbid1 = [0]*T
winbid2 = [0]*T
winbid3 = [0]*T
for t in range(T):
    value = [0]*N
    # 2位価格オークションでの入札価格
    for i in range(N):
        value[i] = random.random() # 区間[0, 1]上の一様分布
    winbid = max(value) # 最高の評価値
    winner = value.index(winbid) # 最高額を入札したプレーヤー
    # ランダム1位価格オークションでの落札者の評価値
    winrand = random.choice(value) # ランダムに選んだ評価値

    # 1位価格と2位価格オークションでの落札価格
    sorted_bid = sorted(value,reverse=True) # 評価値を昇順に並べ替え
    winbid1[t] = sorted_bid[0]*(N-1)/N # 1位価格での落札価格
    winbid2[t] = sorted_bid[1] # 2位価格での落札価格
    winbid3[t] = winrand*(N-1)/N # ランダム1位価格

print('1位価格オークションでの平均落札価格 = ',np.mean(winbid1))
print('2位価格オークションでの平均落札価格 = ',np.mean(winbid2))
print('ランダム1位価格オークションでの平均落札価格 = ',np.mean(winbid3))
