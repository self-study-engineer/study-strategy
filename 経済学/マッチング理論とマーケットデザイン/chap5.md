<div class="chap5">

# 制約付きマッチングにおける"正しい"安定性の定義を考える

```plantuml
title 制約付きマッチング
rectangle "地域α（地域上限）" as r1 {
  rectangle "病院A（設置上限）" as h1
  rectangle "病院B（設置上限）" as h2
  h1 -[hidden]- h2
}
rectangle "地域β（地域上限）" as r2 {
  rectangle "病院C（設置上限）" as h3
  rectangle "病院D（設置上限）" as h4
  rectangle "病院E（設置上限）" as h5
}
actor "研修医1"
actor "研修医2"
actor "研修医3"
actor "研修医4"
```

<div style="padding: 15px 15px 15px 15px; border: 2px solid; border-radius: 5px;">
  <b>【実行可能性】</b>マッチング$\mu$が実行可能（feasible）であるとは、以下の2つを満たすことを言う。<br>
  <ol>
    <li>任意の病院$A\in H$について$|\mu_A|\leqq q_A$が成り立つ</li>
    <li>任意の地域$R$について$|\mu_R|\leqq q_R$が成り立つ</li>
  </ol>
  上の定義は「すべての病院の設置上限」と「すべての地域の地域上限」が守られている時、マッチングが実行可能であるという。
</div>
<br>

- 本章で登場する文字は以下の通り。
  - $D$：研修医の集合（$i,j\in D$）
  - $H$：病院の集合（$A,B\in H$）
  - $q_A\in\mathbb{Z}_+$：病院$A$の設置上限
  - $q_R\in\mathbb{Z}_+$：地域$R$の地域上限
  - $r(A)$：病院$A$が所在する地域
  - $\mu_A=\{i\in D:\mu(i)=A\}$：マッチング$\mu$において病院$A$に配属される研修医の集合、人数を$|\mu_A|$とする。
  - $\mu_R=\{i\in D:r(\mu(i))=R\}$：マッチング$\mu$において地域$R$全体に配属される研修医の集合、人数を$|\mu_R|$とする。

## 制約付きマッチングにおいて安定性をどう定義すれば良いか

- 第4章では日本の研修医マッチング制度の非効率的な点を指摘し、FDAメカニズム（マッチできる研修医の数を増やし、より希望順位の高い病院に配属させられるメカニズム）を提案した。FDAメカニズムは制約があると安定マッチングが存在しない場合があるため通常の意味での安定性を満たすことができない。
- そこで、5章では「**制約付きマッチングにおける望ましい配分の性質とはどのようなものか**」という問題を考える。

<div style="page-break-before:always"></div>

## 制約付きマッチングにおける強安定性

- 通常の安定性は以下の2つの性質を持つ
  - 個人合理的である
  - ブロックするペアが存在しない
- 上記の安定性は制約構造のあるマッチング問題だと存在が保証されないため、本節では「**安定性の妥当な弱め方**」を探る。

### 強安定性の定義

<div style="padding: 15px 15px 0px 15px; border: 2px solid; border-radius: 5px;">
  【<b>強安定性</b>】次の3つの条件を満たすとき、マッチング$\mu$は強安定的であるという。<br>
  <ol>
    <li>実行可能である。</li>
    <li>個人合理的である。</li>
    <li>もし$(i,A)$が$\mu$をブロックするペアならば、次の3つが全て成り立つ。</li>
    <ol>
      <li>【<b>受入数の条件</b>】病院$A$の所在地域には地域上限と同数の研修医がいる。つまり$|\mu_{r(A)}|=q_{r(A)}$が成り立つ。</li>
      <li>【<b>選好の条件</b>】病院$A$はいま採用中のどの研修医についても$i$より好んでいる。つまり、すべての $j\in\mu_A$ について $j\succ_Ai$ が成り立つ。</li>
      <li>【<b>地域内移行の条件</b>】研修医$i$と病院$A$と同じ地域にある他の病院には配属されていない。つまり $r(\mu(i))\neq r(A)$ が成り立つ。</li>
    </ol>
  </ol>
</div>

<div style="page-break-before:always"></div>

### 強安定マッチングは存在しないことがある

- 強安定性は通常の安定性を弱めた条件としては自然に思いつくものであり、違いは「<font color=red><b>実行可能でないケースのみブロックするペアの存在を許容すること</b></font>」である。それ以外は通常の安定性の定義と同じであるが、強安定マッチングは常に存在するとは限らない。

