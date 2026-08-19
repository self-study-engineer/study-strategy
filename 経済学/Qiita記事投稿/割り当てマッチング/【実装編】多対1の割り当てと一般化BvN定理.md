## はじめに

> 本記事は [Budish, Che, Kojima and Milgrom (2013)](https://static1.squarespace.com/static/5e56e1139e190014f1116cac/t/5e5c89d29d9d61249de4e77b/1583122898804/budish-che-kojima-milgrom-2013-aer.pdf)（2026/08/17時点） の内容になります。ただ、理論の証明には深入りせず、**実装をメイン**に扱います。

<!-- バナー画像をここに貼る（例: 2GBvN.png）。前作の RP_PS_mechanism.png と同じ要領で Qiita にアップロードしてURLを差し込む -->
![](RP_PS_mechanism.png)

前回はRP・PSメカニズムで確率行列を求め、バーコフ＝フォン・ノイマンの定理（以下$\text{BvN}$）で実際の割り当てに変換するところまでを実装しました。**本記事では多対一の割り当て問題を取り扱います**。具体的には、**二重階層（$\text{bihierarchy}$）** という条件を満たす制約構造であれば、正方行列でなくても、二重確率行列（行和と列和がともに1）でなくても確定的な割り当てのくじに分解できることを示し、また割り当て問題として「どこまで解けるのか」も示します。

- 【**想定する読者**】マッチング理論の初学者エンジニア
- 【**理論編**】マッチング理論 〜割り当て問題の共有知識〜
- 【**実装編**】RP・PSメカニズムと実際の割り当て
- 【**実装編**】多対1の割り当てと一般化BvN定理 ← <font color=red><b>今回はここ！</b></font>
- [サンプルコード](https://github.com/itokohei0/MarketDesignStudy/tree/master/%E3%83%9E%E3%83%83%E3%83%81%E3%83%B3%E3%82%B0%E7%90%86%E8%AB%96)

<font color=red>1エンジニアの独学で作った記事なので間違った内容を含むと思います。遠慮なくコメントいただけますと幸いです。</font>

### この記事のゴール

前回の BvN 実装（`bvn_algorithm.py`）は、入力を「正方の二重確率行列」に限定していました。今回作る `generalized_bvn_algorithm.py` は、**制約構造**という抽象化を導入することで、その制限を外します。

```mermaid
---
title: 前回と今回の守備範囲
---

flowchart LR
  A["確率行列<br>（正方・二重確率）"] -->|"<b>BvN定理"| B["置換行列の凸結合"]
  C["期待割当行列<br>（任意の形・任意の制約）"] -->|"<b>一般化BvN定理"| D["純割当（pure assignment）<br>の凸結合"]
  style B fill:#aff
  style D fill:#aaf
```

実装するのは次の3つです。

|     | やること                             | 対応する概念                                       |
| --- | ------------------------------------ | -------------------------------------------------- |
| 1   | 制約をデータ構造で表現する           | 制約構造 $\mathcal{H}$                             |
| 2   | 「解けるかどうか」を機械的に判定する | $\text{bihierarchy}$ 判定（**交差グラフの2彩色**） |
| 3   | 期待割当を純割当のくじに分解する     | 一般化BvN分解                                      |

コードはすべて `fractions.Fraction` で厳密計算し、**標準ライブラリのみ**で動きます（Python 3.10+）。

## 課題設定

### なぜ二重確率行列では足りないのか

前回の設定は「$n$人に$n$種類の財をちょうど1つずつ」でした。この枠に入らない要求を並べてみます。

| 現実の要請                                             | 二重確率行列で表現できるか |
| ------------------------------------------------------ | :------------------------- |
| 学校の定員が複数（**多対1**）                          | ❌ 列和が1でなくなる        |
| 学生が複数科目を履修（**多対多**）                     | ❌ 行和が1でなくなる        |
| 定員割れ・未割当を許す                                 | ❌ 行和・列和が固定されない |
| アファーマティブ・アクション（学区別・属性別クォータ） | ❌ 列の**部分**に制約       |
| 時間割制約（同時限の科目は取れない）                   | ❌ 行の**部分**に制約       |
| 校舎を共有する複数プログラムの定員融通                 | ❌ **複数列**にまたがる制約 |

つまり「行和=1、列和=1」という**2種類の制約しか書けない**のが限界でした。ならば制約そのものを一般的に書けるデータ構造を作ればよい、というのが今回の方針です。

### 制約構造と二重階層（$\text{bihierarchy}$）

まず制約構造$S$の説明をします。個人 $i$ が対象 $a$ を受け取る**個数**を$x_{ia}$とすると、制約構造$S \subseteq N \times O$（行列のセルの集合）は制約構造ごとに整数の下限$\underline{q}_S$と上限$\bar q_S$を与え、次の不等式を満たします。$$\underline{q}_S \;\le\; \sum_{(i,a)\in S} \underline{x}_{ia} \;\le\; \bar q_S$$

上記の制約構造のままだと任意の制約を書けるため、当然「書けるが解けない」制約が出てきます。そこで次に二重階層の説明をします。この二重階層が多対一の割り当て問題として「解けるか解けないか」の境界線の役割を果たします。

:::note info
**階層（$\text{hierarchy}$）**
制約集合の族の任意の2元 $S, S'$ について$$S \subseteq S' \quad\text{または}\quad S' \subseteq S \quad\text{または}\quad S \cap S' = \emptyset$$つまり「**入れ子か、交わらないか**」しかない族。

**bihierarchy（二重階層）**
制約構造 $\mathcal{H}$ が共通部分を持たない2つの階層の和 $\mathcal{H} = \mathcal{H}_1 \sqcup \mathcal{H}_2$ に分割できること（直和に分割できること）。
:::

:::note info
**定理1（十分性）** — 制約構造が bihierarchy なら、クォータを満たす任意の期待割当は必ず実装可能。

**定理2（必要性）** — 行制約と列制約をすべて含む「正準二部制約構造」では、bihierarchy は**必要十分**。
:::

なぜ階層が**2つ**必要なのか。行同士は互いに素なので階層になります。列同士も互いに素なので階層になります。しかし**行と列は必ず交差する**（1点で交わり、どちらも他方を含まない）ので、1つの階層にはまとめられません。だから2つに分けて詰め込む——これが bihierarchy の直感です。

そして BvN 定理は、この定理1の1行系にすぎません。

> **系1（BvN定理）**: 行はすべて互いに素なので階層 $\mathcal{H}_1$。列も互いに素なので階層 $\mathcal{H}_2$。よって bihierarchy。定理1より、任意の二重確率行列は置換行列の凸結合。**以上**。

## プログラム

### データ構造

制約集合とその集まりを、そのままデータクラスにします。

```python
from dataclasses import dataclass, field
from fractions import Fraction

Cell = tuple[int, int]      # (個人 index, 対象 index)
Matrix = list[list[Fraction]]


@dataclass(frozen=True)
class ConstraintSet:
    """制約集合 S とそのクォータ (q_S, q̄_S)。"""

    cells: frozenset[Cell]      # S に含まれる (個人, 対象) の組
    floor: int = 0              # 下限 q_S
    ceil: int | None = None     # 上限 q̄_S（None は上限なし）
    name: str = ""              # 表示用ラベル

    def total(self, X: Matrix) -> Fraction:
        return sum((X[i][a] for (i, a) in self.cells), Fraction(0))

    def label(self) -> str:
        return self.name or f"S{sorted(self.cells)}"


@dataclass
class ConstraintStructure:
    """制約構造 H。"""

    n_agents: int
    n_objects: int
    sets: list[ConstraintSet] = field(default_factory=list)

    def with_singletons(self, floor: int = 0, ceil: int | None = 1) -> "ConstraintStructure":
        """すべての単集合 {(i,a)} を（未登録なら）追加した新しい構造を返す。"""
        existing = {cs.cells for cs in self.sets}
        extra = [
            ConstraintSet(frozenset({(i, a)}), floor, ceil, name=f"単集合({i},{a})")
            for i in range(self.n_agents)
            for a in range(self.n_objects)
            if frozenset({(i, a)}) not in existing
        ]
        return ConstraintStructure(self.n_agents, self.n_objects, self.sets + extra)
```

`cells` を `frozenset` にしているのは、後で**包含関係と交差判定を集合演算で書きたい**からです。ここが今回の実装の設計上のキモになります。

制約集合を作るヘルパも用意します。行・列・部分行・部分列の4種類で、実用上の制約はだいたい書けます。

```python
def row(i: int, n_objects: int, floor: int, ceil: int | None, name: str = "") -> ConstraintSet:
    """行制約 {i}×O（個人 i の合計）。"""
    return ConstraintSet(
        frozenset((i, a) for a in range(n_objects)), floor, ceil, name or f"行{i}"
    )


def column(a: int, n_agents: int, floor: int, ceil: int | None, name: str = "") -> ConstraintSet:
    """列制約 N×{a}（対象 a の合計）。"""
    return ConstraintSet(
        frozenset((i, a) for i in range(n_agents)), floor, ceil, name or f"列{a}"
    )


def subcolumn(a: int, agents: list[int], floor: int, ceil: int | None,
              name: str = "") -> ConstraintSet:
    """部分列制約 N'×{a}。グループ別クォータ（アファーマティブ・アクション）に対応。"""
    return ConstraintSet(
        frozenset((i, a) for i in agents), floor, ceil, name or f"部分列{a}{agents}"
    )


def subrow(i: int, objects: list[int], floor: int, ceil: int | None,
           name: str = "") -> ConstraintSet:
    """部分行制約 {i}×O'。時間割・カリキュラム制約に対応。"""
    return ConstraintSet(
        frozenset((i, a) for a in objects), floor, ceil, name or f"部分行{i}{objects}"
    )
```

### bihierarchy の判定

ここが実装として一番おもしろいところです。「2つの階層に分割できるか」を素直に探索すると $2^{|\mathcal{H}|}$ 通りですが、**グラフの2彩色に帰着できます**。

同じ階層に入れられないのは「交差する（共通部分を持つがどちらも他方を含まない）」ペアだけです。そこで

- 頂点 = 制約集合
- 辺 = 交差するペア

という**交差グラフ**を作れば、

$$\mathcal{H} \text{ が bihierarchy} \iff \text{交差グラフが2部グラフ}$$

となり、BFS による2彩色で $O(|\mathcal{H}|^2)$ で判定できます。

```python
from itertools import combinations


def crosses(s: frozenset[Cell], t: frozenset[Cell]) -> bool:
    """S と T が「交差する」（共通部分を持つがどちらも他方を含まない）か。"""
    if s.isdisjoint(t):
        return False
    return not (s <= t or t <= s)


def is_hierarchy(sets: list[ConstraintSet]) -> bool:
    """階層かどうか。"""
    return not any(crosses(s.cells, t.cells) for s, t in combinations(sets, 2))


def find_bihierarchy(
    structure: ConstraintStructure,
) -> tuple[list[ConstraintSet], list[ConstraintSet]] | None:
    """H を2つの階層 H1, H2 に分割する。不可能なら None。"""
    sets = structure.sets
    m = len(sets)

    # 交差グラフを作る
    adjacency: list[list[int]] = [[] for _ in range(m)]
    for u, v in combinations(range(m), 2):
        if crosses(sets[u].cells, sets[v].cells):
            adjacency[u].append(v)
            adjacency[v].append(u)

    # 2彩色（BFS）。同色の隣接が見つかったら奇数長の閉路 → 2彩色不能
    color = [-1] * m
    for start in range(m):
        if color[start] != -1:
            continue
        color[start] = 0
        queue = [start]
        while queue:
            u = queue.pop()
            for v in adjacency[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return None
    return (
        [s for s, c in zip(sets, color) if c == 0],
        [s for s, c in zip(sets, color) if c == 1],
    )
```

`crosses` が `s <= t` という集合の包含演算子だけで書けているのが、`frozenset` にした恩恵です。

### メインアルゴリズム：一般化BvN分解

前回の BvN は「台集合から完全マッチングを1つ見つけて最小重みを引く」でした。今回は制約が任意なので、**ポリトープの頂点に向かって動かす**という別のアプローチを取ります。

考え方はこうです。期待割当 $X$ は、次のポリトープの点になっています。

$$P = \Big\{ X' \;\Big|\; \lfloor x_S \rfloor \le \sum_{(i,a)\in S} x'_{ia} \le \lceil x_S \rceil,\ \forall S \in \mathcal{H} \Big\}$$

$P$ は有界なので、その中の任意の点は**頂点の凸結合**で書けます。そして bihierarchy なら $P$ の頂点はすべて整数点（＝純割当）です。したがって「$X$ を頂点の凸結合に書く」ことができれば分解完了です。

:::note info
**なぜ bihierarchy だと頂点が整数点になるのか（定理1の証明の骨子）**

制約構造を、行＝セル $(i,a)$・列＝制約集合 $S$ の **接合行列** $Y$ で表します（$(i,a) \in S$ なら1、そうでなければ0）。

1. **Hoffman–Kruskal (1956)**：$Y$ が**完全単模**（totally unimodular：任意の正方部分行列の行列式が $0, \pm1$ のいずれか）$\iff$ $P$ の頂点がすべて整数点
2. **Edmonds (1970)**：制約構造が bihierarchy なら $Y$ は完全単模

この2つをつなぐと「bihierarchy $\Rightarrow$ 頂点が整数点 $\Rightarrow$ 整数の純割当の凸結合で書ける」が出ます。**bihierarchy という条件は、突き詰めると「係数行列が完全単模になるための組合せ的な十分条件」**なのです。行と列を2つの階層に分ける、という一見不思議な条件がなぜ効くのか、その正体がここにあります。
:::

手順は次の4ステップ。

1. **動かせる方向 $d$ を探す**。整数になっているセルは固定し、和がすでに整数の制約はその和を変えない（$\sum_S d = 0$）。これは連立一次方程式の**零空間ベクトル**を求めるのと同じ。
2. $d = 0$ しかなければ、$X$ は頂点＝**すでに純割当**。終了。
3. $d \ne 0$ なら、$X + \alpha d$ と $X - \beta d$ が実行可能な最大の $\alpha, \beta > 0$ を取り、$\gamma = \beta/(\alpha+\beta)$ として
   $$X = \gamma (X + \alpha d) + (1-\gamma)(X - \beta d)$$
4. 両枝を**再帰的に**分解し、重みを掛け合わせて併合。

ステップ3の $\alpha, \beta$ の取り方から「少なくとも1つの制約集合の和が新たに整数になる」ことが保証され、整数だった集合は整数のままなので、**有限回で必ず終了**します。

```python
@dataclass
class Term:
    """分解の1項：重み λ と純割当（整数行列）。"""

    weight: Fraction
    assignment: list[list[int]]


def generalized_bvn(
    matrix: list[list],
    structure: ConstraintStructure,
    *,
    check_bihierarchy: bool = True,
) -> list[Term]:
    """期待割当 X を、制約を満たす純割当の凸結合に分解する。"""
    X: Matrix = [[Fraction(str(x)) if isinstance(x, float) else Fraction(x) for x in r]
                 for r in matrix]

    violations = satisfies_quotas(X, structure)
    if violations:
        raise ValueError("期待割当がクォータを満たしていません:\n  " + "\n  ".join(violations))

    if check_bihierarchy and find_bihierarchy(structure) is None:
        raise ValueError("制約構造が bihierarchy ではありません（定理1の十分条件を満たさない）。")

    terms: list[Term] = []
    _decompose(X, structure, Fraction(1), terms)
    return _merge(terms)


def _decompose(X, structure, weight, out) -> None:
    """X を再帰的に分解し、純割当と重みを out に積む。"""
    direction = _find_direction(X, structure)
    if direction is None:                       # 頂点＝純割当に到達
        out.append(Term(weight, [[int(x) for x in r] for r in X]))
        return

    alpha = _max_step(X, structure, direction, +1)
    beta = _max_step(X, structure, direction, -1)
    gamma = beta / (alpha + beta)

    _decompose(_shift(X, direction, alpha), structure, weight * gamma, out)
    _decompose(_shift(X, direction, -beta), structure, weight * (1 - gamma), out)
```

方向 $d$ の探索は、分数セルを変数とする連立一次方程式の零空間を厳密ガウス消去で解きます。

```python
def _find_direction(X, structure) -> dict[Cell, Fraction] | None:
    """整数セルを固定し、整数和の制約を保つ移動方向 d ≠ 0 を1つ返す。無ければ None。"""
    free = [(i, a) for i in range(len(X)) for a in range(len(X[0]))
            if X[i][a].denominator != 1]          # 分数セルだけを変数にする
    if not free:
        return None
    index = {cell: k for k, cell in enumerate(free)}

    # 和がすでに整数の制約 → その和を変えない（等式制約）
    rows: list[list[Fraction]] = []
    for cs in structure.sets:
        if cs.total(X).denominator != 1:
            continue
        vec = [Fraction(0)] * len(free)
        touched = False
        for cell in cs.cells:
            if cell in index:
                vec[index[cell]] = Fraction(1)
                touched = True
        if touched:
            rows.append(vec)

    null = _null_space_vector(rows, len(free))
    if null is None:
        return None
    return {cell: null[k] for k, cell in enumerate(free) if null[k] != 0}


def _max_step(X, structure, d, sign) -> Fraction:
    """X + sign·t·d が ⌊x_S⌋ ≤ · ≤ ⌈x_S⌉ を保つ最大の t。"""
    best: Fraction | None = None
    for cs in structure.sets:
        delta = sum((d.get(cell, Fraction(0)) for cell in cs.cells), Fraction(0)) * sign
        if delta == 0:
            continue
        total = cs.total(X)
        if delta > 0:
            bound = (Fraction(math.ceil(total)) - total) / delta
        else:
            bound = (Fraction(math.floor(total)) - total) / delta
        best = bound if best is None else min(best, bound)
    return best if best is not None else Fraction(0)
```

:::note warn
**計算量の注意**
各ステップで「新たに整数になる制約集合が1つ以上増える」ため、再帰の深さは高々 $|\mathcal{H}|$ です。ただし本実装は**両枝を展開する**ので、項数は最悪 $2^{|\mathcal{H}|}$ になりえます。論文の多項式時間アルゴリズムは各分岐で乱数を引いて片枝だけを辿り、純割当を**1つサンプリング**する方式です。「実際に配る」だけならそちらで十分で、全分解が要るのは検証目的のときだけです。
:::

分解結果の検証には、再構成の一致と全項の制約適合をまとめて確認する関数を用意しました。

```python
def verify(terms: list[Term], X: list[list], structure: ConstraintStructure) -> list[str]:
    """分解の妥当性を検査し、問題点のリストを返す（空なら正常）。"""
    problems: list[str] = []
    total = sum((t.weight for t in terms), Fraction(0))
    if total != 1:
        problems.append(f"重みの総和が1でない: {frac_str(total)}")

    target = [[Fraction(str(x)) if isinstance(x, float) else Fraction(x) for x in r] for r in X]
    if reconstruct(terms) != target:
        problems.append("再構成した行列が元の期待割当と一致しない")

    for k, t in enumerate(terms, 1):
        pure: Matrix = [[Fraction(v) for v in r] for r in t.assignment]
        for v in satisfies_quotas(pure, structure):
            problems.append(f"第{k}項が制約違反 → {v}")
    return problems
```

## 動作確認

### 【例1】多対1割り当て：学校選択

**行和は1のまま、列和は定員に変え、さらに列の内部に制約を入れます。**

- 学生4人（`i0..i3`）× 学校3校（`o0, o1, o2`）
- 各学生はちょうど1校 → 行制約 $[1,1]$
- `o0` の定員2、`o1`・`o2` の定員1 → 列制約
- **`o0` は $\{i_0,i_1\}$ からちょうど1人取る** → 部分列制約（アファーマティブ・アクション型）

<details><summary><b>テストケース</b></summary>

```python
n, m = 4, 3
X = [
    [F(1, 2), F(1, 5), F(3, 10)],
    [F(1, 2), F(1, 2), F(0)],
    [F(4, 5), F(0),    F(1, 5)],
    [F(1, 5), F(3, 10), F(1, 2)],
]
structure = ConstraintStructure(
    n, m,
    [row(i, m, 1, 1) for i in range(n)]
    + [column(0, n, 0, 2), column(1, n, 0, 1), column(2, n, 0, 1)]
    + [subcolumn(0, [0, 1], 1, 1, name="部分列 o0×{i0,i1}")],
).with_singletons(0, 1)

terms = generalized_bvn(X, structure)
```

</details>
<br>

```bash
【期待割当 X】
  [   1/2    1/5   3/10 ]
  [   1/2    1/2      0 ]
  [   4/5      0    1/5 ]
  [   1/5   3/10    1/2 ]

  → bihierarchy（H1: 16集合 / H2: 4集合）
  分解された純割当の数: 5
  【第1項】 λ = 5/14
    [     1      0      0 ]
    [     0      1      0 ]
    [     1      0      0 ]
    [     0      0      1 ]
  【第2項】 λ = 3/10
    [     0      0      1 ]
    [     1      0      0 ]
    [     1      0      0 ]
    [     0      1      0 ]
  【第3項】 λ = 1/7
    [     1      0      0 ]
    [     0      1      0 ]
    [     0      0      1 ]
    [     1      0      0 ]
  【第4項】 λ = 1/7
    [     0      1      0 ]
    [     1      0      0 ]
    [     1      0      0 ]
    [     0      0      1 ]
  【第5項】 λ = 2/35
    [     0      1      0 ]
    [     1      0      0 ]
    [     0      0      1 ]
    [     1      0      0 ]
  検証: すべて OK（再構成一致・全項が制約を満たす）
```

**正方行列でも二重確率行列でもない期待割当が、確定的な割り当てのくじに分解できました。** 多対1の割り当て問題が解けたことになります。

各項を確認すると、確かに

- 各行の1は1つ（各学生ちょうど1校）
- `o0` 列の合計は2以下、`o1`・`o2` 列は1以下
- **`o0` 列の上2セル（$i_0, i_1$）の合計は必ずちょうど1**

を満たしています。第1項では $i_0$ と $i_2$ が `o0` に入っていますが、$i_1$ は入っていません。部分列制約が全項で効いています。

:::note info
**なぜこれが bihierarchy なのか**

部分列は列の**部分集合**なので、列制約と入れ子関係にあります。互いに素な部分列同士なら重なりません。したがって

$$\mathcal{H}_2 = \{\text{列}, \text{部分列}, \text{単集合}\}$$

は依然として階層のままです。**多対1で変わるのはクォータの数値だけで、集合の族の形は変わらない。** これが「1対1が解けるなら多対1も解ける」ことの本質です。
:::

実際の制度でいうと、この部分列制約は次のようなものに対応します。

- ソウル市の学校選択制（学区外からの応募比率の上限）
- 日本の複数の学校選択制（居住地域別クォータ）
- ニューヨーク市 Educational Option プログラム（学力層のミックス）

### 【例2】一気通貫：一般化PSメカニズム → 一般化BvN分解

前回は「PS → BvN」のパイプラインを作りました。今回は制約付き版で同じことをします。

設定は次の通りです。

- 学生4人 × 学校 `a`（定員2）・`b`（定員1）・`∅`（無制限）
- `a` に部分列クォータ $S = \{(1,a),(2,a),(3,a)\}$、上限1
- 選好：学生1,2 は $a \succ b \succ \emptyset$、学生3,4 は $b \succ a \succ \emptyset$

一般化PSメカニズムは、前回のPSから**「利用可能（available）」の定義だけを変えた**ものです。

:::note info
対象 $a$ が個人 $i$ に**利用可能** $\iff$ $(i,a) \in S$ なるすべての制約集合 $S$ について、$S$ 上の累積消費量が上限 $\bar q_S$ **未満**

前回は「$a$ が残っているか」だけを見ていたのを、「$(i,a)$ に関わる**すべて**の制約に余裕があるか」に拡張しただけです。
:::

イーティングの経過はこうなります。

| 時刻    | 起きること                                                              |
| ------- | ----------------------------------------------------------------------- |
| $t=0$   | 1,2 が `a` を、3,4 が `b` を食べ始める                                  |
| $t=1/2$ | 部分列 $S$ の上限1 と `b` の定員1 が**同時に**拘束                      |
| $t>1/2$ | **学生4だけ**が `a` を食べられる（4は $S$ に属さない）。1,2,3 は `∅` へ |

<details><summary><b>テストケース</b></summary>

```python
# 対象の並び: [a, b, ∅]
n, m = 4, 3
X = [
    [F(1, 2), F(0),    F(1, 2)],
    [F(1, 2), F(0),    F(1, 2)],
    [F(0),    F(1, 2), F(1, 2)],
    [F(1, 2), F(1, 2), F(0)],
]
structure = ConstraintStructure(
    n, m,
    [row(i, m, 1, 1) for i in range(n)]
    + [column(0, n, 0, 2, name="列 a(定員2)"), column(1, n, 0, 1, name="列 b(定員1)")]
    + [subcolumn(0, [0, 1, 2], 0, 1, name="部分列 a×{1,2,3}")],
    # ∅ 列は上限なし（列制約を課さない）
).with_singletons(0, 1)

terms = generalized_bvn(X, structure)
```

</details>
<br>

```bash
【一般化PSの期待割当 PS(≻)】（列は a, b, ∅ の順）
  [   1/2      0    1/2 ]
  [   1/2      0    1/2 ]
  [     0    1/2    1/2 ]
  [   1/2    1/2      0 ]

  → bihierarchy（H1: 16集合 / H2: 3集合）
  分解された純割当の数: 4
  【第1項】 λ = 1/4
    [     1      0      0 ]
    [     0      0      1 ]
    [     0      0      1 ]
    [     0      1      0 ]
  【第2項】 λ = 1/4
    [     1      0      0 ]
    [     0      0      1 ]
    [     0      1      0 ]
    [     1      0      0 ]
  【第3項】 λ = 1/4
    [     0      0      1 ]
    [     1      0      0 ]
    [     0      0      1 ]
    [     0      1      0 ]
  【第4項】 λ = 1/4
    [     0      0      1 ]
    [     1      0      0 ]
    [     0      1      0 ]
    [     1      0      0 ]
  検証: すべて OK（再構成一致・全項が制約を満たす）
```

`∅` 列を落として正方化するといった**前処理が一切不要**になった点に注目してください。前回は「∅ 列をそのまま落とせる条件」という注意書きが必要でしたが、今回は `∅` を「列制約を課さない列」として素直に扱えています。制約構造という抽象化の効き目です。

:::note info
**一般化PSの性質**

| 性質             | 結果  | 補足                                                                       |
| ---------------- | :---: | -------------------------------------------------------------------------- |
| 実装可能性       |   ✅   | 定理1から即座に従う（系2）                                                 |
| 順序効率性       |   ✅   | 制約内での効率性。実現するどの純割当も事後的にパレート効率的（定理3）      |
| 制約付き無羨望性 |   ✅   | $i$ が $j$ を羨むなら、$i$ だけが直面する拘束された制約が存在する（定理4） |
| 弱耐戦略性       |   ✅   | 虚偽申告で真の申告を確率支配することはできない（定理5）                    |

**定理4の読み方が重要です。** この例では学生1,2,3 が学生4を羨みます。しかしそれは「部分列制約が 1,2,3 だけに課されている」からであって、設計者が意図的に一方を優遇している以上、規範的には問題ありません。逆に「制約が弱い側が強い側を羨む」ことは起きません。なおRP（ランダム逐次独裁）は、この制約付き無羨望性すら満たしません。
:::

## まとめ：多対1の限界と、その境界線

ここまでで、多対1の割り当て問題が解けることを実装で確認しました。要点は3つです。

- 【**データ構造**】制約を「セルの集合＋整数の上下限」で表現する。行も列も部分列も同じ形で書ける
- 【**判定**】bihierarchy かどうかは**交差グラフの2彩色**で $O(|\mathcal{H}|^2)$ 判定できる
- 【**分解**】ポリトープの零空間ベクトルを求めて両側に振り、再帰する。前回の「完全マッチングを引く」方式より汎用的

理解の要点を1つだけ挙げるなら、これです。

> **多対1が難しいのではなく、1対1で「行和=1、列和=1」に固定していたのが特殊すぎた。**
> 多対1で変わるのはクォータの数値だけで、集合の族の形（階層性）は変わらない。だから同じ定理がそのまま効く。

**——ただし、実は多対1の割り当て問題には限界があり、その境界線もはっきり分かっています。** 最後にその話をして終わります。

### 境界線①：bihierarchy を外れると解けない

定理1は「bihierarchy なら解ける」という**十分条件**でした。では bihierarchy でなければ解けないのか。答えは、行制約と列制約をすべて含む自然な設定（正準二部制約構造）では**そのとおり**です。

:::note info
**定理2（必要性）**：正準二部制約構造が bihierarchy でないなら、実装可能でない。
:::

$$\boxed{\text{正準二部構造では、bihierarchy は「解ける」ことの必要十分条件}}$$

つまり**これ以上の一般化は存在しない**、というのが論文の到達点です。実際に解けない最小例を見てみます。

- 2人 × 2対象
- 第1行 $\{(0,0),(0,1)\}$、第1列 $\{(0,0),(1,0)\}$、**対角集合** $\{(0,1),(1,0)\}$
- いずれも下限=上限=1

3つはどの2つも交差するので、同じ階層に入れられません。期待割当を全セル $1/2$ にすると、クォータは期待値では満たされるのに実装できません。

1. 実装くじは $\underline x_{00} = 1$ となる純割当を正の確率で選ばねばならない
2. 第1行の上限1より $\underline x_{01} = 0$
3. 対角集合の**下限1**より $\underline x_{10} = 1$
4. すると第1列の和が $1 + 1 = 2$ で上限1に違反。**矛盾**

期待値では $0.5$ ずつでつじつまが合っているのに、整数に落とした瞬間に破綻します。「期待割当がクォータを満たすことは必要だが十分ではない」ということの具体的な姿です。

### 境界線②：解けないことの証拠は「奇サイクル」

「bihierarchy でない」だけでは、それが本当に解けない理由を説明したことになりません。その証拠にあたるのが**奇サイクル**です。

:::note info
**奇サイクル（定義4）**
奇数個の制約集合 $(S_1,\dots,S_l)$ と対の列 $(s_1,\dots,s_l)$ が存在し、各 $i$ について
$$s_i \in S_i \cap S_{i+1}\ (\text{添字は巡回}) \quad\text{かつ}\quad s_i \notin S_j\ (j \ne i, i+1)$$

**補題1**：奇サイクルを含む制約構造は実装不可能。
:::

上の例で「第1行・第1列・対角集合」が輪になって交差していたのが、まさに長さ3の奇サイクルです。実装は集合演算そのままで、たった3行で書けます。

```python
def find_odd_cycle(structure: ConstraintStructure) -> list[ConstraintSet] | None:
    """長さ3の奇サイクルを1つ探す。見つかれば実装不可能（補題1）。"""
    for s1, s2, s3 in combinations(structure.sets, 3):
        a, b, c = s1.cells, s2.cells, s3.cells
        if (a & b) - c and (b & c) - a and (a & c) - b:
            return [s1, s2, s3]
    return None
```

「$S_1 \cap S_2$ にあって $S_3$ にない要素が存在する」を3通り確認するだけです。先ほどの例にかけると、次のように証拠を返してくれます。

```bash
  → bihierarchy ではない
  → 奇サイクルを検出（補題1: 実装不可能）
      第1行 = [(0, 0), (0, 1)]
      第1列 = [(0, 0), (1, 0)]
      対角集合 = [(0, 1), (1, 0)]
```

:::note warn
**身近な例：制約が交差した瞬間に壊れる**

- 時間割制約 $\{f_1,m_1\},\{f_2,m_2\}$ と分野制約 $\{f_1,f_2\},\{m_1,m_2\}$ を**同時に**課す
- 同一の学校に人種クォータと性別クォータを**重ねて**課す

どちらも交差するので bihierarchy が壊れます。「うっかり制約を足したら解けなくなっていた」を、`find_bihierarchy()` と `find_odd_cycle()` で**機械的に検出できる**ようになったのが実装上の収穫です。
:::

### 境界線③：3部以上は原理的に解けない

多対1・多対多は解けました。では「学生 / 学校 / 放課後プログラム」のような**3部**はどうか。ここが最後の境界線です。

3部の割当は三つ組 $(i,a,l)$ になり、自然な制約構造は次の3種類を必ず含みます。

$$S_i = \{i\}\times O \times L, \quad S_a = N\times\{a\}\times L, \quad S_l = N \times O \times \{l\}$$

$|N|,|O|,|L| \ge 2$ なら、$i'\ne i,\ a'\ne a,\ l'\ne l$ を取ると

$$(i,a,l') \in S_i \cap S_a \setminus S_l,\quad (i,a',l) \in S_i \cap S_l \setminus S_a,\quad (i',a,l) \in S_a \cap S_l \setminus S_i$$

となり、$(S_i, S_a, S_l)$ が**必ず**長さ3の奇サイクルになります。つまり**どう設計しても解けません**（定理12）。同じ論法で、3人以上の**ルームメイト問題**（任意の2人が組める。ペアワイズ腎臓交換など）も不可能です（定理13）。

$$\boxed{\text{BvN 的な「期待割当を先に設計する」アプローチは、本質的に二部構造までが限界}}$$

:::note info
**契約付きマッチングは3部ではない**

Hatfield–Milgrom (2005) の「契約付きマッチング」（労働者・企業・契約条件）は一見3部に見えますが違います。契約条件の集合 $L$ について「各契約条件が誰かに選ばれねばならない」という制約 $N\times O\times\{l\}$ は存在しないからです。対象集合を $O' = O \times L$ と再定義すれば、**二部の枠にきれいに収まります**。
:::

### おわりに

まとめると、境界線はこうなります。

| 問題 | 解けるか | 理由 |
| --- | :---: | --- |
| 1対1（二重確率行列） | ✅ | bihierarchy の特殊ケース（系1＝BvN定理） |
| **多対1**（定員＋グループ別クォータ） | ✅ | 部分列は列と入れ子なので階層のまま |
| 多対多（履修割当） | ✅ | 部分行が階層をなす限り |
| 交差する制約を同時に課す | ❌ | 奇サイクル（補題1） |
| 3部以上・ルームメイト | ❌ | 必ず奇サイクルを含む（定理12・13） |

「何ができるか」だけでなく「何ができないか」まで、コードで機械的に判定できるようになったことが今回いちばんの収穫だと感じています。なお本記事では触れませんでしたが、論文には「実装可能なくじの中から、事後的に公平なものを選ぶ」手法（効用保証・定理9）も用意されています。機会があれば別記事で扱いたいです。

以上になります。
最後まで読んでいただきありがとうございました。

## 参考文献

- [マッチング理論とマーケットデザイン](https://www.amazon.co.jp/dp/453555935X)
- Hoffman, A. J. and J. B. Kruskal (1956) "Integral Boundary Points of Convex Polyhedra," in *Linear Inequalities and Related Systems*, Princeton University Press.
- Edmonds, J. (1970) "Submodular Functions, Matroids, and Certain Polyhedra," in *Combinatorial Structures and Their Applications*.
- Hatfield, J. W. and P. Milgrom (2005) "Matching with Contracts," *American Economic Review*, 95(4), pp.913–935.
