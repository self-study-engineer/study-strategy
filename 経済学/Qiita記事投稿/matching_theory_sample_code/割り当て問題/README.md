# matching_theory_sample_code

『マッチング理論とマーケットデザイン』第7章・第9章のアルゴリズムを Python で実装したサンプルコードです。確率を `fractions.Fraction` で厳密に計算し、教科書の確率行列・分解（`5/12`, `1/3`, `1/6` など）を誤差なく再現します。メカニズム本体と基本版の性質検証は標準ライブラリのみで動きます（Python 3.10+）。**例外として `extended_assignment_check.py`（制約対応の性質検証）だけは numpy / scipy を使います**（`pip install numpy scipy`。未導入でも順序効率性以外は動作し、順序効率性のみスキップされます）。

同フォルダの両側マッチング実装（`da_algorithm.py` ＋ `matching_check.py`）と同じ規約に揃えています。各アルゴリズムは `<名前>_algorithm.py`（実装）と `<名前>_algorithm_exec.py`（実行例）に分け、性質検証は `assignment_check.py`（`matching_check.py` の片側マッチング版）に集約しています。

## 構成

| ファイル | 内容 | 対応章 |
| --- | --- | --- |
| `rp_algorithm.py` | RPメカニズム（均等確率優先順位）。全 n! 順序を列挙して厳密な確率行列を計算。共通の入力 `Input` / 出力 `ProbabilityMatrix` もここで定義。 | 第7章 |
| `ps_algorithm.py` | PSメカニズム（同時確率消費／イーティングアルゴリズム）。連続的な「食べる」過程をイベント駆動で厳密にシミュレート。 | 第7章 |
| `bvn_algorithm.py` | バーコフ＝フォン・ノイマンの定理。二重確率行列を二部マッチングで置換行列の凸結合に分解。 | 第9章 |
| `assignment_check.py` | 性質検証モジュール。水平性・無羨望性・順序効率性・耐戦略性を検証し、`compare_mechanisms` でRP/PSを比較。 | 第7章 |
| `rp_algorithm_exec.py` | RPの実行例（厳密計算＋モンテカルロ近似＋性質検証）。 | 第7章 |
| `ps_algorithm_exec.py` | PSの実行例（例1・例2＋性質検証）。 | 第7章 |
| `bvn_algorithm_exec.py` | BvN分解の実行例。PSの確率行列をBvN分解で「実現」する連携例を含む。 | 第7・9章 |
| `extended_rp_algorithm.py` | 拡張RPメカニズム。制約を満たす範囲で逐次独裁制を行い、全順序列挙で厳密な期待行列を計算。**単体で完結**（モデル・制約・チェック・表示を自前で持つ）。 | 第9章 |
| `extended_ps_algorithm.py` | 拡張PSメカニズム。獲得可能性（available）に基づくイベント駆動イーティングで順序効率的な期待行列を計算。**単体で完結**。 | 第9章 |
| `extended_rp_algorithm_exec.py` | 拡張RPの実行例（会社の案件割り当て・4シナリオ）。 | 第9章 |
| `extended_ps_algorithm_exec.py` | 拡張PSの実行例（会社の案件割り当て・4シナリオ）。 | 第9章 |
| `extended_assignment_check.py` | **制約対応の性質検証モジュール**（`assignment_check.py` の拡張版）。水平性・無羨望性・順序効率性・耐戦略性を上限制約込みで検証。numpy でベクトル化、順序効率性は scipy.linprog で判定。 | 第9章 |

## 実行方法

```bash
cd matching_theory_sample_code

python3 rp_algorithm_exec.py            # RPメカニズム（第7章・性質検証つき）
python3 ps_algorithm_exec.py            # PSメカニズム（第7章・性質検証つき）
python3 bvn_algorithm_exec.py           # BvN分解 / PS→BvN連携（第7・9章）

python3 extended_rp_algorithm_exec.py   # 拡張RP（第9章・会社の案件割り当て3シナリオ）
python3 extended_ps_algorithm_exec.py   # 拡張PS（第9章・会社の案件割り当て3シナリオ）
```

## 性質の検証（assignment_check.py）

`rp_algorithm_exec.py` / `ps_algorithm_exec.py` は `assignment_check.check_all` で各メカニズムの性質を検証します（すべて `Fraction` で厳密判定）。第7章の理論どおり、RPは耐戦略性・水平性を満たすが順序効率性・無羨望性を満たさないこと、PSは順序効率性・無羨望性を満たすが耐戦略性を満たさないことが確認できます。

- **水平性**: 同じ選好を申告した個人の確率行が一致するか。
- **無羨望性**: 各個人が自分の割り当てで他人の割り当てを弱確率支配するか。
- **順序効率性**: 非浪費性（余っている財より好みの劣る対象を正の確率で消費していないこと）と、Bogomolnaia–Moulin (2001) の特徴づけ「関係 τ_P が非巡回」の両方で判定。τ_P の非巡回性だけで順序効率性と同値になるのは全財が完全配分される設定であり、∅ や余剰供給がある本設定では非浪費性の確認が必要になる。RPの帰結には改善サイクルが見つかり非効率と分かる。
- **耐戦略性**: 各個人の全虚偽申告（O∪{∅} の全順序）でメカニズムを再実行し、正直申告が虚偽申告を弱確率支配しない（得する効用が存在する）ケースを探す。PSでは個人が虚偽申告で得できることが検出される。

