# DA mechanism
print('受入保留方式によるマッチング')
print()

# 女性の数
W=3

# 男性の数
M=2

# 女性の選好
w_pref=[
        [1,2],
        [2,1],
        [1,2]
]
for i in range(W):
    print('女性',i+1,'の希望順位：',end='')
    for j in range(M):
        print(' m{0}'.format(w_pref[i][j]),end='')
    print()
print()
        
# 男性の選好
m_pref=[
        [2,1,3],
        [1,2,3],
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

# 受入保留方式でマッチングを決める

# 仮マッチしている女性の数
num_match = 0

# 仮マッチした相手がいれば1，そうでなければ0
w_filled=[0]*W
m_filled=[0]*M

# 第何希望まですでにプロポーズしたか
position = [0]*W

# ステップ数
t=1
while num_match < W:
    print('ステップ {}'.format(t))
    for i in range(W):
        # 女性がまだ誰ともマッチしていないなら
        if w_filled[i]==0:
            # 女性がプロポーズする相手
            j = w_pref[i][position[i]]-1
            # プロポーズした男性の現在の仮マッチ
            k = m_matched[j]
            print('w{0}がm{1}にプロポーズ'.format(i+1,j+1))
            # 男性がまだ誰ともマッチしない場合
            if m_filled[j]==0:
                # iとjがマッチ
                m_matched[j]=i
                w_matched[i]=j
                print('　w{0}とm{1}が仮マッチ'.format(i+1,j+1))
                w_filled[i]=1
                m_filled[j]=1
                num_match +=1
            # 男性がすでに誰かとマッチしている場合
            elif m_order[j][i] < m_order[j][k]:
                w_filled[k]=0
                order[k]+=1
                print('　m{0}がw{1}をリジェクト'.format(j+1,k+1))
                m_matched[j]=i
                w_matched[i]=j
                print('　w{0}とm{1}が仮マッチ'.format(i+1,j+1))
                w_filled[i]=1
                m_filled[j]=1
            else:
                print('　m{0}がw{1}をリジェクト'.format(j+1,i+1))
                position[i]+=1
                # すべての男性にプロポーズしたらアンマッチ
                if position[i]==M:
                    w_matched[i]=-1
                    w_filled[i]=1
                    num_match +=1
            print()
    t+=1
    print()

#　マッチング結果の印字
print('マッチング結果')
for i in range(W):
    if w_matched[i]==-1:
        print('w{0}:'.format(i+1))
    else:
        print('w{0}: m{1}'.format(i+1,w_matched[i]+1))
        
for j in range(M):
    if m_filled[j]==0:
        print('  : m{0}'.format(j+1))
