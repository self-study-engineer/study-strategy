from da_algorithm import *;

def example_one_to_one():
    """
    実行例 1: 1対1マッチング（男女マッチング）
    """
    print("=" * 50)
    print("例1: 1対1マッチング（女性提案 DA）")
    print("=" * 50)
    print()

    data = DAInput(
        proposer_prefs=[
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ],
        receiver_prefs=[
            [2, 3, 1],
            [1, 3, 2],
            [3, 2, 1],
        ],
        proposer_label="女性",
        receiver_label="男性",
    )
    deferred_acceptance(data)


def example_one_to_one_unmatched():
    """
    例3: 1対1マッチング（余りあり: 提案者 > 受入側）
    """
    print("=" * 50)
    print("例3: 1対1マッチング（余りあり: 女性4人, 男性3人）")
    print("=" * 50)
    print()

    # w1〜w4 が w1 > w2 > w3 の順で m1 を争う。
    # 定員は各男性 1 名なので女性 1 名が必ず unmatched になる。
    data = DAInput(
        proposer_prefs=[
            [1, 2, 3],   # w1: m1 > m2 > m3
            [1, 3, 2],   # w2: m1 > m3 > m2
            [2, 1, 3],   # w3: m2 > m1 > m3
            [2, 3, 1],   # w4: m2 > m3 > m1
        ],
        receiver_prefs=[
            [1, 2, 3, 4],   # m1: w1 > w2 > w3 > w4
            [3, 4, 1, 2],   # m2: w3 > w4 > w1 > w2
            [2, 4, 3, 1],   # m3: w2 > w4 > w3 > w1
        ],
        proposer_label="女性",
        receiver_label="男性",
    )
    deferred_acceptance(data)



if __name__ == "__main__":
    example_one_to_one()
    example_one_to_one_unmatched()