## 3つのアルゴリズムの関係

第7章でPSメカニズムは「確率行列だけを定め、確定的配分は直接与えない」と述べられ、その実現方法は第9章に委ねられています。本コードはその流れを再現します。

```
PSメカニズム（第7章）          BvN定理（第9章）
  選好 → 確率行列 P     ──→     P = Σ λ_k · P^k（置換行列の凸結合）
                                = 「確率 λ_k でくじを引き、確定割り当て P^k を実行」
```

`bvn_algorithm_exec.py` の `example_ps_to_bvn()` で、PSが出した確率行列を実際にBvN分解し、再構成が元の行列と一致することを確認しています。

## 制約付きの拡張（第9章・会社の案件割り当て）

現実の割り当てには複雑な制約が伴う。第9章の拡張メカニズムを使い、社員を案件（プロジェクト）に割り当てる問題を3つの制約シナリオで解きます（`extended_rp_algorithm_exec.py` / `extended_ps_algorithm_exec.py`）。`extended_rp_algorithm.py` と `extended_ps_algorithm.py` はそれぞれ単体で完結しており、他のモジュールに依存しません。

- **実行例1: 1案件に複数人** — 案件ごとに必要人数（供給数）を設定。定員より多くの社員が同じ案件を希望すると確率的に分配されます（例: 4人が定員3の案件Aを希望 → 各人が確率 3/4）。
- **実行例2: ペア禁止** — 仲の悪い2人を同じ案件に入れない。各案件で `{(i,a),(j,a)} ≤ 1` という上限制約になります。
- **実行例3: 若手のみ禁止** — 3年目以下だけで案件を埋めない。各案件で「若手の人数 ≤ 定員−1」とし、最低1枠を中堅以上に確保します。

いずれも**上限制約（部分列制約）**で表現でき、拡張メカニズムが扱えます。

- **拡張RP**: くじで優先順位を決め、各社員が「供給に空きがあり、関係する上限制約を破らない」案件を順に選ぶ。
- **拡張PS**: 各社員が各時点で**獲得可能な**（available: 供給に空きがあり、関係する上限制約 `Σ_S < q̄_S`）案件のうち最も好きなものを食べる。

理論上、拡張PSは制約を満たしつつ**順序効率的**な期待行列を与えます（拡張RPは制約は満たすが順序効率的とは限らない）。なお、本実装は教科書の獲得可能性の定義に従い**上限制約のみ**を対象とします（「最低◯人」のような下限制約は Budish et al. (2013) の一般理論が必要で対象外）。

**実装可能性（分解可能性）に関する注意**: 拡張RPは構成上つねに「制約を満たす確定的割り当てのくじ」なので、期待行列は必ず実装可能です。一方、拡張PSの期待行列を確定的割り当てのくじとして実装（分解）できることが保証されるのは、制約構造が **bihierarchy**（2つの階層族の和。Budish, Che, Kojima and Milgrom 2013, 定理1）をなす場合です。実行例1〜3の制約は bihierarchy を満たしますが、**実行例4はペア禁止制約と若手制約が同一案件上で交差するため bihierarchy にならず、分解可能性は保証されません**（期待行列自体は制約を期待値の意味で満たします）。

## 計算量に関する注意

- **RP**: 厳密計算は全 n! 順序を列挙するため `O(n!·n)`。個人数が多い場合（目安 n>8）は `random_priority(data, n_samples=...)` でモンテカルロ近似に切り替えてください。
- **耐戦略性の検証**: 各個人について `(|O|+1)!` 個の虚偽申告を試すため、財の種類が多いと重くなります。
- **BvN**: n×n 行列は高々 `n² − 2n + 2` 個の置換行列に分解されます。分解は一意とは限りません（第9章・注意点1）。

## 参考文献

- 小島武仁・栗野盛光（2023）『マッチング理論とマーケットデザイン』第7〜9章
- Bogomolnaia, A. and H. Moulin (2001) "A New Solution to the Random Assignment Problem," *Journal of Economic Theory*, 100(2), pp.295-328.
- Che, Y.-K. and F. Kojima (2010) "Asymptotic Equivalence of Probabilistic Serial and Random Priority Mechanisms," *Econometrica*, 78(5), pp.1625-1672.
- Budish, E., Y.-K. Che, F. Kojima, and P. Milgrom (2013) "Designing Random Allocation Mechanisms: Theory and Applications," *American Economic Review*, 103, pp.585-623.
- Birkhoff, G. (1946) "Three Observations on Linear Algebra," *Universidad Nacional de Tucuman Revista*, A5, pp.147-151.
- von Neumann, J. (1953) "A Certain Zero-sum Two-person Game Equivalent to the Optimal Assignment Problem," *Contributions to the Theory of Games*, Vol.2.
