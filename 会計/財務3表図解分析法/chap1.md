<style>
    body {
      counter-reset: chapter 0;
    }
    h1 {
        counter-reset: sub-chapter;
    }
    h2 {
        counter-reset: section;
    }

    h1::before {
        counter-increment: chapter;
        content: "第" counter(chapter) "章 ";
    }
    h2::before {
        counter-increment: sub-chapter;
        content: "(" counter(sub-chapter) ") ";
    }
</style>

# 財務分析の考え方を知ろう

## 会社にとって大切な4つの数字

<img src="images/1-1.png">

- 社長の大切な仕事の一つは事業全体のプロセスを効率よく運営することであり、株主から見て効率よく運営されているかどうかを評価する財務分析指標として自己資本利益率$ROE(Return\hspace{1mm}on\hspace{1mm}Equity)$がある。Returnは当期純利益、Equityは自己資本を表す。
- 財務諸表からざっくり会社の状況を把握するには以下の4つの指標を見る。

$$
\begin{align*}
①財務レバレッジ&=\frac{\color{red}総資本}{\color{orange}自己資本}\\[3mm]
②総資本回転率&=\frac{\color{blue}売上高}{\color{red}総資本}\\[3mm]
③当期純利益率&=\frac{\color{green}当期純利益}{\color{blue}売上高}\\[3mm]
④自己資本利益率&=\frac{\color{green}当期純利益}{\color{orange}自己資本}
\end{align*}
$$

<div style="page-break-before:always"></div>

## デュポン・モデル

<img src="images/1-2.png">

- 自己資本利益率(ROE)、当期純利益率、総資産回転率はいずれも高ければ高いほど良いが、財務レバレッジは異なる。<font color=red><b>財務レバレッジは事業経営の姿勢や方向性を表している指標</b></font>であり、<u>**良し悪しを判断する指標ではない**</u>。
- 財務レバレッジが高いと「意欲的に事業展開しているが高いリスクをとっている」と解釈でき、レバレッジが低いと「安定的な事業で挑戦的ではない事業運営をしている」と解釈できる。

$$
\begin{align*}
自己資本利益率&=\frac{\color{green}当期純利益}{\color{orange}自己資本}\\[3mm]
&=\frac{\color{green}当期純利益}{\color{blue}売上高}\times\frac{\color{blue}売上高}{\color{red}総資本}\times\frac{\color{red}総資本}{\color{orange}自己資本}\\[3mm]
&=当期純利益率\times 総資本回転率\times 財務レバレッジ
\end{align*}
$$

<div style="page-break-before:always"></div>

## キャッシュフロー分析

<table>
	<tbody>
		<tr>
			<th>パターン</th>
			<th>営業CF</th>
			<th>投資CF</th>
			<th>財務CF</th>
			<th>推測例</th>
		</tr>
		<tr>
			<td>①</td>
			<td><font color=red>＋</td>
			<td><font color=red>＋</td>
			<td><font color=red>＋</td>
			<td>営業活動で現金を生み出している。資産売却で<br>現金を取得している。借入などで現金を<br>増やしている。<b>将来の大きな投資のために<br>お金を集めているのだろうか。</td>
		</tr>
		<tr>
			<td>②</td>
			<td><font color=red>＋</td>
			<td><font color=red>＋</td>
			<td><font color=blue>ー</td>
			<td>営業活動で現金を生み出している。資産売却で<br>現金を取得している。借入の返済をしている。<br><b>財務体質を改善しようとしている会社だろうか。</td>
		</tr>
		<tr>
			<td>③</td>
			<td><font color=red>＋</td>
			<td><font color=blue>ー</td>
			<td><font color=red>＋</td>
			<td>営業活動で現金を生み出している。積極的に<br>投資活動をしている。借入などで現金を増やし<br>ている。<b>将来の戦略も明確な積極拡大型のパターン</td>
		</tr>
		<tr>
			<td>④</td>
			<td><font color=red>＋</td>
			<td><font color=blue>ー</td>
			<td><font color=blue>ー</td>
			<td>営業活動で現金を生み出している。積極的に<br>投資活動をしている.
            借入の返済をしている。<br><b>潤沢な営業CFがある会社だろう。</td>
		</tr>
		<tr>
			<td>⑤</td>
			<td><font color=blue>ー</td>
			<td><font color=red>＋</td>
			<td><font color=red>＋</td>
			<td>営業活動でマイナスが出ている。資産売却で<br>現金を取得している。借入などで現金を<br>増やしている。<b>問題会社の一般的なパターン</td>
		</tr>
		<tr>
			<td>⑥</td>
			<td><font color=blue>ー</td>
			<td><font color=red>＋</td>
			<td><font color=blue>ー</td>
			<td>営業活動でマイナスが出ている。資産売却で<br>現金を取得している。借入の返済をしている。<br><b>非常に多くの資産を持った会社なのかもしれない。</td>
		</tr>
		<tr>
			<td>⑦</td>
			<td><font color=blue>ー</td>
			<td><font color=blue>ー</td>
			<td><font color=red>＋</font></td>
			<td>営業活動でマイナスが出ている。積極的に<br>投資活動をしている。借入などで現金を<br>増やしている。<b>現状は苦しいがよほど将来に<br>自信があるのだろう。(希望的観測)</td>
		</tr>
		<tr>
			<td>⑧</td>
			<td><font color=blue>ー</td>
			<td><font color=blue>ー</td>
			<td><font color=blue>ー</td>
			<td>営業活動でマイナスが出ている。積極的に<br>投資活動をしている。借入の返済をしている。<br><b>過去によほどの現金の蓄積があったのだろう。</td>
		</tr>
	</tbody>
