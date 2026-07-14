<div class="chap1">

# マッチングの基本モデル

## 二部マッチングの基礎

### モデル

- 二部マッチングでは2種類の異なるグループに属する参加者たちをどのように組み合わせるかを考える。例えば、①労働市場における「求職者」と「雇用主」、②研修医マッチング市場における「研修医」と「病院」、③婚活市場における「男性」と「女性」、④教育産業市場における「学生」と「大学」、などがある。

#### 【1対1マッチング】数式による表現

$$
\begin{align*}
&【条件1】\mu(s)\in C\cup \{\emptyset\}&(1)\\
&【条件2】\mu(c)\in S\cup \{\emptyset\}&(2)\\
&【条件3】\mu(s)=c\iff s=\mu(c)&(3)
\end{align*}
$$

- 学生$s\in S$、大学$c\in C$とするとき、**1対1マッチング**$\mu:S\cup C\rightarrow S\cup C\cup \{\emptyset\}$は以下の3つの条件を満たす。
  - 【**条件1**】どの学生も1つの大学に入学しているか、どこにも入学していないかのどちらか
  - 【**条件2**】どの大学も1人の学生を入学させているか、誰も入学させていないかのどちらか
  - 【**条件3**】もし学生$s$が大学$c$に入学しているなら、大学$c$は学生$s$を受け入れている

#### 【多対1マッチング】数式による表現

$$
\begin{align*}
&【条件1】\mu(s)\subseteq Cかつ|\mu(s)|≦1&(1)\\
&【条件2】\mu(c)\subseteq Sかつ|\mu(c)|≦q_c&(2)\\
&【条件3】\mu(s)=\{c\}\iff s\in\mu(c)&(3)
\end{align*}
$$

- 学生$s\in S$、大学$c\in C$とするとき、**多対1マッチング**$\mu:S\cup C\twoheadrightarrow	 S\cup C\cup \{\emptyset\}$は以下の3つの条件を満たす。ここで、大学$c$が受け入れる学生の最大人数を$q_c$とし、$\displaystyle{|q|=\sum_{c\in C}q_c}$とする。
  - 【**条件1**】どの学生もどこかの大学に入学しており、かつ、学生が入学可能な大学数が1以下
  - 【**条件2**】どの大学もどこかの学生を受け入れており、かつ、大学が受け入れ可能な学生数は$q_c$以下である。
  - 【**条件3**】学生$s$が大学$c$に入学しているならば、大学$c$が受け入れ可能に学生に$s$は含まれる。

<div style="page-break-before:always"></div>

### 安定性

- 安定性とは、「**どの意思決定者も不満がない状態**」であり、具体的には以下の2つの条件を満たすことを言う。
  - 【**条件1**】どの参加者によってもブロックされない。（<font color=red>個人合理性</font>）
  - 【**条件2**】どのペアによってもブロックされない。

#### 【1対1マッチング】数式による安定性の表現

$$
\begin{align*}
&【条件1：\color{red}個人合理性\color{black}】\overline{\emptyset\succ\mu(i)}\iff\emptyset\precsim\mu(i)\\
&【条件2】\overline{\color{blue}c\succ\mu(s)\color{black}かつ\color{green}s\succ\mu(c)}\iff\color{blue}c\precsim\mu(s)\color{black}または\color{green}s\precsim\mu(c)
\end{align*}
$$

- 【**条件1**】がブロックされている状況について説明する。これは、参加者$i\in S\cup C$(学生または大学)にとってマッチング$\mu$で組む相手が受け入れられないと言う状況であり、「**学生が無理やり大学に入学させられている状況**」や「**大学が無理やり学生を入れられている状況**」を指す。
- 【**条件2**】がブロックされている状況について説明する。これは、両者が両者に不満を持っている状態であり、「**学生$s$は自身が入学する大学$\mu(s)$よりも別の大学$c$が好きで、大学$c$もまた、受け入れる学生$\mu(c)$よりも別の学生$s$を希望している状況**」を指す。

#### 【多対1マッチング】数式による安定性の表現

