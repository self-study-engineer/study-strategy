<div class="chap2">

# 安定マッチングについて深掘りする<font size=5>〜最適性、耐戦略性、古典的理論の限界〜</font>

## 安定マッチングの性質

### 最適安定マッチング

$$
\begin{align*}
S=\{s_1,s_2\}&\hspace{1mm},\hspace{1mm}C=\{c_1,c_2\}\\
\succ s_1&:c_1,c_2\\
\succ s_2&:c_2,c_1\\
\succ c_1&:s_2,s_1\\
\succ c_2&:s_1,s_2\\
\color{red}【\bold{学生}応募制DA】s_1\hearts c_1、s_2\hearts c_2&\color{red}\iff \bold{学生}最適安定マッチング\\
\color{red}【\bold{大学}応募制DA】s_1\hearts c_2、s_2\hearts c_1&\color{red}\iff \bold{大学}最適安定マッチング
\end{align*}
$$
$$
【\bold{定理}】\\
学生応募制DAアルゴリズムが与えるマッチングは\\
学生最適安定マッチングである。
\\[4mm]
【\bold{定理}】\\
大学応募制DAアルゴリズムが与えるマッチングは\\
大学最適安定マッチングである。
$$

- 複数の安定マッチングがある時、その中にはある特別な性質を持つマッチングがある。上記のマッチング例の場合、学生応募制と大学応募制のDAアルゴリズムで異なる安定マッチングが得られ、前者は「学生最適安定マッチング」、後者は「大学最適安定マッチング」である。

<div style="page-break-before:always"></div>

