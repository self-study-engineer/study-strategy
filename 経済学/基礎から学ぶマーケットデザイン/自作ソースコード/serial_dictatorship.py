"""
Serial Dictatorship (SD) — 順位優先方式

対応するマッチング問題:
  - 優先順位に基づく配分問題（住宅配分，学校選択など）
  - 初期保有のない配分問題

使い方:
  agent_prefs    : エージェント i の選好リスト（オブジェクトの番号, 1-indexed）
  priority_order : エージェントの優先順位（1-indexed のエージェント番号リスト）
                   リストの先頭が最高優先順位
  capacities     : オブジェクト j の定員（省略時はすべて 1）
  verbose        : True のとき各ステップを表示

性質:
  - パレート効率的
  - 耐戦略的（優先順位が外生的に固定された場合）
  - ただし誰を最高優先にするかが配分に強い影響を与える（公平性の問題）

Random Serial Dictatorship (RSD) との関係:
  優先順位をランダムに決定することで事前の公平性を担保する拡張が RSD。
"""

from dataclasses import dataclass


@dataclass
class SDInput:
    agent_prefs: list[list[int]]
    priority_order: list[int]
    capacities: list[int] | None = None
    agent_label: str = "A"
    object_label: str = "O"

    @property
    def n_agents(self) -> int:
        return len(self.agent_prefs)

    @property
    def n_objects(self) -> int:
        return max(
            max(pref) for pref in self.agent_prefs if pref
        )

    def get_capacities(self) -> list[int]:
        if self.capacities is None:
            return [1] * self.n_objects
        return self.capacities


@dataclass
class SDResult:
    allocation: list[int]   # allocation[i] = オブジェクトの0-index (-1 = unallocated)


def serial_dictatorship(data: SDInput, verbose: bool = True) -> SDResult:
    """
    Serial Dictatorship を実行し，優先順位ベースの配分を返す。

    各ステップで:
      1. 優先順位リストの先頭エージェントを選ぶ
      2. そのエージェントが残存オブジェクトの中から最も好きなものを取得（確定）
      3. オブジェクトの残定員が0になったら除外して次ステップへ
      4. 全員に配分されるか利用可能なオブジェクトがなくなるまで繰り返す
    """
    al = data.agent_label
    ol = data.object_label
    caps = data.get_capacities()

    allocation: list[int] = [-1] * data.n_agents
    remaining_caps: list[int] = caps[:]
    remaining_objects: set[int] = {j for j, c in enumerate(remaining_caps) if c > 0}

    if verbose:
        _print_preferences(data)
        print("=== Serial Dictatorship 開始 ===\n")

    for step, agent_1indexed in enumerate(data.priority_order, start=1):
        agent = agent_1indexed - 1

        if verbose:
            print(f"--- ステップ {step} ---")
            avail = ", ".join(f"{ol}{j+1}" for j in sorted(remaining_objects))
            print(f"  残存オブジェクト: {avail if avail else 'なし'}")
            print(f"  {al}{agent+1}（優先順位 {step} 位）が選択")

        if not remaining_objects:
            if verbose:
                print(f"  → 残存オブジェクトなし，{al}{agent+1} はマッチなし\n")
            continue

        # 選好リストの中で残存オブジェクトの最上位を選ぶ
        chosen = _top_available(agent, data.agent_prefs, remaining_objects)

        if chosen is None:
            if verbose:
                print(f"  → 選好リスト内に残存オブジェクトなし，{al}{agent+1} はマッチなし\n")
            continue

        allocation[agent] = chosen
        remaining_caps[chosen] -= 1
        if remaining_caps[chosen] <= 0:
            remaining_objects.discard(chosen)

        if verbose:
            print(f"  → {ol}{chosen+1} を取得（確定）\n")

    result = SDResult(allocation=allocation)

    if verbose:
        print("=== Serial Dictatorship 終了 ===\n")
        _print_result(result, data)

    return result


def _top_available(
    agent: int,
    agent_prefs: list[list[int]],
    remaining: set[int],
) -> int | None:
    for obj_1indexed in agent_prefs[agent]:
        obj = obj_1indexed - 1
        if obj in remaining:
            return obj
    return None


def _print_preferences(data: SDInput) -> None:
    al = data.agent_label
    ol = data.object_label
    print(f"【{al} の選好】")
    for i, pref in enumerate(data.agent_prefs):
        row = " ".join(f"{ol}{x}" for x in pref)
        print(f"  {al}{i+1}: {row}")
    print()
    print("【優先順位】")
    order_str = " > ".join(f"{al}{x}" for x in data.priority_order)
    print(f"  {order_str}")
    caps = data.get_capacities()
    if any(c != 1 for c in caps):
        print()
        print(f"【{ol} の定員】")
        for j, c in enumerate(caps):
            print(f"  {ol}{j+1}: {c}")
    print()


def _print_result(result: SDResult, data: SDInput) -> None:
    al = data.agent_label
    ol = data.object_label
    print("【配分結果】")
    for i, obj in enumerate(result.allocation):
        partner = f"{ol}{obj+1}" if obj != -1 else "マッチなし"
        print(f"  {al}{i+1}: {partner}")
    print()
