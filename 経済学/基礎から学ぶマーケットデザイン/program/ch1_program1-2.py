# Majority judgement

import statistics

# 投票者の数
N = 5

# 候補の数
C = 4

# 各候補に対するグレード。上から順に投票者1，投票者2，……が付けたグレード。
# また，左から順に候補1，候補2，……に対するグレード。数値が高いほど得点が高い
value = [
    [7,2,6,3],
    [6,5,1,2],
    [2,3,7,6],
    [1,6,2,5],
    [4,3,1,2]
]

# 各候補に対するグレードの表示
for i in range(N):
    print('投票者',i+1,': ', end='')
    for j in range(C):
        print(value[i][j],' ', end='')
    print()
        
# 候補ごとに与えられたグレードのリスト作成
c_eval = [[0]*N for j in range(C)]
for j in range(C):
    for i in range(N):
        c_eval[j][i]=value[i][j]

# 各候補に対するグレードのメディアンを取得
print('中央値   : ', end='')
median = [0]*C
for i in range(C):
    median[i] = statistics.median(c_eval[i])
    print(median[i],' ', end='')
print()
print()

# 中央値が最大の候補者の集合
winner = [i for i, w in enumerate(median) if w == max(median)]

# 当選者のグレードの中央値
med_win = median[winner[0]]
print('当選者の中央値 = ',med_win)

# 当選者の出力
print('当選者:　',end='')
for i in range(len(winner)):
    print('候補',winner[i]+1,' ',end='')    
print()
