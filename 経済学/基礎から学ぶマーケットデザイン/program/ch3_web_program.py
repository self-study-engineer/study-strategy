# Discriminative price and uniform-price auctions

# プレーヤーの数
N = 2

# 財の数
M = 2

# 評価値　各行に各プレーヤーの1つ目の財，2つ目の財，……に対する評価値
value = [
    [80,40],
    [65,30]
    ]
for i in range(N):
    print('プレーヤー',i+1,'の評価値: ', end='')
    for j in range(M):
        print(' ',value[i][j],end='')
    print()

print()
# 入札価格　各行に各プレーヤーの1つ目の財，2つ目の財，……に対する入札価格
bid = [
       [80,40],
       [65,30]
       ]
for i in range(N):
    print('プレーヤー',i+1,'の入札価格: ', end='')
    for j in range(M):
        print(' ',bid[i][j],end='')
    print()

print()
# すべてのプレーヤーの入札価格を1つのベクトルにまとめる
b = [0]*(N*M)
b_index = [0]*(N*M)
for i in range(N):
    for j in range(M):
        b[i*M+j] = bid[i][j]
        b_index[i*M+j] = i

# 入札価格を降順に並べ替える（バブル・ソート）
for i in range(N*M):
    for j in range(N*M-1,i,-1):
        if b[j] > b[j-1]:
            b[j], b[j-1] = b[j-1], b[j]
            b_index[j], b_index[j-1] = b_index[j-1], b_index[j]


# 落札者と支払い額の決定
# 差別価格オークションの場合
print('差別価格オークション:')
for j in range(M):
    print(j+1,'位の落札者: プレーヤー',b_index[j]+1,' 支払額 = ',b[j])

print()
# 一様価格オークションの場合
print('一様価格オークション:')
for j in range(M):
    print(j+1,'位の落札者: プレーヤー',b_index[j]+1,' 支払額 = ',b[M])
