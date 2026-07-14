# Kth-price private value auction

import random

# プレーヤーの数
N = 5

# 落札者はK位の価格を支払う
K = 2
print(K,'位価格オークションの場合')
print()

# 評価値
value = [0]*N
for i in range(N):
    value[i] = random.random() # 区間[0, 1]上の一様分布
    print('プレーヤー',i+1,'の評価値 = ',value[i])
print()

# 入札価格
bid = [0]*N
for i in range(N):
    bid[i] = value[i]*(N-1)/(N-K+1)
    print('プレーヤー',i+1,'の入札価格 = ',bid[i])

print()
# 落札者の出力
winbid = max(bid) # 最高の入札価格
winner = bid.index(winbid) # 最高額を入札したプレーヤー
print('落札者:　',winner+1)    

# 落札者の入札価格と落札価格
print('落札者の入札価格 = ',bid[winner])
sorted_bid = sorted(bid,reverse=True) # 入札価格を昇順に並べ替え
winbid = sorted_bid[K-1]
print('落札価格 = ',winbid)