#### 【例】強安定性を満たさないマッチング

$$
\begin{align*}
  &\hspace{1mm}1\quad 2\\
  -&----\\
  &A\quad B\\
  &B\quad A\\
\end{align*}
\hspace{35mm}
\begin{align*}
  &A\quad B\\
  -&----\\
  &\hspace{1mm}2\quad 1\\
  &\hspace{1mm}1\quad 2\\
\end{align*}
\\[5mm]
\begin{align*}
  【\bold{マッチング結果1}】&(1\hearts A)\quad 2とBはマッチしない\\
  【\bold{マッチング結果2}】&(2\hearts A)\quad 1とBはマッチしない\\
  【\bold{マッチング結果3}】&(2\hearts B)\quad 1とAはマッチしない\\
  【\bold{マッチング結果4}】&(1\hearts B)\quad 2とAはマッチしない
\end{align*}
$$

- 強安定性を満たさないマッチングを考える。2人の研修医、同じ地域内にある2つの病院、地域上限は1とする。その上で、選好とマッチング結果は上の通り。
- 【**マッチング結果1について**】$(1\hearts A)$は$(2,A)$にブロックされる。今、病院$A$は2を1より好むため強安定性の定義の【選好の条件】を満たさない。つまり、病院Aは1を雇うのをやめて2を雇えば、地域上限を破ることなくブロック可能。
- 【**マッチング結果2について**】$(2\hearts A)$は$(2,B)$にブロックされる。2は同じ地域の病院に配属されるため強安定性の定義の【地域内移行の条件】を満たさない。つまり、2が病院Bに移っても地域全体に配属される研修医の数は変わらず、実行可能な範囲でブロック可能。
- 【**マッチング結果3について**】$(2\hearts B)$は$(1,B)$にブロックされる。病院Bは1を2より好むため強安定性の定義の【選好の条件】を満たさない。つまり、病院Bは2を雇うのをやめて1を雇えば、地域上限を破ることなくブロック可能。
- 【**マッチング結果4について**】$(1\hearts B)$は$(1,A)$にブロックされる。1は同じ地域内の病院に配属されるため強安定性の定義の【地域内移行の条件】を満たさない。つまり、1が病院Aに移っても地域全体の配属される研修医の数は変わらず、実行可能な範囲でブロック可能。

<div style="page-break-before:always"></div>

### 強安定マッチングの不可能性定理

- 本節では強安定マッチングの不存在がどの程度深刻なのかを考える。具体的には「強安定マッチングが存在することを保証する制約構造とはどのようなものか」という問いを考える。
- 制約構造について2つの性質を定義する。
  1. どんな研修医の数、選好、病院の設置上限についても常に強安定マッチングが存在する時、その制約構造は**強安定マッチングの存在を保証する**という。
  2. すべての地域について「病院の数が1つだけ」または「地域上限が0」のどちらかが成り立つ時、その制約構造は**病院間独立性（independence across hospitals）** を満たすという。
- 一般的に、「①研修医側耐戦略性を満たし、②強安定マッチングが存在するならばそれを選ぶようなメカニズムが存在すること」と「病院間独立性を満たすこと」は同値である。つまり、ほとんどの「まともな」制約付きマッチング問題において、たとえ強安定マッチングが存在する場合であっても強安定マッチングを選び取ることができるような研修医側耐戦略性を満たすメカニズムは存在しない。

## 弱安定性

- 5.2節では、安定性を弱めた「強安定性」を定義したが、ほとんどの強安定マッチングは存在しないか、存在したとしてもそれを選び取ることができる耐戦略的なメカニズムが存在しないことがわかった。

### 弱安定性の定義

<div style="padding: 15px 15px 0px 15px; border: 2px solid; border-radius: 5px;">
  【<b>弱安定性</b>】次の3つの条件を満たすとき、マッチング$\mu$は弱安定的であるという。<br>
  <ol>
    <li>実行可能である。</li>
    <li>個人合理的である。</li>
    <li>もし$(i,A)$が$\mu$をブロックするペアならば、次の3つが全て成り立つ。</li>
    <ol>
      <li>【<b>受入数の条件</b>】病院$A$の所在地域には地域上限と同数の研修医がいる。つまり$|\mu_{r(A)}|=q_{r(A)}$が成り立つ。</li>
      <li>【<b>選好の条件</b>】病院$A$はいま採用中のどの研修医についても$i$より好んでいる。つまり、すべての $j\in\mu_A$ について $j\succ_Ai$ が成り立つ。</li>
    </ol>
  </ol>
