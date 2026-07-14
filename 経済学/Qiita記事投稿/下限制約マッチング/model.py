"""
model.py — 下限制約マッチング: データ構造

参考文献:
    Goto et al. (2016) "Strategyproof matching with regional minimum and maximum quotas"
    Artificial Intelligence 235, 40-57.

モデル定義 (Section 2):
    - 市場 (S, C, R, p, q, ≻_S, ≻_C, X, ≻_PL)
    - 地域 R は階層木 (hierarchical region) を仮定 (Definition 6, 7)
    - コントラクト x = (s, c) ∈ X = S × C
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# 地域木 (Region Tree)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RegionNode:
    """
    地域木の1ノード (= 1地域)。

    Attributes
    ----------
    name       : 地域名（表示用）
    schools    : この地域に含まれる学校インデックスの集合
    min_quota  : 地域最低定員 p_r  (0 ≤ p_r ≤ q_r)
    max_quota  : 地域最高定員 q_r
    children   : 子ノードのリスト（葉ノードでは空）
    parent     : 親ノード（ルートでは None）
    """
    name: str
    schools: frozenset[int]
    min_quota: int
    max_quota: int
    children: list[RegionNode] = field(default_factory=list)
    parent: RegionNode | None = field(default=None, repr=False)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def all_nodes(self) -> list[RegionNode]:
        """自身を含む全子孫ノードを返す (DFS順)。"""
        result: list[RegionNode] = [self]
        for child in self.children:
            result.extend(child.all_nodes())
        return result

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


@dataclass
class RegionTree:
    """
    地域の階層木。

    ルートは全学校を含む地域 C。
    葉は個々の学校 {c} に対応。
    """
    root: RegionNode

    def all_nodes(self) -> list[RegionNode]:
        return self.root.all_nodes()

    def leaf_nodes(self) -> list[RegionNode]:
        return [n for n in self.all_nodes() if n.is_leaf()]

    def internal_nodes(self) -> list[RegionNode]:
        return [n for n in self.all_nodes() if not n.is_leaf()]

    def node_for_school(self, school_idx: int) -> RegionNode:
        """学校インデックスに対応する葉ノードを返す。"""
        for node in self.leaf_nodes():
            if school_idx in node.schools:
                return node
        raise ValueError(f"School {school_idx} not found in tree.")


# ─────────────────────────────────────────────────────────────────────────────
# 市場 (Market)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Market:
    """
    マッチング市場の全データ。

    Attributes
    ----------
    student_names   : 学生名のリスト（長さ n）
    school_names    : 学校名のリスト（長さ m）
    student_prefs   : student_prefs[s] = 学生 s の選好順（学校インデックスのリスト、先が好み）
    school_priors   : school_priors[c] = 学校 c の優先順（学生インデックスのリスト、先が高優先）
    region_tree     : 地域の階層木
    tiebreak_order  : 優先リスト PL 生成時の学校タイブレーク順（学校インデックスのリスト）
                      デフォルトは [0, 1, ..., m-1]
    """
    student_names: list[str]
    school_names: list[str]
    student_prefs: list[list[int]]
    school_priors: list[list[int]]
    region_tree: RegionTree
    tiebreak_order: list[int] | None = None

    # ── 派生プロパティ ─────────────────────────────────────────────────────

    @property
    def n_students(self) -> int:
        return len(self.student_names)

    @property
    def n_schools(self) -> int:
        return len(self.school_names)

    def s_name(self, s: int) -> str:
        return self.student_names[s]

    def c_name(self, c: int) -> str:
        return self.school_names[c]

    # ── 優先順位 (rank) ───────────────────────────────────────────────────

    def school_rank(self, c: int, s: int) -> int:
        """
        学校 c における学生 s の順位（0-origin, 小さいほど高優先）。
        rank_c(s) に対応 (Section 2 の定義)。
        """
        try:
            return self.school_priors[c].index(s)
        except ValueError:
            return self.n_students  # リストにない学生は最低優先

    def student_rank(self, s: int, c: int) -> int:
        """学生 s における学校 c の選好順位（0-origin, 小さいほど好み）。"""
        try:
            return self.student_prefs[s].index(c)
        except ValueError:
            return self.n_schools

    # ── 優先リスト (PL) ───────────────────────────────────────────────────

    def priority_list(self) -> list[tuple[int, int]]:
        """
        全コントラクト (s, c) を PL 順にソートして返す。

        PL 定義 (Section 2):
          (s, c_i) ≻_PL (s', c_j)  iff
            rank_{c_i}(s) < rank_{c_j}(s')  または
            rank_{c_i}(s) = rank_{c_j}(s') かつ i < j (タイブレーク)
        """
        tiebreak = self.tiebreak_order or list(range(self.n_schools))
        tiebreak_rank = {c: i for i, c in enumerate(tiebreak)}

        contracts = [
            (s, c)
            for s in range(self.n_students)
            for c in range(self.n_schools)
        ]
        contracts.sort(
            key=lambda sc: (
                self.school_rank(sc[1], sc[0]),   # rank_c(s)
                tiebreak_rank[sc[1]],              # タイブレーク
            )
        )
        return contracts

    # ── 個別定員 ──────────────────────────────────────────────────────────

    def individual_min_quota(self, c: int) -> int:
        """学校 c の個別最低定員 p_{c}。葉ノードの min_quota を参照。"""
        return self.region_tree.node_for_school(c).min_quota

    def individual_max_quota(self, c: int) -> int:
        """学校 c の個別最高定員 q_{c}。葉ノードの max_quota を参照。"""
        return self.region_tree.node_for_school(c).max_quota


# ─────────────────────────────────────────────────────────────────────────────
# 木構築ユーティリティ
# ─────────────────────────────────────────────────────────────────────────────

def build_tree_from_dict(
    tree_def: dict,
    n_students: int,
    school_names: list[str],
) -> RegionTree:
    """
    辞書形式の木定義から RegionTree を構築する。

    tree_def の形式:
    {
        "name": "全国",
        "min_quota": 8,
        "max_quota": 8,
        "children": [
            {
                "name": "地域A",
                "min_quota": 3,
                "max_quota": 5,
                "children": [
                    {"name": "c1", "school_idx": 0, "min_quota": 1, "max_quota": 3},
                    {"name": "c2", "school_idx": 1, "min_quota": 1, "max_quota": 3},
                ]
            },
            ...
        ]
    }

    葉ノードは "school_idx" キーを持ち、children は持たない。
    ルートノードの min_quota/max_quota は自動的に n_students に設定される（拘束なし）。
    """

    def _build(d: dict, parent: RegionNode | None = None) -> RegionNode:
        is_leaf = "school_idx" in d
        if is_leaf:
            idx = d["school_idx"]
            node = RegionNode(
                name=d.get("name", school_names[idx]),
                schools=frozenset([idx]),
                min_quota=d.get("min_quota", 0),
                max_quota=d.get("max_quota", n_students),
                children=[],
                parent=parent,
            )
        else:
            children_defs = d.get("children", [])
            node = RegionNode(
                name=d.get("name", "region"),
                schools=frozenset(),  # 後で集約
                min_quota=d.get("min_quota", 0),
                max_quota=d.get("max_quota", n_students),
                children=[],
                parent=parent,
            )
            for cd in children_defs:
                child = _build(cd, parent=node)
                node.children.append(child)
            # schools を子から集約
            object.__setattr__(
                node, "schools",
                frozenset().union(*(c.schools for c in node.children))
            )
        return node

    root = _build(tree_def)
    # ルートは非拘束（n students）
    root.min_quota = n_students
    root.max_quota = n_students
    return RegionTree(root=root)