$$
\begin{align*}
&【条件1：\color{red}個人合理性\color{black}】\overline{_s\emptyset\succ\mu(s)または_c\emptyset\succsim s'}\iff_s\emptyset\precsim\mu(s)かつ_c\emptyset\prec s'\\
&【条件2】\overline{\color{blue}c\succ{} _s\mu(s)\color{black}かつ\color{green}\left[s\succ{} _cs'または\left[|\mu(c)|<q_cかつs\succ{}_c\emptyset\right]\hspace{1mm}\right]}\iff\\
&\hspace{15.5mm}\color{blue}c\precsim{}_s\mu(s)\color{black}または\color{green}\left[s\precsim{}_cs'かつ\left[|\mu(c)|≧q_cまたはs\precsim{}_c\emptyset\right]\hspace{1mm}\right]\\[1mm]
&\hspace{15mm}ただし、s'\in\mu(c)
\end{align*}
$$

- 【**条件1**】がブロックされている状況については、1対1マッチングと同様の考え方になる。
- 【**条件2**】がブロックされている状況について説明する。これは、学生側と大学側の両方の不満の有無を表す条件であり、<font color=blue>青色の条件式が学生側の選好</font>、<font color=green>緑色の条件式が大学側の選好</font>である。学生側の選好は1対1と同様であるが、大学側については定員$q_c$というパラメータが追加されたことで複雑化している。

<div style="page-break-before:always"></div>

## DA（Deferred Acceptance）アルゴリズム

- 安定的なマッチングはアルゴリズムを用いて非常に簡単に見つけることが可能であり、それが、**DAアルゴリズム（Deferred Acceptance Algorithm：受入保留アルゴリズム）** である。DAアルゴリズムは2つのバージョンがあり、ここでは、<u>学生応募制DAアルゴリズム（もう一方は大学応募制DAアルゴリズム）</u>を説明する。

### DAアルゴリズムの定義

- 【**1対1と多対1マッチングの違い**】<font color=red><b>各大学が自分の定員$q_c$の範囲内で複数の学生を仮受け入れできる点</b></font>

#### 【1対1マッチング】

```plantuml
title 1対1マッチング

actor 学生 as student1
actor 学生 as student2
actor 学生 as student3
rectangle 大学 as college1
rectangle 大学 as college2
rectangle 大学 as college3

student1 -- college1
student2 -- college2
student3 -- college3
```

- 【**ステップ1**】
  - （**a**）各学生は自分にとって受け入れ可能な第1志望の大学に出願する（受入可能な大学がなければ外部オプション$\emptyset$を選択する、つまり浪人する）。
  - （**b**）各大学は出願してきた学生の中から一番好ましい学生を「仮に」受け入れ、それ以外の学生を不合格（reject）する。受け入れ可能な出願者が一人もいなければ、全員を不合格にする。
- 【**ステップ2**】
  - （**a**）不合格にされた学生は次に志望する受入可能な大学に出願する（なければ外部オプション$\emptyset$、つまり浪人を選ぶ）。
  - （**b**）各大学はこのステップで出願してきた学生と前のステップで「仮に」受け入れた学生を合わせた中から、一番好ましい学生を「仮に」受け入れ、それ以外の学生を不合格にする。ただし、受け入れ可能な出願者が一人もいなければ、全員を不合格にする。
- 【**ステップ3**】ステップ2の過程を出願がなくなるまで繰り返す。最後に大学が「仮」受け入れしている学生を正式に受け入れ、入学させる。

<div style="page-break-before:always"></div>

#### 【多対1マッチング】

```plantuml
title 多対1マッチング

actor 学生 as student1
actor 学生 as student2
actor 学生 as student3
actor 学生 as student4
actor 学生 as student5
actor 学生 as student6
rectangle "大学\n（定員3人）" as college1
rectangle "大学\n（定員2人）" as college2
rectangle "大学\n（定員1人）" as college3

student1 -- college1
student2 -- college1
student3 -- college1
student4 -- college2
student5 -- college2
student6 -- college3
```

- 【**ステップ1**】
  - （**a**）各学生は第1志望の大学に出願する（なければ外部オプション$\emptyset$、つまり浪人を選択する）。
  - （**b**）各大学$c$は出願してきた学生の中から<font color=red>定員$q_c$までの範囲で</font>好ましい学生を「仮に」受け入れ、それ以外の学生を不合格とする。受け入れ可能でない出願者は不合格者とする。
- 【**ステップ2**】
  - （**a**）前のステップで不合格とされた学生は次に志望する大学に出願する（なければ外部オプション$\emptyset$、つまり浪人を選択する）。
  - （**b**）各大学$c$はこのステップで出願してきた学生と前のステップで「仮に」受け入れた学生を合わせた中から、<font color=red>定員$q_c$までの範囲で</font>好ましいものを「仮に」受け入れ、それ以外の学生を不合格とする。受け入れ可能でない出願者は不合格とする。
- 【**ステップ3**】出願がなくなるまでステップ2を繰り返し、最後に大学が「仮に」受け入れしている学生を正式に受け入れ、入学させる。

<div style="page-break-before:always"></div>

### DAアルゴリズムを使ってみる

$$
\begin{align*}
S=\{s_1,s_2,s_3\}&\hspace{1mm},\hspace{2mm}C=\{c_1,c_2\}\\
\succ s_1&:c_1,c_2\\
\succ s_2&:c_1\hspace{3mm}※\emptyset\succ_{s_2}c_2\\
\succ s_3&:c_2,c_1\\
\succ c_1&:s_3,s_2,s_1\\
\succ c_2&:s_1,s_3\\
\color{red}【帰結】s_1\hearts c_2&\color{red}、s_2\hearts\emptyset、s_3\hearts c_1
\end{align*}
$$

- 【**補足**】上記リストを用いてDAアルゴリズムの処理を見る。学生$s_1$は大学$c_1,c_2$の順で第1志望、第2志望であり、学生$s_2$は$c_1$が第1志望、$c_2$は受け入れ可能ではない（$\emptyset\succ_{s_2}c_2$）と読む。

```plantuml
title 1対1マッチングにおけるDAアルゴリズム

rectangle ステップ1 as step1 {
  actor 学生1 as step1_student1
  actor 学生2 as step1_student2
  actor 学生3 as step1_student3
  rectangle 大学1 as step1_college1
  rectangle 大学2 as step1_college2
  step1_student1 --> step1_college1: 出願→不合格
  step1_student2 --> step1_college1: 出願→仮受け入れ
  step1_student3 --> step1_college2: 出願→仮受け入れ
}
rectangle ステップ2 as step2 {
  actor 学生1 as step2_student1
  actor 学生2 as step2_student2
  actor 学生3 as step2_student3
  rectangle 大学1 as step2_college1
  rectangle 大学2 as step2_college2
  step2_student1 --> step2_college2: 出願→仮受け入れ
  step2_student2 --> step2_college1: 仮受け入れ中
  step2_student3 --> step2_college2: 仮受け入れ中→不合格
}
step1 -[hidden]-- step2
```

```plantuml
rectangle ステップ3 as step3 {
  actor 学生1 as step3_student1
  actor 学生2 as step3_student2
  actor 学生3 as step3_student3
  rectangle 大学1 as step3_college1
  rectangle 大学2 as step3_college2
  step3_student1 --> step3_college2: 仮受け入れ中
  step3_student2 --> step3_college1: 仮受け入れ中→不合格
  step3_student3 --> step3_college1: 出願→仮受け入れ
}
rectangle "ステップ4（アルゴリズム終了）" as step4 {
  actor 学生1 as step4_student1
  actor 学生2 as step4_student2
  actor 学生3 as step4_student3
  rectangle 大学1 as step4_college1
  rectangle 大学2 as step4_college2
  step4_student1 --> step4_college2: <color red>入学受け入れ
  step4_student2 --> step4_student2: <color red>外部オプション
  step4_student3 --> step4_college1: <color red>入学受け入れ
}
step3 -[hidden]-- step4
```

- 【**ステップ1**】$s_1$と$s_2$は第1志望の$c_1$に出願し、$s_3$は第1志望の$c_2$に出願する。次に、$c_1$は$s_1$と$s_2$のうち、より好ましい$s_2$を「仮に」受け入れ、$s_1$を不合格にする。$c_2$は$s_3$を「仮に」受け入れる。
- 【**ステップ2**】不合格にされた$s_1$は第2志望の$c_2$に出願する。次に、$c_2$は「仮受け入れ中」の$s_3$と$s_1$を比較し、より好ましい$s_1$を「仮に」受け入れ、$s_3$を不合格にする。
- 【**ステップ3**】不合格にされた$s_3$は第2志望の$c_1$に出願する。次に、$c_1$は「仮受け入れ中」の$s_2$と$s_3$を比較し、より好ましい$s_3$を「仮に」受け入れ、$s_2$を不合格にする。
- 【**ステップ4**】不合格にされた$s_2$はもう志望する大学がないので、外部オプション$\emptyset$を選び、出願がなくなったのでアルゴリズムが終了する。

<div style="page-break-before:always"></div>

### DAアルゴリズムと安定

$$
【\bold{定理}】DAアルゴリズムが与えるマッチングは安定的である
$$

> <font size=4><div align=center>【**証明**】</div></font>**DAアルゴリズムが与えるマッチングを$\mu$とする**。DAアルゴリズムが安定性を満たすためには以下の2つの条件を満たすことを証明する必要がある。
> - 【**条件1**】どの参加者によっても$\mu(*)$はブロックされない（<font color=red>個人合理性</font>）
> - 【**条件2**】どんなペアによっても$\mu(*)$はブロックされない
> 
> まず、**条件1**の証明を行う。DAアルゴリズムの定義によると、各学生$s_i$は各ステップにおいて、自分にとって受け入れ可能な大学$\mu(s_i)$にしか出願せず、最終的なマッチングで受け入れられない大学に入学していることはあり得ない。また、各大学$c_i$も各ステップにおいて自分にとって受け入れ可能な学生$\mu(c_i)$しかキープせず、最終的なマッチングで受け入れられない学生をキープしていることはあり得ない。<font color=red>したがって、$\mu(*)$はどの個人にもブロックされない</font>。
> 　次に**条件2**の証明、「ペアによるブロックに対する頑健性」を確認する。学生$s$は今マッチしている大学$\mu(s)$よりも他の大学$c$の方を好んでいる、つまり、$c\succ_s\mu(s)$が成り立っていると仮定する。このとき、DAアルゴリズムの定義によると、「**①どこかのステップで$s$は$c$に出願していた、かつ、②$c$は$s$を不合格とし、別にマッチした学生$\mu(c)$が存在する**」ことになり、$\mu(c)\succ_c s$を満たす。以上より、DAアルゴリズムは条件2に対して以下の帰結を得る。
> $$
> 【DAアルゴリズムから得られる帰結】\\[1mm]
> c\succ_s\mu(s)\Rightarrow \mu(c)\succ_c s
> $$上式は「学生$s$は自身がマッチした大学$\mu(s)$よりも別の大学$c$の方が好きならば、大学$c$は$s$よりも自身がマッチした学生$\mu(c)$の方が好きである」ことを意味する。<font color=red>したがって、どんなペアも$\mu(*)$をブロックすることができないことがわかる</font>。

## 現実の市場における重要性

- マッチング理論の最初の論文（Gale and Shapley）は1962年であったが、アメリカの研修医マッチング制度（NRMP：National Resident Matching Program）は1950年代初頭から病院応募制のDAアルゴリズムを使っていた。つまり、DAアルゴリズムはすでに現実の市場に使われていた。例えば、Roth（1991）はイギリスの研修医マッチングを調査したところ、安定的なマッチング方式は長期間採用されているが、安定的でない方式は数年以内に使われなくなっていた。<font color=red>「現場の市場参加者たちが試行錯誤で見つけたマッチング方式が、実は学者が理論的に導き出した方式と一致している」</font>と言うことである。

<div style="page-break-before:always"></div>

---

#### 参考文献

<ol class="brackets">
  <li>Abdulkadiroglu, Atila, Parag A. Pathak and Alvin. E. Roth (2009) "Strategy-Proofness versus Efficiency in Matching with Indifferences: Redesigning New York City High School Match," <i>American Economic Review</i>, 99(5), pp.1954-1978.</li>
  <li>Gale, David and Lloyd S. Shapley (1962) "College Admissions and the Stability of Marriage," <i>American Mathematical Monthly</i>, 69(1), pp.9-15.</li>
  <li>Roth, Alvin E. (1982) "The Economics of Matching: Stability and Incentives," <i>Mathematics of Operations Research</i>, 7, pp.617-628</li>
  <li>Roth, Alvin E. (1984) "The Evolution of the Labor Market for Medical Interns and Residents: A Case Study in Game Theory," <i>Journal of Political Economy</i>, 92(6), pp.991-1016.</li>
  <li>Roth, Alvin E. (1991) "A Natural Experiment in the Organization of Entry-Level Labor Markets: Regional Markets for New Physicians and Surgeons in the United Kingdom," <i>American Economic Review</i>, 81(3), pp.415-440.</li>
  <li>Roth, Alvin E. (2002) "The Economist as Engineer: Game Theory, Experimentation, and Computation as Tools for Design Economics," <i>Econometrica</i>, 70(4), pp.1341-1378.</li>
</ol>