</div>
<br>

- つまり、<font color=red>強安定性の【地域内移行の条件】を取り除いたものが「弱安定性」</font>になる。つまり、ブロックするペアの存在を「受入数」と「選好」の2つに絞ったものが弱安定性になる。
- この弱安定性が4.3節で紹介した「制約付き安定性」の正体である。一般に、弱安定性マッチングは常に存在する。そこで次節では、弱安定性という概念は「ダメそうな」マッチングを排除できる程度には十分強い条件なのかを考える。

### 弱安定性の望ましい性質

$$
弱安定的である\Rightarrow 制約付き効率的である
$$

<div style="padding: 15px 15px 0px 15px; border: 2px solid; border-radius: 5px;">
  【<b>無駄がないの定義</b>】次の2つの条件を同時に満たすペア$(i,A)$が存在しないことをいう。<br>
  <ol>
    <li>研修医$i$が現在配属されている病院 $\mu(i)$ よりも病院$A$を好み、かつ、病院$A$にとっても$i$は受け入れ可能である。つまり $A\succ_i\mu(i)$ かつ $i\succ_A\emptyset$ が成り立つ。</li>
    <li>病院$A$の設置上限と$A$の所在地域の地域上限のどちらにも達していない。つまり $|\mu_A|<q_A$ かつ $|\mu_{r(A)}|<q_{r(A)}$ が成り立つ。</li>
  </ol>
</div>
<br>
<div style="padding: 15px 15px 0px 15px; border: 2px solid; border-radius: 5px;">
  【<b>無羨望性の定義</b>】次の2つの条件を同時に満たすペア$(i,j)$が存在しないことをいう。<br>
  <ol>
    <li>研修医$i$は$j$の配属先の方を今の自分の配属先より好む。つまり、$\mu(j)\succ_i\mu(i)$ が成り立つ。</li>
    <li>研修医$j$の配属先 $\mu(j)$ は$j$より$i$を好む、または$j$はどこにも配属されていない。つまり $i\succ_{\mu(j)}j$ または $\mu(j)=\emptyset$ が成り立つ。</li>
  </ol>
</div>
<br>
<div style="padding: 15px 15px 0px 15px; border: 2px solid; border-radius: 5px;">
  【<b><font color=red>弱安定マッチングが満たす4つの性質</font></b>】あるマッチングが弱安定的であることと、そのマッチングが以下の4つの条件を満たすことは同値である。<br>
  <ol>
    <li>実行可能である</li>
    <li>個人合理的である</li>
    <li>無駄がない</li>
    <li>正当な羨望がない（無羨望性を満たす）</li>
  </ol>
</div>
<br>

- 一般に、**FDAメカニズムの帰結は弱安定マッチング**であり、また弱安定性は4.2節で説明した制約付き効率性を含意する。
- 弱安定性はいくつかの標準的な規範的性質によって特徴付けられることがわかっており、それにともに以下の2つの条件を導入する。
  - **マッチング$\mu$に無駄がない（non-wasteful）**
  - **マッチング$\mu$が無羨望性を満たす（正当な羨望がない）**
- 以上のことから弱安定性という条件は厚生経済学やゲーム理論でこれまで考えられてきた標準的な規範的性質である個人合理性や無羨望性を満たすことが確認できる。

#### 【振り返り】制約付き効率性

<div style="padding: 15px 15px 0px 15px; border: 2px solid; border-radius: 5px;">
  【<b>制約付き効率性の定義</b>】以下の3つの条件を満たすマッチング$\mu'$が存在しないことを言う<br>
  <ol>
    <li>$\mu'$は実行可能である</li>
    <li>すべての $i\in D\cup H$ について $\mu'(i)\succ_i\mu(i)$ または $\mu'(i)=\mu(i)$ が成り立つ</li>
    <li>ある $j\in D\cup H$ について $\mu'(j)\succ_j\mu(j)$ が成り立つ</li>
  </ol>
</div>

### 制約構造の一般化

$$
【\bold{制約構造の一般化}】\\[1mm]
f：\mathbb{Z}^n\rightarrow\{0,1\}
$$

