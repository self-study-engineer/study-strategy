## はじめに

<!-- バナー画像をここに貼る（例: 1RPPS.png）。前作の 1DA.png と同じ要領で Qiita にアップロードしてURLを差し込む -->
![](RP_PS_mechanism.png)

本記事では、割り当て問題（ヒトとモノのマッチング）のメカニズムである **RPメカニズム**・**PSメカニズム**をPythonで実装し、さらに求めた確率行列を **実際の割り当て** に変換するところまでを一気通貫で扱います。理論の振り返りも兼ねて、実際にソースコードを動かしながら理解を深めることを目的にしています。

- 【**想定する読者**】マッチング理論の初学者エンジニア
- 【**理論編**】マッチング理論 〜割り当て問題の共有知識〜
- 【**実装編**】RP・PSメカニズムと実際の割り当て 〜確率行列を作って「くじ」に変える〜 ← <font color=red><b>今回はここ！</b></font>
- [サンプルコード](https://github.com/itokohei0/MarketDesignStudy/tree/master/%E3%83%9E%E3%83%83%E3%83%81%E3%83%B3%E3%82%B0%E7%90%86%E8%AB%96)

<font color=red>1エンジニアの独学で作った記事なので間違った内容を含むと思います。遠慮なくコメントいただけますと幸いです。</font>

### この記事のゴール

割り当ての流れは「**個人の選好表明 → 確率行列 → 実際の割り当て**」の3ステップです。選好を入力データとして、RP・PSメカニズムを適用し、出力データとして確率行列を得ます。そして、確率行列を新たな入力データとして、バーコフ＝フォン・ノイマンの定理を適用し、出力データとして確定的な割り当てを求めます。
　本記事は**前半**でRP・PSを実装して確率行列を求め、**後半**でバーコフ＝フォン・ノイマンの定理を実装して確率行列を割り当てに変換します。

```mermaid
flowchart LR
  A["個人の選好表明<br>（希望リスト）"] -->|"<b>RP・PSメカニズム"| B["確率行列 P"]
  B -->|"<b>バーコフ＝フォン・ノイマンの定理"| C["確定的な割り当て<br>上のくじ"]
  style B fill:#aaf
  style C fill:#aff
```

:::note info
**理論編の復習**

|            | RPメカニズム                       | PSメカニズム                 |
| ---------- | ---------------------------------- | ---------------------------- |
| 直感       | くじで順番を決めて選ぶ             | 全員同時に少しずつ食べる     |
| 強み       | 耐戦略性・水平性を満たす           | 順序効率性・無羨望性を満たす |
| 弱み       | 順序効率性を満たさない             | 耐戦略性を満たさない         |
| 大市場では | 順序効率性・無羨望性も近似的に回復 | 耐戦略性も回復               |

:::

本記事のコードはすべて確率を `fractions.Fraction` で扱い、$\frac{5}{12}$ のような値を**誤差なく**計算します。

# 【前半】確率行列を「求める」

## データ構造とアルゴリズム

### 入出力データ

入出力データはRPとPSで共通とし、以下のように定義します。ここで、`∅`（どの財も受け取らない）は供給無制限の特別な財として最後の列に置きます。

- 【**入力データ`Input`**】各個人の選好と各財の供給数
- 【**出力データ`ProbabilityMatrix`**】確率行列

```python
from dataclasses import dataclass, field
from fractions import Fraction

EMPTY = "∅"  # どの財も受け取らないことを表す特別な財（供給数は無制限）

@dataclass
class Input:
    """確率的割り当て問題の入力（RP / PS 共通の形式）"""
    prefs: list[list[str]]              # 各個人の選好（左ほど好き）
    capacities: dict[str, int]         # 各財の供給数
    agent_names: list[str] | None = None
    goods: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.goods:
            self.goods = list(self.capacities.keys())

    @property
    def n_agents(self) -> int:
        return len(self.prefs)

    def columns(self) -> list[str]:
        """確率行列の列順（財 → 最後に ∅）。"""
        return [*self.goods, EMPTY]

    def acceptable_pref(self, agent: int) -> list[str]:
        """個人 agent の選好を ∅ までで切り出し，末尾に ∅ を保証して返す。"""
        cut: list[str] = []
        for item in self.prefs[agent]:
            cut.append(item)
            if item == EMPTY:
                return cut
        cut.append(EMPTY)
        return cut

@dataclass
class ProbabilityMatrix:
    """確率行列（各成分は Fraction）。行＝個人，列＝財（末尾が ∅）。"""

    columns: list[str]
    rows: list[list[Fraction]]
    agent_label: str = "個人"
    agent_names: list[str] | None = None

    def row_of(self, agent: int) -> list[Fraction]:
        return self.rows[agent]

    def name(self, agent: int) -> str:
        if self.agent_names:
            return self.agent_names[agent]
        return f"{self.agent_label}{agent + 1}"

    def __str__(self) -> str:
        name_w = max((len(self.name(i)) for i in range(len(self.rows))), default=4)
        header = " " * (name_w + 2) + "  ".join(f"{c:>6}" for c in self.columns)
        lines = [header]
        for i, row in enumerate(self.rows):
            cells = "  ".join(f"{frac_str(p):>6}" for p in row)
            lines.append(f"{self.name(i):<{name_w}}  {cells}")
        return "\n".join(lines)
```

出力の確率行列 `ProbabilityMatrix` は、各成分を `Fraction` で持つ行列です（行＝個人・列＝財）。

### アルゴリズム

#### RPメカニズムの実装

RPメカニズムは「すべての優先順位（$n!$ 通り）を列挙し、各順位で逐次独裁制を行って平均する」ことで**厳密な確率行列**を求めます。

```python
from itertools import permutations
from fractions import Fraction

def random_priority(
    data: Input,
    *,
    n_samples: int | None = None,
    seed: int | None = None,
    verbose: bool = True,
) -> ProbabilityMatrix:
    """RPメカニズムが定める確率行列を返す。"""

    columns = data.columns()
    col_index = {c: k for k, c in enumerate(columns)}
    n = data.n_agents

    if verbose:
        print_input(data)
        print("=== RPメカニズム ===\n")

    # 優先順位の並び（全 n! 通り or 無作為抽出）を用意する
    if n_samples is None:
        orders = permutations(range(n))
    else:
        rng = random.Random(seed)
        orders = (tuple(rng.sample(range(n), n)) for _ in range(n_samples))

    # 【確率計算】各優先順位で逐次独裁制（高優先の人から残存財の最善を取る）を行い，平均する
    counts = [[Fraction(0) for _ in columns] for _ in range(n)]
    total = 0
    for order in orders:
        remaining = dict(data.capacities)          # 残りの供給数（整数）
        alloc = [EMPTY] * n
        for agent in order:                        # 優先順位の高い人から確定的に取る
            for item in data.acceptable_pref(agent):
                if item == EMPTY:
                    break
                if remaining.get(item, 0) > 0:
                    alloc[agent] = item
                    remaining[item] -= 1
                    break
        for i, good in enumerate(alloc):
            counts[i][col_index[good]] += 1
        total += 1
    rows = [[count / total for count in row] for row in counts]

    matrix = ProbabilityMatrix(columns=columns, rows=rows, agent_label=data.agent_label, agent_names=data.agent_names)
    if verbose:
        print_result(data, matrix, "RPメカニズムの確率行列")
    return matrix
```

ポイントは内側の二重ループで、ある優先順位 `order` のもとで「上位の人から、残っている中で最も好きな財を1つ取る」という逐次独裁制をそのまま書いています。これを全順序について平均すれば確率行列になります。

#### PSメカニズムの実装

PSメカニズムは「全員が同時に、残っている中で一番好きな財を食べる」過程を、**イベント駆動**（どれかの財が食べ尽くされる瞬間まで一気に時間を進める）でシミュレートします。

```python
from fractions import Fraction

def probabilistic_serial(
    data: Input,
    *,
    verbose: bool = True,
) -> ProbabilityMatrix:
    """PSメカニズムが定める確率行列を返す。"""

    columns = data.columns()
    col_index = {c: k for k, c in enumerate(columns)}
    n = data.n_agents

    if verbose:
        print_input(data)
        print("=== PSメカニズム ===\n")

    # 残量（∅ は無制限なので None で表す）
    remaining: dict[str, Fraction | None] = {g: Fraction(q) for g, q in data.capacities.items()}
    remaining[EMPTY] = None

    # 【確率計算】各局面で全員が同時に残存財の最善を食べ，食べた量（時間）を積み上げる
    rows = [[Fraction(0) for _ in columns] for _ in range(n)]
    t, end = Fraction(0), Fraction(1)
    while t < end:
        alloc = [EMPTY] * n
        for agent in range(n):                     # 各人がいま食べる残存財の最善を選ぶ
            for item in data.acceptable_pref(agent):
                if item == EMPTY:
                    break
                amt = remaining.get(item)          # 供給に無い財は None → 無視（RP版の .get と同挙動）
                if amt is not None and amt > 0:
                    alloc[agent] = item
                    break
        # 次にどれかの財が食べ尽くされるまでの時間 Δt（上限は t=1 までの残り）
        dt = end - t
        for good in set(alloc):
            amt = remaining[good]
            if amt is not None:
                dt = min(dt, amt / alloc.count(good))
        for i, good in enumerate(alloc):
            rows[i][col_index[good]] += dt
        for good in set(alloc):                    # 食べた分だけ残量を減らす（∅ は減らない）
            amt = remaining[good]
            if amt is not None:
                remaining[good] = amt - alloc.count(good) * dt
        t += dt

    matrix = ProbabilityMatrix(columns=columns, rows=rows, agent_label=data.agent_label, agent_names=data.agent_names)
    if verbose:
        print_result(data, matrix, "PSメカニズムの確率行列")
    return matrix
```

`dt`（次に何かが食べ尽くされるまでの時間）を一気に進めるのがポイントです。`amt / alloc.count(good)`＝「残量 ÷ その財を食べている人数」で、その財が消えるまでの時間を計算しています。








## 動作確認

### 【例1】個人4人・財2つ

教科書と同じ設定です。佐藤・鈴木は $a,\ b,\ \emptyset$、高橋・田中は $b,\ a,\ \emptyset$ の順に希望し、供給は $q_a=q_b=1$ です。

<details><summary><b>テストケース</b></summary>

```python
from rp_algorithm import EMPTY, Input, random_priority

data = Input(
    prefs=[
        ["a", "b", EMPTY],   # 佐藤
        ["a", "b", EMPTY],   # 鈴木
        ["b", "a", EMPTY],   # 高橋
        ["b", "a", EMPTY],   # 田中
    ],
    capacities={"a": 1, "b": 1},
    agent_names=["佐藤", "鈴木", "高橋", "田中"],
)
matrix = random_priority(data)
```

</details>
<br>

**RPメカニズムの確率行列**

```bash
=== RPメカニズムの確率行列 ===
               a       b       ∅
佐藤        5/12    1/12     1/2
鈴木        5/12    1/12     1/2
高橋        1/12    5/12     1/2
田中        1/12    5/12     1/2
  ------------------------------
期待人数       1       1       2
```

教科書の確率行列（佐藤・鈴木は $a=\frac{5}{12}$、高橋・田中は $b=\frac{5}{12}$）を厳密に再現できました。

<details><summary><b>佐藤が財 a をもらえる確率 5/12 の内訳（手計算）</b></summary>

佐藤が $a$ を取れるのは「①佐藤が1位のとき」か「②高橋か田中が1位かつ佐藤が2位のとき」です。

- ①の確率 $= \dfrac{3!}{4!}=\dfrac{6}{24}\\[3mm]$
- ②の確率 $= \dfrac{{}_2P_1\times 2!}{4!}=\dfrac{4}{24}\\[3mm]$
- 合計 $= \dfrac{10}{24}=\dfrac{5}{12}$

何ももらえない確率（$\emptyset$、＝3位か4位）は $\dfrac{3!\times 2}{4!}=\dfrac{1}{2}$。残りが $b$ で $1-\frac{10}{24}-\frac{12}{24}=\frac{2}{24}=\frac{1}{12}$ となります。全列挙のコードの結果と手計算が一致していることが分かります。

</details>
<br>

**PSメカニズムの確率行列**

```bash
=== PSメカニズムの確率行列 ===
               a       b       ∅
佐藤         1/2       0     1/2
鈴木         1/2       0     1/2
高橋           0     1/2     1/2
田中           0     1/2     1/2
  ------------------------------
期待人数       1       1       2
```

同じ入力でも、RPの $(\frac{5}{12},\frac{1}{12},\frac{1}{2})$ に対しPSは $(\frac{1}{2},0,\frac{1}{2})$ と異なる行列になりました。PSでは第2希望の財（佐藤にとっての $b$）に確率が漏れず、第1希望に確率が集中するぶん、**順序効率的**な配分になっています。








### モンテカルロ近似

$n!$ の全列挙は個人数が増えると重くなります（目安 $n>8$）。その場合は `n_samples` を指定して、優先順位を無作為抽出する**モンテカルロ近似**に切り替えられます。

```python
matrix = random_priority(data, n_samples=200_000, seed=42)
```

```bash
近似確率行列（200,000 回サンプリング, 小数表示）:
  佐藤: 0.417  0.083  0.501   （列: a, b, ∅）
  鈴木: 0.417  0.084  0.500   （列: a, b, ∅）
  高橋: 0.083  0.418  0.499   （列: a, b, ∅）
  田中: 0.084  0.415  0.501   （列: a, b, ∅）
```

厳密値 $\frac{5}{12}\approx 0.417$ にしっかり近づいています（小数第3位で四捨五入しているため、行の和がちょうど1にならないことがあります）。

:::note warn
**計算量の注意**
RPの厳密計算は全 $n!$ 通りを列挙するため $O(n!\cdot n)$ です。$n=9$ で約3秒、$n=10$ で約30秒が実用上の限界の目安なので、それ以上はモンテカルロ近似を使ってください。
:::

### 【PSメカニズム：例2】PSは耐戦略性を満たさない

理論編で「PSは耐戦略性を満たさない」と述べました。その反例を実際に作って確認します。

<details><summary><b>テストケース</b></summary>

```python
data = Input(
    prefs=[
        ["a", "b", EMPTY],   # 佐藤（真の選好）
        ["a", EMPTY],        # 鈴木
        ["b", EMPTY],        # 高橋
        ["b", EMPTY],        # 田中
    ],
    capacities={"a": 1, "b": 1},
    agent_names=["佐藤", "鈴木", "高橋", "田中"],
)
matrix = probabilistic_serial(data)
```

</details>
<br>

```bash
=== PSメカニズムの確率行列 ===
               a       b       ∅
佐藤         1/2       0     1/2
鈴木         1/2       0     1/2
高橋           0     1/2     1/2
田中           0     1/2     1/2
  ------------------------------
期待人数       1       1       2

【水平性】✅ 成立
【無羨望性】✅ 成立
【順序効率性】✅ 成立
【耐戦略性】❌ 不成立
    - 佐藤 は虚偽申告 [b, a, ∅] で得できる可能性がある
```

佐藤が正直に `a, b, ∅` と申告すると $(\frac{1}{2},0,\frac{1}{2})$ ですが、`b, a, ∅` と**嘘をつくと** $(\frac{1}{3},\frac{1}{3},\frac{1}{3})$ になります。効用が $u_a=6,u_b=5,u_\emptyset=0$ なら、期待効用は $3 \to 3\frac{2}{3}$ と上がり、嘘が得になってしまいます。

同じ入力をRPにかけると耐戦略性は ✅ のままです（佐藤は $(\frac{1}{2},\frac{1}{12},\frac{5}{12})$）。RPとPSの「一長一短」が、コードの判定でもはっきり確認できました。



# 【後半】確率行列を割り当てに変換する

## なぜ確率行列だけでは足りないのか

第1部で確率行列は求まりました。しかし $(\frac{1}{2},0,\frac{1}{2})$ と言われても、**実際に誰に何を配ればいいか**は決まりません。確率はあくまで「割り当ての設計図」であって、最後は1つの確定的な割り当て（誰が何をもらうか）に落とし込む必要があります。
　そこで使うのが**バーコフ＝フォン・ノイマンの定理**です。この定理を用いて確定的な割り当てを求めることができます。以降、<font color=red>$n$人の個人に$n$種類の財をちょうど1つずつ割り当てる問題を考えます</font>。これにより、確率行列は以下の特徴を持ちます。

- 【**特徴1**】確率行列の要素は全て0以上1以下
- 【**特徴2**】各個人が少なくともどれかの財をもらえる確率が1（**各行の和が1**）
- 【**特徴3**】各財が少なくとも誰かに割り当てられる確率も1（**各列の和が1**）

## バーコフ＝フォン・ノイマンの定理

まず用語を整理します。

| 用語         | 定義                                                      |
| ------------ | --------------------------------------------------------- |
| 確率行列     | 各要素が非負で、各**行**の和が1の行列                     |
| 二重確率行列 | 各要素が非負で、各**行・各列**の和が1の正方行列           |
| 置換行列     | 各行・各列に1が1つだけある行列（＝1つの確定的な割り当て） |
| 凸結合       | 重みが非負で総和が1の重みつき和                           |

:::note info
**バーコフ＝フォン・ノイマンの定理**
どんな**二重確率行列**も、**置換行列の凸結合**で表現できる。
:::

置換行列は「確率1で誰に何を配るか」を表す確定的な割り当てです。だから二重確率行列を置換行列の凸結合に分解できれば、「**重み（確率）に従ってくじを引き、当たった置換行列の通りに配る**」という実際の手続きが得られます。

以下に個人3人に財$\{a,b,c\}$を割り当てる確率行列にバーコフ＝フォンノイマンの定理を適用した例を示します。

```math
\left(
  \begin{array}{ccc}
    1/6 & 1/3 & 1/2\\
    1/3 & 2/3 & 0\\
    1/2 & 0   & 1/2
  \end{array}
\right)
=\frac{1}{2}\!
\underbrace{\left(
  \begin{array}{ccc}
    0&0&1\\ 0&1&0\\ 1&0&0
  \end{array}
\right)}_{置換行列}
+\frac{1}{3}\!
\underbrace{\left(
  \begin{array}{ccc}
    0&1&0\\ 1&0&0\\ 0&0&1
  \end{array}
\right)}_{置換行列}
+\frac{1}{6}\!
\underbrace{\left(
  \begin{array}{ccc}
    1&0&0\\ 0&1&0\\ 0&0&1
  \end{array}
\right)}_{置換行列}\\[5mm]
【凸結合】\frac{1}{2}+\frac{1}{3}+\frac{1}{6}=1
```

上式で得られた結果は以下のことを示します。

- 【**パターン1**】確率$1/2$で個人$1,2,3$にそれぞれ財$c,b,a$を割り当てる
- 【**パターン2**】確率$1/3$で個人$1,2,3$にそれぞれ財$b,a,c$を割り当てる
- 【**パターン3**】確率$1/6$で個人$1,2,3$にそれぞれ財$a,b,c$を割り当てる

<!-- 9章の分解手順の図（9-1〜9-6.png）を貼る場所。サイクルを見つけて重みを移す手順 -->

## BvN分解の実装

分解は「残差行列の非零成分（台集合）の中から**完全マッチング（置換）を1つ見つけ**、その最小重みを引く」を繰り返すだけです。完全マッチングは二部グラフ（行＝個人・列＝財）の**増加道法（`_find_permutation_in_support`関数）** で構成します。

```python
from dataclasses import dataclass
from fractions import Fraction

@dataclass
class BvNTerm:
    weight: Fraction
    perm: list[int]   # perm[i] = 行 i で 1 が立つ列

def birkhoff_von_neumann(matrix) -> list[BvNTerm]:
    P = [[Fraction(x) for x in row] for row in matrix]
    n = len(P)
    residual = [row[:] for row in P]
    terms = []
    while any(residual[i][j] != 0 for i in range(n) for j in range(n)):
        perm = _find_permutation_in_support(residual, n)   # 台集合の完全マッチング
        weight = min(residual[i][perm[i]] for i in range(n))  # その最小成分が重み
        for i in range(n):
            residual[i][perm[i]] -= weight
        terms.append(BvNTerm(weight=weight, perm=perm))
    return terms

def _find_permutation_in_support(residual, n):
    """残差の非零成分（support）だけで完全マッチングを1つ探す。"""
    match_col = [-1] * n   # 列 j に割り当てられた行
    result = [-1] * n      # result[i] = 行 i に割り当てられた列

    def try_assign(row, visited):
        for col in range(n):
            if residual[row][col] > 0 and not visited[col]:
                visited[col] = True
                if match_col[col] == -1 or try_assign(match_col[col], visited):
                    match_col[col] = row
                    result[row] = col
                    return True
        return False

    for row in range(n):
        if not try_assign(row, [False] * n):
            return None
    return result
```

二重確率行列であれば、台集合に必ず完全マッチングが存在することが保証されます（ホールの定理）。

</details>

## 動作確認

### 【例1】バーコフ＝フォンノイマンの定理単体のテスト

<details><summary><b>テストケース</b></summary>

```python
from bvn_algorithm import birkhoff_von_neumann

P = [
    ["1/6", "1/3", "1/2"],
    ["1/3", "2/3", "0"],
    ["1/2", "0", "1/2"],
]
terms = birkhoff_von_neumann(P)
```

</details>
<br>

```bash
=== バーコフ＝フォン・ノイマン分解 ===

【第1項】 λ = 1/2
  [    0     0     1 ]
  [    0     1     0 ]
  [    1     0     0 ]
【第2項】 λ = 1/3
  [    0     1     0 ]
  [    1     0     0 ]
  [    0     0     1 ]
【第3項】 λ = 1/6
  [    1     0     0 ]
  [    0     1     0 ]
  [    0     0     1 ]

【くじとしての解釈】
  確率 1/2 で: 個人1→財c, 個人2→財b, 個人3→財a
  確率 1/3 で: 個人1→財b, 個人2→財a, 個人3→財c
  確率 1/6 で: 個人1→財a, 個人2→財b, 個人3→財c
```

二重確率行列が3つの確定的な割り当て（置換行列）と、それぞれを選ぶ確率に分解できました。あとはこの確率でくじを引けば、設計図どおりの割り当てが実現します。

### 【例2】一気通貫：PSメカニズム → BvN分解

第1部のPSと第2部のBvNをつなげば、「**選好 → 確率行列 → 確定的な割り当てのくじ**」が1本のパイプラインになります。

<details><summary><b>テストケース</b></summary>

```python
from rp_algorithm import EMPTY, Input
from ps_algorithm import probabilistic_serial
from bvn_algorithm import birkhoff_von_neumann, reconstruct, _print_matrix

data = Input(
    prefs=[
        ["a", "b", "c", EMPTY],
        ["a", "c", "b", EMPTY],
        ["b", "a", "c", EMPTY],
    ],
    capacities={"a": 1, "b": 1, "c": 1},
)
matrix = probabilistic_serial(data, verbose=False)      # 選好 → 確率行列（PS）

n_goods = len(data.goods)
sub = [row[:n_goods] for row in matrix.rows]            # ∅ 列を除く（3×3 の二重確率行列）

print("PSが定める確率行列（∅ 列を除く，行＝個人 / 列＝a,b,c）:")
_print_matrix(sub)
print()

terms = birkhoff_von_neumann(sub)                       # 確率行列 → 置換行列の凸結合
rebuilt = reconstruct(terms, len(sub))
print(f"分解の再構成が元の確率行列と一致: {rebuilt == sub}")
print()
_print_lottery_interpretation(terms)
```

</details>
<br>

**実行結果**

```bash
...

PSが定める確率行列（∅ 列を除く，行＝個人 / 列＝a,b,c）:
  [  1/2   1/4   1/4 ]
  [  1/2     0   1/2 ]
  [    0   3/4   1/4 ]

=== バーコフ＝フォン・ノイマン分解 ===

【入力（二重確率行列 P）】
  [  1/2   1/4   1/4 ]
  [  1/2     0   1/2 ]
  [    0   3/4   1/4 ]

【第1項】 λ = 1/2
  [    1     0     0 ]
  [    0     0     1 ]
  [    0     1     0 ]

【第2項】 λ = 1/4
  [    0     0     1 ]
  [    1     0     0 ]
  [    0     1     0 ]

【第3項】 λ = 1/4
  [    0     1     0 ]
  [    1     0     0 ]
  [    0     0     1 ]

分解された置換行列の数: 3　/　重みの総和: 1

分解の再構成が元の確率行列と一致: True

...
```

PSが出した確率行列をBvN分解し、分解結果を足し戻すと**元の行列にぴったり一致**しました（`True`）。確率行列が「絵に描いた餅」ではなく、実際に遂行できる割り当てであることが確認できます。

:::note warn
**∅ 列をそのまま落とせる条件**
この例で ∅ 列を除くだけで正方の二重確率行列になるのは、財の総供給数（3）と人数（3）が等しく、全員がすべての財を受容するため ∅ の確率がすべて0になる特殊な設定だからです。∅ に正の確率が付く問題では、∅ を「供給数が十分大きいダミー財」として行列に残し、行和・列和が1にそろうよう列を複製するなどの前処理をしてから分解します。
:::

:::note info
**計算量について**
$n\times n$ の二重確率行列は高々 $n^2-2n+2$ 個の置換行列に分解できます。ただし「実際に1つの割り当てを実現する」だけなら、分解の途中で引いたくじに従って片方を捨てていけるので、$n^2$ 程度のステップで確定割り当てにたどり着けます。なお分解の仕方は一意とは限りません。
:::

## まとめ

本記事では、割り当ての「選好 → 確率行列 → 実際の割り当て」を一気通貫で実装しました。

- 【**前半**】RP（全順序の列挙）とPS（イベント駆動の食べ尽くし）で確率行列を厳密に計算し、4性質を自動判定。RPは順序効率性を、PSは耐戦略性を満たさないことをコードで確認した。
- 【**後半**】バーコフ＝フォン・ノイマンの定理で、二重確率行列を置換行列の凸結合（くじ）に分解し、確率行列を実際の割り当てに変換した。



## 参考文献

- [マッチング理論とマーケットデザイン](https://www.amazon.co.jp/dp/453555935X)
