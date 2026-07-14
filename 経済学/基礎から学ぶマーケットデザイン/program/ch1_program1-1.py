# Condorcet jury theorem

import random

# プレーヤーの数
N = 3

# 繰り返し回数
T = 1000

# 各プレーヤーが正しい決定をする確率
p = [0]*N
for i in range(N):
    r = 0
    while r<=0.5:
        r = random.random()
    p[i]=r
    print('プレーヤー',i+1,'の決定が正しい確率 = ',p[i])

# 3人の合議による決定が正しい確率
q1 = 0
for i in range(T):
    v = 0
    # 各プレーヤーjが正しい決定=1，それ以外は0
    for j in range(N):
        r = random.random()
        if r < p[j]:
            v += 1
    # 多数決による3人の合議が正しい決定である回数
    if v > N/2:
        q1 += 1
# 正しい決定をした割合の計算
q1 = q1/T
print('3人の合議による決定が正しい確率 = ',q1)

# 各プレーヤーの決定が正しい確率の平均
q2 = 0
for i in range(T):
    # プレーヤーの中から1人を選ぶ
    j = random.randint(0,2)
    # 選ばれたプレーヤーが正しい決定をした回数
    r = random.random()
    if r < p[j]:
        q2 += 1
# 正しい決定をした割合の計算
q2 = q2/T
print('各プレーヤーの決定が正しい確率の平均 = ',q2)