- これまでに分析した弱安定性と強安定性に関する命題は上式の関数$f$ように一般化して表現できる。具体的には「各病院で配属される研修医の人数」を表す$n$次元ベクトルを入力すると$1（実行可能）$または$0（実行不可能）$を返す関数である。
- 例えば、病院が$A,B,C$の3つあり、そこに配属される研修医の人数がそれぞれ4人、5人、3人だとする。この構成で<font color=red>実行可能ならば、$f(4,5,3)=1$</font>となり、<font color=blue>実行不可能ならば$f(4,5,3)=0$</font>となる。
- このような関数$f$を制約関数と呼び、配属人数のみを制限する制約構造であれば、どんなものでも表現できる。<u>ただし、配属される人の属性に応じて配属可能人数が変化するような制約はこの関数では表現できない</u>。詳しくは6章で取り扱う。

#### 人数上限だけを定める制約関数が持つ性質

$$
【\bold{遺伝性}】\\[1mm]
f(w')=1\hspace{1mm}かつ\hspace{1mm}w\leqq w'\hspace{1mm}\implies\hspace{1mm}f(w)=1
$$

- 制約関数には「**遺伝性**」という性質を課すことが多い、具体的には「配属人数$w'$が実行可能ならばそれ以下の人数しか各病院に割り当てないような配属方法$w$もまた実行可能である」という性質であり、**一般に人数の上限だけを定める制約は遺伝性を満たす**。
- 遺伝性を満たす制約構造の例としては他にも以下のようなものが挙げられる。
  - 【**階層構造（ヒエラルキー）を持つような制約構造**】都道府県ごとの地域上限に加えて、関東地方、東北地方、中部地方、などの地方ごとにも地方上限があり、それも満たさなければいけないような制約構造。
  - 【**地域上限などに加えて専門科ごとに定員があるような制約構造**】麻酔科、皮膚科、眼科、放射線科、など研修医が専攻するコースごとに上限があり、それを満たさなければいけない制約構造。

<div style="page-break-before:always"></div>

## 終わりに

- この章では制約付きマッチングにおいて安定性をどのように定義すれば良いのかを考えた。弱安定マッチングは制約付きマッチング問題においても常に存在することがわかった。また、弱安定マッチングは制約付き効率性を満たし、4つの標準的な規範的性質を満たす唯一の条件であることを確認した。
- 弱安定性というマッチングの望ましい性質は日本の研修医マッチング問題だけでなく、より広範な制約付きマッチング問題において使える、まさに正しい安定性の概念であることを確認した。

---

#### 参考文献

<ol class="brackets">
  <li>田村明久（2009）『離散凸解析とゲーム理論』朝倉書店</li>
  <li>Balinski, Michel and Tayfun Sonmez（1999） "A Tale of Two Mechanisms: Student Placement," <i>Journal of Economic Theory</i>, 84, pp.73-94.</li>
  <li>Kamada, Yuichiro and Fuhito Kojima（2012） "Stability and Strategy-Proofness for Matching with Constraints: A Problem in the Japanese Medical Match and Its Solution," <i>American Economic Review Papers and Proceedings</i>, 102(3), pp.366-370.</li>
  <li>Kamada, Yuichiro and Fuhito Kojima（2015） "Efficient Matching under Distributional Constraints: Theory and Applications," <i>American Economic Review</i>, 105(1), pp.67-99.</li>
  <li>Kamada, Yuichiro and Fuhito Kojima（2017） "Stability Concepts in Matching under Distributional Constraints," <i>Journal of Economic Theory</i>, 168, pp.107-142</li>
  <li>Kamada, Yuichiro and Fuhito Kojima（2018） "Stability and Strategy-Proofness for Matching with Constraints: A Necessary and Sufficient Condition," <i>Theoretical Economics</i>, 13(2), pp.761-794.</li>
  <li>Kamada, Yuichiro and Fuhito Kojima（2024） "Fair Matching under Constraints: Theory and Applications," <i>Review of Economic Studies</i>, 91(2), pp.1162-1199.</li>
  <li>Kojima, Fuhito, Akihisa Tamura and Makoto Yokoo（2018） "Designing Matching Mechanisms under Constraints: An Approach from Discrete Convex Analysis," <i>Journal of Economic Theory</i>, 176, pp.803-833.</li>
</ol>