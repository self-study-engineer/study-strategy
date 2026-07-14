# Keyword auction

import copy
 
# 企業の数
N = 3

# 広告枠の数
M = 2

# 各広告枠の平均クリック数
click = [100,90]

# 各企業の1クリック当たりの広告の評価値
value = [600,300,100]
for i in range(N):
    print('プレーヤー',i+1,'の評価値: ', value[i])

print()
# 各プレーヤーの入札価格
bid = [600,300,100]
b_index = [0]*N
for i in range(N):
    print('プレーヤー',i+1,'の入札価格: ', bid[i])
    b_index[i] = i # 各入札価格に対するプレーヤー番号の記録
print()

# 入札価格を降順に並べ替える（バブルソート）
for i in range(N):
    for j in range(N-1,i,-1):
        if bid[j] > bid[j-1]:
            bid[j], bid[j-1] = bid[j-1], bid[j]
            b_index[j], b_index[j-1] = b_index[j-1], b_index[j]

# 落札者と支払い額の決定
# 一般化された二位価格オークションの場合
print('一般化された二位価格オークション:')
for j in range(M):
    print(j+1,'位の落札者: プレーヤー',b_index[j]+1,' 支払額 = ',bid[j+1]*click[j],end='')
    print('　利得 = ',(value[b_index[j]]-bid[j+1])*click[j])

print()
# VCGオークションの場合
print('VCGオークション:')

# jが参加した時のj以外の便益の和
sum1 = [0]*N
for j in range(M):
    for k in range(M):
        if k != j:
            sum1[j] += value[b_index[k]]*click[k]

# jが参加しない時のj以外の便益の和
b_ind = [0]*N
sum2 = [0]*N
for j in range(M):
    # 入札者リストのコピー
    b_ind = copy.copy(b_index)
    # j番目のプレーヤーを入札者のリストから除く
    del b_ind[j]
    for k in range(M):
        sum2[j] += value[b_ind[k]]*click[k]

# 結果表示
payment = [0]*N
for j in range(M):
    payment[j] = sum2[j]-sum1[j]
    print(j+1,'位の落札者: プレーヤー',b_index[j]+1,' 支払額 = ',payment[j],end='')
    print('　利得 = ',(value[b_index[j]])*click[j]-payment[j])
