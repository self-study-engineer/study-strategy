<style>
    body {
      counter-reset: chapter 2;
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

# 財務3表の読み解き方

## PLとBSを図にしてみる



<div style="page-break-before:always"></div>

## CS分析の方法


