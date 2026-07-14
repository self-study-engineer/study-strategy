# Borda

# 投票者の数
N = 5

# 候補の数
C = 4

# 各候補に対する得点。上から順に投票者1，投票者2，……が付けた得点。
# また，左から順に候補1，候補2，……に対する得点。数値が高いほど得点が高い
value = [
    [4,1,3,2],
    [4,3,1,2],
    [1,2,4,3],
    [1,4,2,3],
    [4,3,1,2]
]

# 各候補に対する得点の表示
for i in range(N):
    print('投票者',i+1,': ', end='')
    for j in range(C):
        print(value[i][j],' ', end='')
    print()

# 候補ごとに与えられた点数のリスト作成
c_eval = [[0]*N for j in range(C)]
for j in range(C):
    for i in range(N):
        c_eval[j][i]=value[i][j]

# 各候補に対する得点合計を計算
print('得点合計 : ', end='')
point = [0]*C
for i in range(C):
    point[i] = sum(c_eval[i])
    print(point[i],' ', end='')
print()
print()

# 得点合計が最大の候補の集合
winner = [i for i, w in enumerate(point) if w == max(point)]

# 当選者の得点合計
p_win = point[winner[0]]
print('当選者の得点合計 = ',p_win)

# 当選者の出力
print('当選者:　',end='')
for i in range(len(winner)):
    print('候補',winner[i]+1,' ',end='')    
print()
