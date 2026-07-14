# DA mechanism
print('受入保留方式によるマッチング')
print()

# 学生の数
S=4

# 研究室の数
C=3

# 学生の選好、左からc1の順位、c2の順位、……
s_pref=[
        [1,2,3],
        [1,2,3],
        [2,3,1],
        [3,1,2]
]
for i in range(S):
    print('学生',i+1,'の希望順位：',end='')
    for j in range(C):
        print(' s{0}'.format(s_pref[i][j]),end='')
    print()
print()

# 研究室の選好、左からs1の順位、s2の順位、……
c_pref=[
        [1,2,3,4],
        [2,3,4,1],
        [4,1,2,3]
]
for i in range(C):
    print('研究室',i+1,'の希望順位：',end='')
    for j in range(S):
        print(' c{0}'.format(c_pref[i][j]),end='')
    print()
print()

# 研究室の希望順位を左からs1の順位、s2の順位、……に変換する
c_order = [[0]*S for i in range(C)]
for i in range(C):
    for j in range(S):
        k = c_pref[i][j]
        c_order[i][k-1] = j+1
        
# 研究室の定員
capacity=[1,1,2]
for i in range(C):
    print('学校',i+1,'の定員：',end='')
    print(capacity[i])
print()

# マッチした相手
s_matched=[0]*(S+1)
c_matched=[[0]*(S+1) for i in range(C)]

# 受入保留方式でマッチングを決める

# 仮マッチしている学生の数
num_match = 0

# 学生に仮マッチした相手がいれば1、そうでなければ0
s_filled=[0]*(S+1)

# すでに学校に割り当てられている人数
c_filled=[0]*C

# 第何希望まですでにプロポーズしたか
position = [0]*(S+1)

# ステップ数
t=1
while num_match < S:
    print('ステップ {}'.format(t))
    for i in range(S):
        # 学生がまだ誰ともマッチしていないなら
        if s_filled[i]==0:
            # 学生がプロポーズする相手
            j = s_pref[i][position[i]]-1
            print('s{0}がc{1}にプロポーズ'.format(i+1,j+1))
            # 研究室の定員に空きがある場合
            if c_filled[j]<capacity[j]:
                # iとjがマッチ
                c_matched[j][i]=1
                s_matched[i]=j
                print('　s{0}とc{1}が仮マッチ'.format(i+1,j+1))
                s_filled[i]=1
                c_filled[j]+=1
                num_match +=1
            # 研究室の定員がすでに埋まっている場合
            else:
                temp = -1
                # ダミープレーヤー
                rejected = S
                for k in range(S):
                    if c_matched[j][k]==1:
                        # 学生kがリジェクトされる候補になるなら
                        if c_order[j][i] < c_order[j][k] and c_order[j][k]>temp:
                            # 前に仮リジェクトされた学生を戻す
                            s_filled[rejected]=1
                            position[rejected]-=1
                            c_matched[j][rejected]=1
                            s_matched[rejected]=j
                            # 新たに学生kを仮リジェクトする
                            s_filled[k]=0
                            position[k]+=1
                            rejected=k
                            c_matched[j][k]=0
                            # 修正箇所
                            # temp = c_pref[j][k]
                            temp = c_order[j][k]
                            print('　c{0}がs{1}をリジェクト'.format(j+1,k+1))
                            
                # 学生iが研究室jに受け入れられたならば
                if temp > -1:
                    c_matched[j][i]=1
                    s_matched[i]=j
                    print('　s{0}とc{1}が仮マッチ'.format(i+1,j+1))
                    s_filled[i]=1
                    # 修正箇所
                    if position[rejected]==C:
                        s_matched[rejected] = -1
                        s_filled[rejected] = 1
                        num_match += 1
                else:
                    print('　c{0}がs{1}をリジェクト'.format(j+1,i+1))
                    position[i]+=1
                    # すべての男性にプロポーズしたらアンマッチ
                    if position[i]==C:
                        s_matched[i]=-1
                        s_filled[i]=1
                        num_match +=1
            print()
    t+=1
    print()

#　マッチング結果の印字
print('マッチング結果')
for i in range(S):
    if s_matched[i]==-1:
        print('s{0}:'.format(i+1))
    else:
        print('s{0}: c{1}'.format(i+1,s_matched[i]+1))
        
for j in range(C):
    if c_filled[j]==0:
        print('  : c{0}'.format(j+1))
