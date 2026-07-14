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
        content: "Coffee Break " counter(chapter) "　";
    }
    h2::before {
        counter-increment: sub-chapter;
        content: "(" counter(sub-chapter) ") ";
    }
</style>

# 経営感覚を高めるPLの見方



# 左右がバランスするからバランスシートというのではない



# 会計のロジックは美しい



# 財務会計と管理会計



# 「人間」は財務諸表に出てこない



# 借金を返済するとPLのどこに表れるか


