"""
Deferred Acceptance (DA) Algorithm — 受入保留方式

対応するマッチング問題:
  - 1対1マッチング（男女マッチング、安定マッチング）
  - 多対1マッチング（大学入試、病院・研修医配属）

使い方:
  proposer_prefs : 提案者 i の選好リスト（受入側の番号, 1-indexed）
  receiver_prefs : 受入側 j の選好リスト（提案者の番号, 1-indexed）
  capacities     : 受入側 j の定員（省略時はすべて 1）
  verbose        : True のとき各ステップを表示
"""

from dataclasses import dataclass


@dataclass
class DAInput:
    proposer_prefs: list[list[int]]
    receiver_prefs: list[list[int]]
    capacities: list[int] | None = None
    proposer_label: str = "P"
    receiver_label: str = "R"

    @property
    def n_proposers(self) -> int:
        return len(self.proposer_prefs)

    @property
    def n_receivers(self) -> int:
        return len(self.receiver_prefs)

    def get_capacities(self) -> list[int]:
        if self.capacities is None:
            return [1] * self.n_receivers
        return self.capacities


@dataclass
class DAResult:
    proposer_match: list[int]   # proposer_match[i] = 受入側の0-index (-1 = unmatched)
    receiver_match: list[list[int]]  # receiver_match[j] = 提案者の0-indexリスト


def deferred_acceptance(data: DAInput, verbose: bool = True) -> DAResult:
    """
    提案者最適な安定マッチングを返す。
    各提案者は自分の選好順に受入側へ提案し、受入側は定員まで仮受入する。
    """
    P = data.n_proposers
    R = data.n_receivers
    caps = data.get_capacities()
    pl = data.proposer_label
    rl = data.receiver_label

    r_rank = _build_rank_table(data.receiver_prefs, P)

    proposer_match: list[int] = [-1] * P
    receiver_match: list[list[int]] = [[] for _ in range(R)]
    next_proposal = [0] * P
    free_proposers: set[int] = set(range(P))
    step = 1

    if verbose:
        _print_preferences(data)
        print("=== DA アルゴリズム 開始 ===\n")

    while free_proposers:
        if verbose:
            print(f"--- ステップ {step} ---")

        proposer = free_proposers.pop()

        if next_proposal[proposer] >= R:
            if verbose:
                print(f"  {pl}{proposer+1} は全受入側に提案済み → マッチなし\n")
            step += 1
            continue

        receiver = data.proposer_prefs[proposer][next_proposal[proposer]] - 1
        next_proposal[proposer] += 1

        if verbose:
            print(f"  {pl}{proposer+1} が {rl}{receiver+1} に提案")

        candidates = receiver_match[receiver] + [proposer]

        if len(candidates) <= caps[receiver]:
            receiver_match[receiver].append(proposer)
            proposer_match[proposer] = receiver
            if verbose:
                print(f"    → {rl}{receiver+1} が {pl}{proposer+1} を仮受入\n")
        else:
            worst = _find_worst(receiver, candidates, r_rank)
            if worst == proposer:
                free_proposers.add(proposer)
                if verbose:
                    print(f"    → {rl}{receiver+1} が {pl}{proposer+1} を拒否\n")
            else:
                receiver_match[receiver].remove(worst)
                receiver_match[receiver].append(proposer)
                proposer_match[proposer] = receiver
                proposer_match[worst] = -1
                free_proposers.add(worst)
                if verbose:
                    print(f"    → {rl}{receiver+1} が {pl}{worst+1} を解放し，{pl}{proposer+1} を仮受入\n")

        step += 1

    result = DAResult(proposer_match=proposer_match, receiver_match=receiver_match)

    print("=== DA アルゴリズム 終了 ===\n")
    _print_result(result, data)

    return result


def _build_rank_table(prefs: list[list[int]], target_size: int) -> list[list[int]]:
    """選好リスト (1-indexed) を順位表 (0-indexed) に変換する。"""
    rank = [[target_size] * target_size for _ in range(len(prefs))]
    for i, row in enumerate(prefs):
        for r, target in enumerate(row):
            rank[i][target - 1] = r
    return rank


def _find_worst(
    receiver: int,
    candidates: list[int],
    r_rank: list[list[int]],
) -> int:
    return max(candidates, key=lambda p: r_rank[receiver][p])


def _print_preferences(data: DAInput) -> None:
    pl = data.proposer_label
    rl = data.receiver_label
    print(f"【{pl} の選好】")
    for i, pref in enumerate(data.proposer_prefs):
        row = " ".join(f"{rl}{x}" for x in pref)
        print(f"  {pl}{i+1}: {row}")
    print()
    print(f"【{rl} の選好】")
    for j, pref in enumerate(data.receiver_prefs):
        row = " ".join(f"{pl}{x}" for x in pref)
        print(f"  {rl}{j+1}: {row}")
    caps = data.get_capacities()
    if any(c != 1 for c in caps):
        print()
        print(f"【{rl} の定員】")
        for j, c in enumerate(caps):
            print(f"  {rl}{j+1}: {c}")
    print()


def _print_result(result: DAResult, data: DAInput) -> None:
    pl = data.proposer_label
    rl = data.receiver_label
    print("【マッチング結果】")
    for i, r in enumerate(result.proposer_match):
        partner = f"{rl}{r+1}" if r != -1 else "マッチなし"
        print(f"  {pl}{i+1}: {partner}")
    print()