> <font size=4><div align=center><b>【証明】</b></div></font>**学生応募制DAアルゴリズムが与えるマッチングは学生最適安定マッチングであることを示す**。そのために、「どの学生もDAアルゴリズムのどのステップにおいても自分にとって達成可能な大学からは絶対に不合格とされない」ことを示す。
> 　背理法を用いて示す。<font color=red>DAアルゴリズムのステップにおいて「最も早く」達成可能な大学から不合格にされた学生を$s$、不合格にした大学を$c$と仮定する</font>。そして、$s$にとって$c$が達成可能な何らかの安定マッチングを $\mu(c)=s$ とする。この時、以下の2つの帰結を得る。
> - ①$c$は$s$とは別の学生$s'$をキープしていた（$s'\succ_c s=\mu(c)$が成り立つ）
> - ②$s'$が$s$より先に$c$に出願した（$c\succ_{s'}\mu(s')$が成り立つ）
>
> つまり $①s'\succ_c \mu(c)かつ②c\succ_{s'}\mu(s')$ を満足することになり、これは<font color=red>「学生$s'$と大学$c$のペアが$\mu$をブロックできる」ことを意味し、安定性に矛盾する</font>。よって最初の仮定が間違っており、達成可能な相手から不合格とされる学生は存在しないことが示された。

> <font size=4><div align=center><b>【証明】</b></div></font>**学生応募制DAアルゴリズムが大学にとって最も好ましくない安定マッチングであることを示す**。そのために、「学生応募制DAアルゴリズムの帰結を$\mu^*$において、最も好ましくない安定マッチングにおけるマッチ相手とは異なる相手とペアになっている大学$c$が存在する」と仮定し、矛盾を導く。
> 　帰結$\mu^*$で$c$がペアになっている学生を$s$とすると、$\mu^*(c)=s$が成立する。この時、<font color=red>$c$にとって達成可能だが「$s$よりも好ましくない学生$s'$」が存在すると仮定</font>すると、$s\succ_c s'=\mu(c)$が成立する。ここで、$\mu(c)$は$s'$と$c$がペアになるような安定マッチングを表す。$\mu^*$は学生最適安定マッチングなので $c\succ\mu(s)$であり、以上より、以下の式が成り立つ。$$
> s\succ_c\mu(c)かつc\succ_s\mu(s)
> $$しかし、これは<font color=red>「$s$と$c$のペアが$\mu$をブロックできる」ことを意味し、安定性に矛盾する</font>。よって最初の仮定が間違っており、達成可能な中で最も好ましくない学生とマッチングしていることが示された。

<div style="page-break-before:always"></div>

### 僻地病院定理

$$
【\bold{定理}】\color{red}僻地病院定理\color{black}\\
ある安定マッチングでペアのいない（外部オプションとマッチしている）\\
学生や大学は他のどんな安定マッチングでもペアとなる相手がいない。
$$

> <font size=4><div align=center><b>【証明】</b></div></font>学生最適安定マッチングを$\mu^*$とし、任意の安定マッチングを$\mu$とする。
> $$
> \begin{align*}
>   ①&\mu^*は学生にとって最適な安定マッチングなので、\\
>   &\muで入学している学生は\mu^*でも入学している。\\
>   \implies
>   ②&\mu^*は大学にとって最も好ましくない安定マッチングなので、\\
>   &\mu^*で学生を持つ大学は\muでも学生を持つはずである。\\
>   \implies
>   ③&1対1マッチングにおける\muにおいて「入学している学生の人数」と\\
>    &「学生を持つ大学の数」は等しくなければならない。\\
>   \implies
>   ④&\mu^*でペアとなる相手のいる学生や大学と\muで\\
>   &ペアとなる相手のいる学生や大学は等しくなければならない。\\
>   \implies
>   ⑤&マッチ相手を持つ人はどんな安定マッチングでも常に相手を持つが、\\
>   &マッチ相手を持たない人はどんな安定マッチングでも相手を持たない。
> \end{align*}
> $$

- **僻地病院定理**は「少しかわいそうな帰結が導かれる」。研修医最適安定マッチングにおいて研修医が誰も配属された内容な不人気な病院があったとすると、どのような安定マッチングにおいても研修医が誰も配属されないという帰結が導かれる。
- <font color=red><b>僻地病院定理</b>はある種の公平性を保証する定理でもある</font>。どの安定マッチングを選ぶかによって研修医と病院のどちらに有利なのかは変わるものの、そう大きくは変わらない。
- $2009$年、日本政府は僻地病院定理による研修医の「**地域偏在の問題**」を解消するために元々使っていたDAアルゴリズムをやめ、別の制度に変えた。結果として、「地域偏在の問題の軽減」はできたが、「安定性の喪失」になった。

<div style="page-break-before:always"></div>

## 耐戦略性

- 一般的に、マッチングの主催者が参加者の選好を全て知っていることはあり得ない。また、<font color=red>全ての参加者が正直に選好を申告してくれる保証もない</font>。DAアルゴリズムは真の選好の下では安定性という望ましい性質を持つが、嘘の情報があれば結果として得られるマッチングは安定的ではないかもしれない。
- **以降では**参加者たちの「真の選好」と「申告された選好」を区別する。

### 安定的かつ耐戦略的なメカニズムの不可能性


- <font color=red>参加者たちが申告した選好に対して何らかのマッチングを与える手続きを「<b>メカニズム</b>」</font>と呼び、メカニズムは望ましい結果を得るための実行手段になる。ここで、「安定的なメカニズム」と「耐戦略的なメカニズム」を説明する。
  - 【**安定的なメカニズム**】どのような申告に対してもその申告のもとで安定マッチングを選ぶようなメカニズム
  - 【**耐戦略的なメカニズム**】どの参加者についても嘘をつくことにインセンティブがないような（正直な申告をしたときよりも望ましい相手にマッチできないような）メカニズム
- DAアルゴリズムは安定的ではあるが、「**耐戦略性を満たさない**」。これは、望ましい性質を満たすかどうかを調べる上で非常に重要であるが、マーケットデザイナーの関心ごとではない。

<table>
    <caption><b>マーケットデザイナーの関心</b></caption>
	<tbody>
		<tr>
			<th>重要なこと</th>
			<th>重要でないこと</th>
		</tr>
		<tr>
			<td>
            ◼理論が現実の制度設計に<br>　<font color=red>どれくらい有用なのか</font><br>
            ◼メカニズムの結果が制度設計に<br>　<font color=red>どのような影響があるのか</font><br>
            ◼選好の虚偽申告は実際に<br>　どれくらい行われるのか<br>
            ◼虚偽申告によってどれくらい安定性が<br>　失われてしまうのか
            </td>
			<td>
            ◼制度設計の理論の完璧さ<br>
            ◼DAアルゴリズムは安定的ではあるが<br>　<b>耐戦略性を満たさない</b>
            </td>
		</tr>
	</tbody>
</table>

<div style="page-break-before:always"></div>

$$
【\bold{定理}】\\
安定的かつ耐戦略的なメカニズムは存在しない。
$$

> <font size=4><div align=center><b>【証明】</b></div></font>証明は非常にシンプル。なぜなら「任意の安定的なメカニズムに対してたった1つでも嘘をついて得をするような選好の組み合わせを見つければ良い」からである。
>
> $$
【\bold{真の選好}】\\
\succ s_1:c_1,c_2\\
\succ s_2:c_2,c_1\\
\succ c_1:s_2,s_1\\
\succ c_2:s_1,s_2\\[3mm]
【\bold{すべての安定マッチング}】\\[1mm]
(i)\left.
\begin{array}{ll}
s_1 \hearts c_1 \\[1mm]
s_2 \hearts c_2
\end{array}
\right.
\hspace{3mm}または\hspace{5mm}
(ii)\left.
\begin{array}{ll}
s_1 \hearts c_2 \\[1mm]
s_2 \hearts c_1
\end{array}
\right.
$$上記の選好と帰結に対して、虚偽の申告があった場合の帰結を考える。以下に虚偽の申告AとBを示し、さらにその時の帰結を示す。
> $$
【\bold{虚偽の申告A}とその\bold{帰結}】\\
\begin{align*}
\left.
\begin{array}{ll}
\succ s_1&:c_1,c_2\\
\succ s_2&:c_2,c_1\\
\color{red}\succ' c_1&\color{red}:s_2,\emptyset,s_1\\
\succ c_2&:s_1,s_2
\end{array}
\right.
&\Rightarrow
(i)\left.
\begin{array}{ll}
&s_1 \hearts c_2 \\[1mm]
&s_2 \hearts c_1
\end{array}
\hspace{2mm}(c_1が虚偽申告した場合)
\right.\\
\end{align*}
\\[4mm]
【\bold{虚偽の申告B}とその\bold{帰結}】\\
\begin{align*}
\left.
\begin{array}{ll}
\color{red}\succ' s_1&\color{red}:c_1,\emptyset,c_2\\
\succ s_2&:c_2,c_1\\
\succ c_1&:s_2,s_1\\
\succ c_2&:s_1,s_2
\end{array}
\right.
&\Rightarrow
(ii)\left.
\begin{array}{ll}
&s_1 \hearts c_1 \\[1mm]
&s_2 \hearts c_2
\end{array}
\hspace{2mm}(s_1が虚偽申告した場合)
\right.
\end{align*}
$$
> 上記の結果より、安定マッチング$(i)$のメカニズムを使うと大学$c_1$が虚偽申告することで得ができ、一方、安定マッチング$(ii)$のメカニズムを使うと学生$s_1$が虚偽申告することで得ができる。以上より、<font color=red>メカニズムに安定性を要求すると耐戦略性が成り立たない</font>。したがって、耐戦略的で安定的なメカニズムは存在しない。

<div style="page-break-before:always"></div>

### 片側耐戦略性

$$
【\bold{定理}】\\
\bold{\color{red}学生}/\bold{\color{blue}大学}応募制DAアルゴリズムは「\bold{\color{red}学生}/\bold{\color{blue}大学}側耐戦略性」を満たす。
$$

> <font size=4><div align=center><b>【直感的な証明】</b></div></font>DAアルゴリズムが片側耐戦略性を満たすことを直感的に説明するために、DAアルゴリズム（受け入れ保留アルゴリズム）と対極にある、いわば**受け入れ即決アルゴリズム**を考える。
> 　大学応募制受け入れ「即決」アルゴリズムの場合、大学は出願してきた学生の中から1人を選んで受け入れを確定させ、マッチングの場から撤退しなければならない。学生からすると「本当は第1志望の$c_1$に出願したいが、$c_1$は人気で不合格の可能性も高い。また、その間に第2志望の$c_2$の定員が埋まってしまうかもしれない。」と考えると<u>学生$s$は戦略的な虚偽申告の可能性が発生する</u>。一方、学生応募制DAアルゴリズムには「**受け入れ保留**」があり、第1志望から不合格を言い渡されたとしても第2志望の入学枠は自分に開かれているため、安心して正直に選好を申告できる、つまり、<font color=red>学生応募制DAアルゴリズムにおいて学生が嘘の申告によるインセンティブがない</font>。
> 【**補足**】学生応募制DAアルゴリズムは学生側グループ耐戦略性という性質をも満たす。複数の学生たちが結託して虚偽の選好を申告しても、正直申告する場合と比べて得をすることがない。

- 前項では不可能性定理を証明したが、一方で、DAアルゴリズムは「**片側耐戦略性**」という耐戦略性を弱めた条件を満たす。

## 多対1マッチング

### 感応的選好の仮定

$$
\begin{align*}
【\bold{学生の集合Sの集合S(c)}】&S(c)=\{S'\sube S:0≦|S'|≦q_c\}\\[1mm]
【\bold{感応的選好\color{red}\succ_c^*\color{black}}】&\hspace{-2mm}
\left.
\begin{array}{l}
\forall s,t\in S\backslash S',\hspace{1mm}S'\cup\{s\}\color{red}\succ_c^*\color{black} S'\cup\{t\}\iff s\succ_c t\\
\forall s\hspace{3mm}\in S\backslash S',\hspace{1mm}S'\cup\{s\}\color{red}\succ_c^*\color{black} S'\hspace{8.5mm}\iff s\succ_c\emptyset\\
\end{array}
\right.
\end{align*}
$$

- 多対1マッチングにおいて、「学生たちのバランスを考慮した評価」のような<font color=red>大学が複雑な選好を持っている場合「<b>安定マッチングが存在しない</b>」ことがある</font>。上式の拡張された選好$\succ_c^*$は「**感応性(responsiveness)**」と言い、「**感応的選好**」を定義できる。
【**※**】感応性という用語は「学生の集合に対する選好が学生個人に対する選好に対して感応的である」ということから来た言葉である。
- **感応性選好**の仮定はグループに対する選好が個々の選好のみに感応的であることを要求する、「**一種の独立性の条件**」である。

#### 感応的選好の例

$$
\begin{align*}
【\bold{入力1}】&\succ_c：s_1,s_2,s_3,s_4,s_5\\[1mm]
【\bold{入力2}】&A=\{s_1,s_2,s_3,s_4\}、B=\{s_1,s_3,s_4,s_5\}\\[1mm]
【\bold{感応的選好}】&A \succ_c^* B
\end{align*}
$$

- 上式のように、大学$c$の選好$\succ_c$（入力1）と学生グループ$A$と$B$（入力2）を考えた時、「大学$c$はグループ$A$をグループ$B$より好む」という意味を持つ。このように、<font color=red>感応的選好は「グループに対する選好を要求する条件」である</font>。

### 多対1でも成り立つことと成り立たないこと

- 感応的選好を仮定すると、1対1マッチングが成り立つ「多くの」結果が多対1マッチングでも成り立つことを示すことができる。

<table>
	<tbody>
		<tr>
			<th>1対1と多対1の<br>両方で成立すること</th>
			<th>1対1で成立するが、<br>多対1では成立しないこと</th>
		</tr>
		<tr>
			<td>
            ◼学生応募制DAアルゴリズムの帰結は学生最適安定<br>
            　マッチングであり、大学応募制DAアルゴリズムの<br>
            　帰結は大学最適安定マッチングである。<br>
            ◼僻地病院定理が成り立つ。ある安定マッチングで<br>
            　浪人する学生はどんな安定マッチングのもとでも<br>
            　浪人することになる。<br>
            ◼学生応募制DAアルゴリズムは学生側耐戦略性を満たす。
            </td>
			<td valign=top>
            ◼多対1では大学側耐戦略性を<br>
            　満たさない
            </td>
		</tr>
	</tbody>
</table>

<div style="page-break-before:always"></div>

## カップルがいるマッチング

- <font color=red>現実のマッチング市場にはカップルが多数参加している</font>。例えば、前述の**NRMP**では$5〜10\%$、**APPIC** では臨床心理学者全体の$1〜2\%$がカップルとしてマッチングに参加している。
  - 【**NRMP**】全米研修医マッチングプログラム（National Resident Matching Program）
  - 【**APPIC**】アメリカの臨床心理学博士号取得者とポスドク先とをマッチングさせるプログラム
- 「同じ地域の病院で働きたい、違う地域の病院で離れて働くのは嫌だ」など、カップルたちは以下の選好を持つ。しかし、 <font color=red>DAアルゴリズムは個人を独立した参加者として扱ってしまうため、「夫は東海岸のボストンで働くが、妻は西海岸のロサンゼルスで働く」ことになる可能性もある</font>。

### 安定マッチングの不可能性

$$
\begin{align*}
\succ_s&：c_1,c_2\\
\succ_{m,w}&：(c_1,c_2)\\
\succ_{c_1}&：m,s\\
\succ_{c_2}&：s,w
\end{align*}
$$

$$
\begin{align*}
&【\bold{ステップ1}】\left.
\begin{array}{l}
    s\hspace{2.3mm}-\\
    m-c_1\\
    w\hspace{.4mm}-c_2
\end{array}
\right.
\end{align*}\\[2mm]
\begin{align*}
&【\bold{ステップ2}】\left.
\begin{array}{l}
    s\hspace{1.3mm}-c_2\\
    m-c_1\\
    w\hspace{1.5mm}-
\end{array}
\right.
\end{align*}\\[2mm]
\begin{align*}
&【\bold{ステップ3}】\left.
\begin{array}{l}
    s\hspace{1.3mm}-c_2\\
    m\hspace{.8mm}-\\
    w\hspace{1.5mm}-
\end{array}
\right.
\end{align*}\\[2mm]
\begin{align*}
&【\bold{ステップ4}】\left.
\begin{array}{l}
    s\hspace{1.3mm}-c_1\\
    m\hspace{.8mm}-\\
    w\hspace{1.5mm}-
\end{array}
\right.
\end{align*}\\[2mm]
\begin{align*}
&【\bold{ステップ5}】\left.
\begin{array}{l}
    s\hspace{2.3mm}-\\
    m-c_1\\
    w\hspace{.4mm}-c_2
\end{array}
\right.
\end{align*}\\[2mm]
以降、【\bold{ステップ1}】〜【\bold{ステップ5}】を繰り返す\dots
$$

- 学生と大学の例で説明する。上式のように独身の学生$s$、結婚している学生のカップル$(m,w)$、そして大学$c_1$（定員1名）,$c_2$（定員1名）が参加しているマッチング市場を考える。ここで、<u>カップル$(m,w)$は夫$m$が$c_1$かつ妻$w$が$c_2$に入学する組合せでなければ浪人を選ぶとする</u>。
- 上記のように、<font color=red>カップルの選好を許容してDAアルゴリズムを適用すると【<b>ステップ1</b>】〜【<b>ステップ5</b>】を繰り返すことになり、安定マッチングが存在しない</font>。つまり、これまでのDAアルゴリズムを修正する必要がある。

### 選好の制限

- カップルの選好を許容するマッチングの場合、選好の範囲を制限することが必要になる。実際、**Klaus and Klijn（2005）** はそれぞれのカップルの選好について安定マッチングが存在するための十分条件を見つけており、またそれは、その条件がそれより弱いと安定的マッチングは存在しないという意味で、ほぼ必要条件でもある。

## 【補題】DAアルゴリズムが片側耐戦略性を満たすことの証明

$$
学生s\in S、大学c\in C、参加者i\in S\cup C、嘘の申告\succ_i'とする。\\[2mm]
【\bold{定義}】\\[1mm]
\begin{align*}
【\bold{メカニズム}】&M：\mathcal{P}\rightarrow\mathcal{M}\\
【\bold{強選好の集合}】&\mathcal{P}=(\mathcal{P_1},\mathcal{P_2},\dots)\\
【\bold{選好プロファイル}】&\mathcal{P_i}=(\succ_{s_1},\succ_{s_2},\dotsb,\succ_{c_1},\succ_{c_2},\dotsb)\\
【\bold{メカニズムのSP}】&\overline{M_i(\succ_i',\succ_{-i})\succ_iM_i(\succ_i,\succ_{-i})}\\
【\bold{学生側耐戦略性}】&\overline{M_s(\succ_s',\succ_{-s})\succ_sM_s(\succ_s,\succ_{-s})}
\end{align*}
\\[3mm]
【\bold{定理}】\\
1対1学生応募制DAアルゴリズムは学生側耐戦略性を満たす。
$$

> <font size=4><div align=center><b>【証明】</b></div></font>背理法で示す。**メカニズム$M$を学生応募制DAアルゴリズムとする**。このとき、ある学生$s\in S$、ある選好プロファイル $\succ\in\mathcal{P}_{S\cup C}$ 、学生$s$による嘘の選好 $\succ_s'\in\mathcal{P}$ があるとし、以下の仮定の矛盾を導く。
> $$
> M_s(\succ_s',\succ_{-s})\succ_sM_s(\succ)
> $$ここで、一般性を失うことなく $s$ の正直な選好 $\succ_s$ を以下のように定義し、嘘をついた時の $s$ のマッチ相手 $c_k$ は以下のように表現できる。
> $$
> \begin{align*}
> 【\bold{正直な選好}】&\succ_s：c_1,\dots,c_k,c_{k+1},\dots,\emptyset\\
> 【\bold{虚偽申告時のマッチ相手}】&M_s(\succ_s',\succ_{-i})=c_k\hspace{3mm}（1≦k≦m）\\
> \end{align*}
> $$
> 

<div style="page-break-before:always"></div>

---

#### 参考文献

<ol class="brackets">
  <li>Hatfield, John W. and Paul R.Milgrom (2005) "Matching with Contracts," <i>American Economic Review</i>, 95(4), pp.913-935.</li>
  <li>Klaus, Bettina and Flip Klijn (2005) "Stable Matchings and Preferences of Couples," <i>Journal of Economic Theory</i>, 121(1), pp.75-106.</li>
  <li>Klaus, Bettina, Flip Klijn, and Toshifumi Nakamura (2009) "Corrigendum: Stable Matchings and Preferences of Couples," <i>Journal of Economic Theory</i>, 144(5), pp.2227-2233.</li>
  <li>Roth, Alvin E. (1985) "The College Admissions Problem is Not Equivalent to the Marriage Problem," <i>Journal of Economic Theory</i>, 36(2), pp.277-288.</li>
  <li>Roth, Alvin E. and Marilda A. Oliveira Sotomayor (1990) <i>Two-Sided Matching: A Study in Game-Theoretic Modeling and Analysis</i>, Cambridge University Press.</li>
  <li>Sonmez, Tayfun (1997) "Manipulation via Capacities in Two-Sided Matching Markets," <i>Journal of Economic Theory</i>, 77(1), pp.197-204.</li>
</ol>