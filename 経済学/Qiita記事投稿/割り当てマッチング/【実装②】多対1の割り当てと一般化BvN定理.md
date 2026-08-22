## はじめに

> 本記事は [Budish, Che, Kojima and Milgrom (2013)](https://static1.squarespace.com/static/5e56e1139e190014f1116cac/t/5e5c89d29d9d61249de4e77b/1583122898804/budish-che-kojima-milgrom-2013-aer.pdf)（2026/08/17時点） の内容になります。ただ、理論の証明には深入りせず、**実装をメイン**に扱います。

<!-- バナー画像をここに貼る（例: 2GBvN.png）。前作の RP_PS_mechanism.png と同じ要領で Qiita にアップロードしてURLを差し込む -->
![](RP_PS_mechanism.png)

前回はRP・PSメカニズムで確率行列を求め、バーコフ＝フォン・ノイマンの定理（以下$\text{BvN}$）で実際の割り当てに変換するところまでを実装しました。**本記事では多対一の割り当て問題を取り扱います**。具体的には、**二重階層（$\text{bihierarchy}$）** という条件を満たす制約構造であれば、正方行列でなくても、二重確率行列（行和と列和がともに1）でなくても確定的な割り当てのくじに分解できることを示し、また割り当て問題として「どこまで解けるのか」も示します。

- 【**想定する読者**】マッチング理論の初学者エンジニア
- 【**準備**】マッチング理論 〜割り当て問題の共有知識〜
- 【**実装①**】RP・PSメカニズムと実際の割り当て
- 【**実装②**】多対1の割り当てと一般化BvN定理 ← <font color=red><b>今回はここ！</b></font>
- [サンプルコード](https://github.com/itokohei0/MarketDesignStudy/tree/master/%E3%83%9E%E3%83%83%E3%83%81%E3%83%B3%E3%82%B0%E7%90%86%E8%AB%96)

<font color=red>1エンジニアの独学で作った記事なので間違った内容を含むと思います。遠慮なくコメントいただけますと幸いです。</font>

### この記事のゴール

前回の BvN 実装（`bvn_algorithm.py`）は、入力を「正方の二重確率行列」に限定していました。今回作る `generalized_bvn_algorithm.py` は、**制約構造**という抽象化を導入することで、その制限を外します。

```mermaid
---
title: 前回と今回の守備範囲
---

flowchart LR
  A["選好の申告"] -->|"拡張PS<br>（実装②）"| D["期待割当"]
  D -->|"一般化BvN定理<br>（実装②）"| E["純割当のくじ"]
  style D fill:#aaf
  style E fill:#aaf
```

実装するのは次の4つです。

|     | やること                             | 対応する概念                                       |
| --- | ------------------------------------ | -------------------------------------------------- |
| 1   | 制約付きで期待割当を求める           | 拡張PSメカニズム（**PSへの挿入2箇所**）            |
| 2   | 制約をデータ構造で表現する           | 制約構造 $\mathcal{H}$                             |
| 3   | 「解けるかどうか」を機械的に判定する | $\text{bihierarchy}$ 判定（**交差グラフの2彩色**） |
| 4   | 期待割当を純割当のくじに分解する     | 一般化BvN分解                                      |

コードはすべて `fractions.Fraction` で厳密計算し、**標準ライブラリのみ**で動きます（Python 3.10+）。

:::note info
**用語について：「確率行列」から「期待割当」へ**

前回まで真ん中の行列を**確率行列**と呼んでいましたが、今回から**期待割当（expected assignment）** と呼び方を変えます。

1対1では各成分が「個人 $i$ が財 $a$ をもらう**確率**」でした。しかし多対1では定員が2以上になるため、各成分は「個人 $i$ が財 $a$ を受け取る**期待個数**」と解釈するのが自然になります（原論文もこの理由で用語を変えています）。

同じ理由で、分解して得られる確定的な割り当ても、1対1の**置換行列**ではなく、より一般的な**純割当（pure assignment）＝整数行列**と呼びます。
:::

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

### 拡張PSメカニズム ── PSへの挿入は2箇所だけ

まず、制約のもとで期待割当を求めるメカニズムを作ります。前回のPSメカニズムを**拡張PSメカニズム**にしますが、変更はごくわずかです。

理論的な違いは1点に集約できます。

|                    | 「食べられる」の判定                                             |
| ------------------ | ---------------------------------------------------------------- |
| PS（前回）         | その財が残っているか                                             |
| **拡張PS（今回）** | その財が残っている **かつ** $(i,a)$ に関わる全制約に余地があるか |

前回は「$a$ が残っているか」だけを見ていたのを、「$(i,a)$ に関わる**すべて**の制約に余裕があるか」に広げただけです。コードもこの通りになります。

#### 入力に制約を足す

まず制約を表す型を用意し、前回の `Input` に1つフィールドを足します。

```python
@dataclass(frozen=True)
class Constraint:
    """上限制約集合 S：ペア (個人 i, 財 a) の集合とその和の上限 q̄_S。【拡張で追加】"""

    pairs: frozenset[tuple[int, str]]
    upper: int
    label: str = ""


@dataclass
class ConstrainedInput:
    """前回の Input に上限制約を足しただけ。"""

    prefs: list[list[str]]
    capacities: dict[str, int]
    constraints: list[Constraint] = field(default_factory=list)   # 【拡張で追加】
    agent_names: list[str] | None = None
    agent_label: str = "個人"
    object_label: str = "財"
    goods: list[str] = field(default_factory=list)
    # 以降のメソッド（columns / acceptable_pref / name）は前回と同一
```

たとえば「学校 a は 学生1,2,3 から高々1人しか取らない」という制約はこう書けます。

```python
Constraint(
    pairs=frozenset({(0, "a"), (1, "a"), (2, "a")}),
    upper=1,
    label="学校a は 学生1,2,3 から高々1人",
)
```

#### 挿入①：食べる財を選ぶとき、制約に余地があるかも見る

```python
# 前回（PS）
if amt is not None and amt > 0:
    alloc[agent] = item
    break

# 今回（拡張PS）── 追加は末尾の and 以降だけ
if amt is not None and amt > 0 and _within_constraints(data, agent, item, rows, col_index):
    alloc[agent] = item
    break
```

判定関数の中身は素直です。

```python
def _within_constraints(data, agent, item, rows, col_index) -> bool:
    """(agent, item) を含む全ての上限制約にまだ余地があるか。【拡張で追加】"""
    for S in data.constraints:
        if (agent, item) in S.pairs:
            cur = sum((rows[i][col_index[a]] for (i, a) in S.pairs), Fraction(0))
            if cur >= S.upper:
                return False
    return True
```

#### 挿入②：Δt の計算に「制約が飽和する時刻」も加える

前回のPSは「次にどれかの財が食べ尽くされるまで」時間を一気に進めていました。今回は「**制約が上限に達するまで**」もイベントに含める必要があります。

```python
        dt = end - t
        for good in set(alloc):                    # ← ここまでは前回と同じ
            amt = remaining[good]
            if amt is not None:
                dt = min(dt, amt / alloc.count(good))
        for S in data.constraints:                 # 【拡張で追加】
            rate = sum(1 for i, good in enumerate(alloc) if (i, good) in S.pairs)
            if rate > 0:
                cur = sum((rows[i][col_index[a]] for (i, a) in S.pairs), Fraction(0))
                dt = min(dt, (Fraction(S.upper) - cur) / rate)
```

`rate` は「いまその制約の中の財を食べている人数」です。`(上限 − 現在値) ÷ rate` で、その制約が飽和するまでの時間が出ます。

:::note info
**挿入は本当に2箇所だけ**

`extended_ps_algorithm.py` は `ps_algorithm.py` と独立に動きますが、両者を差分で比較できるようにしてあります。

```bash
diff -u ps_algorithm.py extended_ps_algorithm.py   # 差分を確認する
grep 【拡張で追加】 extended_ps_algorithm.py        # 拡張点を一覧する
```

アルゴリズム本体で `【拡張で追加】` が付いているのは、上の挿入①②と `_within_constraints()` だけです。
:::

#### 動かしてみる

学生4人、学校 `a`（定員2）・`b`（定員1）、`a` には「学生1,2,3 から高々1人」という制約を置きます。選好は学生1,2 が `a ≻ b ≻ ∅`、学生3,4 が `b ≻ a ≻ ∅` です。

イーティングの経過はこうなります。

| 時刻    | 起きること                                                           |
| ------- | -------------------------------------------------------------------- |
| $t=0$   | 1,2 が `a` を、3,4 が `b` を食べ始める                               |
| $t=1/2$ | 制約の上限1 と `b` の定員1 が**同時に**拘束（挿入②が効く）           |
| $t>1/2$ | **学生4だけ**が `a` を食べられる（4は制約の対象外）。1,2,3 は `∅` へ |

```bash
【学生の選好（左ほど希望が高い）】
  学生1: a, b, ∅
  学生2: a, b, ∅
  学生3: b, a, ∅
  学生4: b, a, ∅

【学校の供給数（必要人数）】
  a: 2人, b: 1人

【追加の制約】
  - 学校a は 学生1,2,3 から高々1人

=== 拡張PSメカニズムの期待行列 ===
               a       b       ∅
学生1        1/2       0     1/2
学生2        1/2       0     1/2
学生3          0     1/2     1/2
学生4        1/2     1/2       0
  ------------------------------
期待人数     3/2       1     3/2

【制約充足】✅ 成立
```

期待割当が求まりました。ただし成分に $\frac{1}{2}$ が残っているので、**このままでは配れません**。ここから先が本題です。

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

### アダプタ ── 拡張PSと一般化BvNを繋ぐ

最後に、拡張PSの出力を一般化BvNに渡すための変換関数を書きます。両者は制約の持ち方が違うためです。

|                              | 財の表現            | 制約       |
| ---------------------------- | ------------------- | ---------- |
| 拡張PS（`Constraint`）       | **文字列**（`"a"`） | 上限のみ   |
| 一般化BvN（`ConstraintSet`） | **列 index**（`0`） | 下限＋上限 |

変換の中身が、そのまま**この記事の主題**になっています。

```python
def from_constrained_input(data, matrix) -> tuple[Matrix, ConstraintStructure]:
    """拡張PSの入出力を、一般化BvN が受け取る形（期待割当＋制約構造）に変換する。"""
    columns = matrix.columns                       # [財..., ∅]
    col_index = {c: k for k, c in enumerate(columns)}
    n, m = len(matrix.rows), len(columns)

    X = [[Fraction(v) for v in row] for row in matrix.rows]
    sets: list[ConstraintSet] = []

    # 各人ちょうど1つ（∅ を含めて行の和は必ず 1）
    sets += [row(i, m, 1, 1, name=f"行{i}(各人1つ)") for i in range(n)]

    # 財の供給数（∅ 列には制約を課さない）
    for a in data.goods:
        sets.append(column(col_index[a], n, 0, data.capacities[a],
                           name=f"列{a}(供給{data.capacities[a]})"))

    # 追加の上限制約（下限は 0）
    for S in data.constraints:
        sets.append(ConstraintSet(
            frozenset((i, col_index[a]) for (i, a) in S.pairs),
            0, S.upper, name=S.label,
        ))

    return X, ConstraintStructure(n, m, sets).with_singletons(0, 1)
```

:::note info
**この関数が「制約構造」という考え方そのもの**

前回まで**暗黙のルール**だったものが、今回はすべて**同じ型の制約集合**になっています。

| 前回は暗黙だったもの     | 今回の書き方                   |
| ------------------------ | ------------------------------ |
| 各人ちょうど1つ          | `row(i, m, 1, 1)`              |
| 財 $a$ の供給数 $q_a$    | `column(a, n, 0, q_a)`         |
| グループ別クォータ       | `ConstraintSet(..., 0, upper)` |
| 1人が同じ財を2つ取らない | 単集合制約 `[0, 1]`            |
| ∅ は無制限               | 制約を課さない                 |

「行の和も列の和もグループ別クォータも、**全部同じ `ConstraintSet` で書ける**」——これが制約構造という抽象化の正体です。
:::

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

### 【例2】一気通貫：選好 → 拡張PS → 一般化BvN

例1では期待割当と制約構造を手で組み立てました。ここでは**選好から出発**して、最後の「くじ」まで一気に通します。前回の「PS → BvN」と同じパイプラインです。

<details><summary><b>テストケース</b></summary>

```python
from extended_ps_algorithm import EMPTY, Constraint, ConstrainedInput, extended_probabilistic_serial
from generalized_bvn_algorithm import from_constrained_input, generalized_bvn, verify

data = ConstrainedInput(
    prefs=[
        ["a", "b", EMPTY],   # 学生1
        ["a", "b", EMPTY],   # 学生2
        ["b", "a", EMPTY],   # 学生3
        ["b", "a", EMPTY],   # 学生4
    ],
    capacities={"a": 2, "b": 1},
    constraints=[
        Constraint(
            pairs=frozenset({(0, "a"), (1, "a"), (2, "a")}),
            upper=1,
            label="学校a は 学生1,2,3 から高々1人",
        )
    ],
    agent_names=["学生1", "学生2", "学生3", "学生4"],
    agent_label="学生",
    object_label="学校",
)

matrix = extended_probabilistic_serial(data)          # ステップ1: 選好 → 期待割当
X, structure = from_constrained_input(data, matrix)   # ステップ2: 制約構造に変換
terms = generalized_bvn(X, structure)                 # ステップ3: 純割当のくじに分解
```

</details>
<br>

**実行結果**

```bash
─── ステップ2: 制約構造に変換する ───

  制約集合の総数: 19
  → bihierarchy（H1: 16集合 / H2: 3集合）

  期待割当 X（列は a, b, ∅）
    [   1/2      0    1/2 ]
    [   1/2      0    1/2 ]
    [     0    1/2    1/2 ]
    [   1/2    1/2      0 ]

─── ステップ3: 一般化BvNで純割当のくじに分解する ───

  分解された純割当の数: 4

  【第1項】 λ = 1/4
    学生1: a
    学生2: ∅
    学生3: ∅
    学生4: b

  【第2項】 λ = 1/4
    学生1: a
    学生2: ∅
    学生3: b
    学生4: a

  【第3項】 λ = 1/4
    学生1: ∅
    学生2: a
    学生3: ∅
    学生4: b

  【第4項】 λ = 1/4
    学生1: ∅
    学生2: a
    学生3: b
    学生4: a

  検証: すべて OK（再構成一致・全項が制約を満たす）
```

**選好を入れたら、実際に配れる「くじ」が出てきました。** どの項を見ても

- 各学生は高々1校（∅ を含めてちょうど1つ）
- `a` は2人まで、`b` は1人まで
- **`a` に入る学生1,2,3 は常に高々1人**

を満たしています。第2項では学生1と学生4が `a` に入っていますが、学生4は制約の対象外なので問題ありません。

:::note info
**前処理が要らなくなった**

前回は「∅ 列をそのまま落として正方化できるのは特殊な設定のときだけ」という注意書きが必要でした。今回は `∅` を「列制約を課さない列」として扱えるので、**前処理が一切要りません**。制約構造という抽象化の効き目です。
:::

もう1つ、社内の案件アサインの例も動かせます。「佐藤と鈴木を案件Aで同席させない」という制約を入れると、分解された全ての純割当で2人が別々の案件になります。

```bash
=== 拡張PSメカニズムの期待行列 ===
               A       B       ∅
佐藤         1/2     1/2       0
鈴木         1/2     1/2       0
高橋           1       0       0
田中           0       1       0

─── ステップ3: 一般化BvNで純割当のくじに分解する ───

  分解された純割当の数: 2

  【第1項】 λ = 1/2
    佐藤: A
    鈴木: B
    高橋: A
    田中: B

  【第2項】 λ = 1/2
    佐藤: B
    鈴木: A
    高橋: A
    田中: B

  検証: すべて OK（再構成一致・全項が制約を満たす）
```

期待割当のレベルでは佐藤も鈴木も「A に $\frac{1}{2}$」ですが、**くじのどちらを引いても2人が同じ案件になることはありません**。期待値だけを見ていては分からない、実装のレベルで初めて保証される性質です。

## まとめ：多対1の限界と、その境界線

ここまでで、多対1の割り当て問題が解けることを実装で確認しました。要点は4つです。

- 【**メカニズム**】拡張PSは前回のPSに**挿入2箇所**を足すだけ。「食べられる」の判定に制約の余地を加える
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

| 問題                                  | 解けるか | 理由                                     |
| ------------------------------------- | :------: | ---------------------------------------- |
| 1対1（二重確率行列）                  |    ✅     | bihierarchy の特殊ケース（系1＝BvN定理） |
| **多対1**（定員＋グループ別クォータ） |    ✅     | 部分列は列と入れ子なので階層のまま       |
| 多対多（履修割当）                    |    ✅     | 部分行が階層をなす限り                   |
| 交差する制約を同時に課す              |    ❌     | 奇サイクル（補題1）                      |
| 3部以上・ルームメイト                 |    ❌     | 必ず奇サイクルを含む（定理12・13）       |

「何ができるか」だけでなく「何ができないか」まで、コードで機械的に判定できるようになったことが今回いちばんの収穫だと感じています。なお本記事では触れませんでしたが、論文には「実装可能なくじの中から、事後的に公平なものを選ぶ」手法（効用保証・定理9）も用意されています。機会があれば別記事で扱いたいです。

以上になります。
最後まで読んでいただきありがとうございました。

## 参考文献

- [マッチング理論とマーケットデザイン](https://www.amazon.co.jp/dp/453555935X)
- Hoffman, A. J. and J. B. Kruskal (1956) "Integral Boundary Points of Convex Polyhedra," in *Linear Inequalities and Related Systems*, Princeton University Press.
- Edmonds, J. (1970) "Submodular Functions, Matroids, and Certain Polyhedra," in *Combinatorial Structures and Their Applications*.
- Hatfield, J. W. and P. Milgrom (2005) "Matching with Contracts," *American Economic Review*, 95(4), pp.913–935.
