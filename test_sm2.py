from sm2 import sm2_update

ef_a, rep_a, int_a = 2.5, 0, 0  # always correct
ef_b, rep_b, int_b = 2.5, 0, 0  # always incorrect

for round in range(1, 4):
    ef_a, rep_a, int_a, next_a = sm2_update(ef_a, rep_a, int_a, 4)
    ef_b, rep_b, int_b, next_b = sm2_update(ef_b, rep_b, int_b, 2)
    print(f"Round {round}: correct word due in {int_a}d, wrong word due in {int_b}d")