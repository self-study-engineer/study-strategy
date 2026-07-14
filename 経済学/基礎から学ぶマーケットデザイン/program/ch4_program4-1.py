# Priority matching
print('順位優先方式によるマッチング')
print()

# 女性の数
W=3

# 男性の数
M=3

# 女性の選好
w_pref=[
        [1,2,3],
        [2,3,1],
        [3,1,2]
]
for i in range(W):
    print('女性',i+1,'の希望順位：',end='')
    for j in range(M):
        print(' m{0}'.format(w_pref[i][j]),end='')
    print()
print()

# 女性の希望順位を左からm1の順位，m2の順位，……に変換する
w_order = [[0]*M for i in range(W)]
for i in range(W):
    for j in range(M):
        k = w_pref[i][j]
        w_order[i][k-1] = j+1

# 男性の選好
m_pref=[
        [2,3,1],
        [1,3,2],
        [3,2,1]
]
for i in range(M):
    print('男性',i+1,'の希望順位：',end='')
    for j in range(W):
        print(' w{0}'.format(m_pref[i][j]),end='')
    print()
print()

# 男性の希望順位を左からw1の順位，w2の順位，……に変換する
m_order = [[0]*W for i in range(M)]
for i in range(M):
    for j in range(W):
        k = m_pref[i][j]
        m_order[i][k-1] = j+1
        
# マッチした相手を格納するリスト
w_matched=[0]*W
m_matched=[0]*M
        
# 女性優先で順位和の小さい順にマッチングを決める
for k in range(2,W+M):
    for i in range(W):  
        for j in range(M):
            if w_order[i][j]+m_order[j][i]==k: # 順位和がkの男女の場合
                if w_matched[i]==0 and m_matched[j]==0: # 男女ともまだマッチしていないなら
                    w_matched[i]=j+1
                    m_matched[j]=i+1
                    print('w{0}とm{1}がマッチ: 順位和{2}'.format(i+1,j+1,k))
print()

#　マッチング結果の印字
print('マッチング結果')
for i in range(W):
    if w_matched[i]==0:
        print('w{0}: '.format(i+1))                
    else:
        print('w{0}: m{1}'.format(i+1,w_matched[i]))
                    
for j in range(M):
    if m_matched[j]==0:
        print('    m{0}: '.format(j+1))
