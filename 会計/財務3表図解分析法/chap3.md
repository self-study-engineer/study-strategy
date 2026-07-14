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

# PLとBSの作図方法について

## 作図ソフトについて



## 財務データの入手方法

### ①日本の会社の財務諸表の入手方法



### ②アメリカの会社の財務諸表の入手方法



## PLとBSの作図方法


