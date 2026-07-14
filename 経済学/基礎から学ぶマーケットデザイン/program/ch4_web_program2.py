# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 17:28:33 2021

@author: MXE03
"""
# TTC方式
print('TTC方式によるマッチング')
print()

# 学生の数
S=3

# 研究室の数
C=3

# 生徒の選好、左からc1の順位、c2の順位、……
s_pref=[
        [2,1,3],
        [1,2,3],
        [1,2,3]
]
for i in range(S):
    print('生徒',i+1,'の希望順位：',end='')
    for j in range(C):
        print(' c{0}'.format(s_pref[i][j]),end='')
    print()
print()

# 学校の優先順位、左からs1の順位、s2の順位、……
c_pref=[
        [1,3,2],
        [2,1,3],
        [2,1,3]
]
for i in range(C):
    print('学校',i+1,'の優先順位：',end='')
    for j in range(S):
        print(' s{0}'.format(c_pref[i][j]),end='')
    print()
print()

# 研究室の定員
capacity=[1,1,1]
for i in range(C):
    print('学校',i+1,'の定員：',end='')
    print(capacity[i])
print()

# マッチした相手
s_matched=[-1]*S # アンマッチなら-1
c_matched=[[0]*S for i in range(C)]

# 学生の選好を第1希望から順に並べ替える
s_propose=[[0]*C for i in range(S)]
for i in range(S):
    for j in range(C):
        k = s_pref[i][j]
        s_propose[i][k-1]=j

# マッチしている学生の数
num_match = 0

# 学生にマッチした相手がいれば1、そうでなければ0
s_filled=[0]*S

# すでに学校に割り当てられている人数
c_filled=[0]*C

# 生徒が第何希望まですでに指差したか
position = [0]*(C+1)

# TTC方式でマッチングを決める

# すべての生徒がマッチするまで繰り返す
t=1
while num_match < S:
    print('ステップ{0}'.format(t))
    
    # サイクル候補
    cycle = [0]*(S+C)
    
    # 生徒が順に指差していく
    for i in range(S):
        # 生徒がまだ誰ともマッチしていないなら
        if s_filled[i]==0:
            
            # この生徒を含むサイクルが形成されるかのフラグ
            flag = 0
            
            #　サイクルの長さ
            num = 0
            
            # 最初に指差す学生
            x = i
            
            # ループ
            while flag==0:
                # 学生自身をサイクル候補に入れる
                cycle[num]=x 
                
                # 学生がプロポーズする学校
                k = s_propose[x][position[x]]
                print('s{0}がc{1}を指差す'.format(x+1,k+1))
                
                # 学校kの定員がすでに埋まっていたらループを抜ける
                if c_filled[k]==capacity[k]:
                    print('c{0}の定員が埋まっている'.format(k+1))
                    flag = 1
                else:
                    # 学校kをサイクル候補に入れる
                    num += 1
                    cycle[num]=k+S
                
                    # まだ配属されていない学生の中から一番順位の高い生徒yを選ぶ
                    m = 0
                    y = c_pref[k][m]-1
                    while s_filled[y]==1:
                        m += 1
                        y = c_pref[k][m]-1

                    # もし学校が生徒xを指差していたらサイクル形成
                    if y in cycle:
                        print('c{0}がs{1}を指差す'.format(k+1,y+1))
                        print()
                        print('サイクル形成')
                        flag = 2
                    else:
                        print('c{0}がs{1}を指差す'.format(k+1,y+1),end='')
                        # 学校kが指差した生徒yをxにしてループに戻る
                        x = y
                        num += 1
            
                # サイクルができた場合
                if flag == 2:
                    # サイクルの最後尾の学校が指差した生徒のcycle内のインデックス
                    z = cycle.index(y)
                    for l in range(z,num+1,2):
                        print('s{0}　→　c{1}　→　'.format(cycle[l]+1,cycle[l+1]-(S-1)),end='')
                        s_matched[cycle[l]]=cycle[l+1]-S
                        s_filled[cycle[l]]=1
                        num_match += 1
                        c_filled[cycle[l+1]-S]+=1
                    print('s{}'.format(cycle[z]+1))
                print()
            
    # マッチできなかった生徒は次の希望順位に応募
    for i in range(S):
        if s_filled[i]==0:
            position[i] += 1
        # すべての学校にプロポーズしたらアンマッチ
        if position[i]==C:
            s_matched[i]=-1
            s_filled[i]=1
            num_match +=1

    t += 1
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