</table>

<div style="page-break-before:always"></div>

- PLは正しい利益を計算する表、BSはある時点の財産残高一覧表であり、いずれも現金の動きは見えてこない。CSを見れば1年間の現金の動きを確認でき、その会社の事業活動がわかる。
- <font color=red>CSは表の一番したの現金残高が、実際の現金残高と一致していないと、どこか間違っていることになるため、比較的粉飾しにくい。</font>
- キャッシュフローには3種類あり、それぞれの増減で解釈が異なる。
  - 【**営業CF**】営業活動による会社のお金の増減を表す。
  - 【**投資CF**】設備投資したり、有価証券を購入したりするとマイナス（<font color=blue>ー</font>）、逆に設備や有価証券を売却するとプラス（<font color=red>＋</font>）になる。
  - 【**財務CF**】借入金の返済や配当金があるとマイナス（<font color=blue>ー</font>）、借入金や新株発行すればプラス（<font color=red>＋</font>）になる。
- <b>パターン⑤（<font color=blue>ー</font>、<font color=red>＋</font>、<font color=red>＋</font>）は</b>「**問題のある会社**」であり、自分の会社の資産を切り売りしていると解釈できる。さらに、各CFについては以下の解釈ができる。
  - 【**営業CF**】営業活動をやればやるほど現金が少なくなっている。これは人件費や仕入支出が営業収入より多いことを意味し、営業効率が悪い。
  - 【**投資CF**】財務CFでも補填できなかったお金を設備や土地の売却で賄っていると解釈できる。
  - 【**財務CF**】営業CFがマイナスのため人からお金を借りていると解釈できる。
- 一方、<b>パターン②（<font color=red>＋</font>、<font color=red>＋</font>、<font color=blue>ー</font>）</b>や<b>④（<font color=red>＋</font>、<font color=blue>ー</font>、<font color=blue>ー</font>）</b>のように、営業CFがプラスの会社は借金を返済して自己資本比率の高い安定した企業を目指していたり、多額の配当で株主還元率が高いことが多く、財務CFがマイナスになる。
- さらに、<b>パターン③（<font color=red>＋</font>、<font color=blue>ー</font>、<font color=red>＋</font>）は</b>「営業CFによる会社の売上」と「財務CFによる借入金や社債発行」を集めて積極的な投資活動をしていると解釈でき、「<b>将来の戦略が明確な会社</b>s」と解釈することができる。
- <font color=red><b>財務分析では、PLとBSから4つの指標(ROE、当期純利益率、総資本回転率、財務レバレッジ)と、CSの8つのパターンをチェックする</b></font>。


```plantuml
@startuml
title 投資CFと財務CFの解釈
left to right direction

rectangle 投資CF as investment_cf
rectangle 財務CF as finance_cf
rectangle 固定資産の売買 as investment_cf_equipment
rectangle 有価証券の売買 as investment_cf_securities
rectangle 借入金の実行や返済 as finance_cf_loans
rectangle 配当や自己株式の取得 as finance_cf_dividends

investment_cf -- investment_cf_equipment
investment_cf -- investment_cf_securities
finance_cf -- finance_cf_loans
finance_cf -- finance_cf_dividends
investment_cf_equipment -[hidden]-finance_cf
@enduml
```
