import copy

from blackjack import *
from prettytable import PrettyTable as Pt
import numpy as np

# Table format:
# Rows: each row represents up card
# Values for each row: A, 2, 3, 4, 5, 6, 7, 8, 9, 10
# Columns: each column represents what dealer ends up with
# Values for each column: 17, 18, 19, 20, 21, Bust

# card_ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
card_ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
card_rank_probs = [1 / 13, 1 / 13, 1 / 13, 1 / 13, 1 / 13, 1 / 13, 1 / 13, 1 / 13, 1 / 13, 4 / 13]
deck_amount = 1
card_amounts = np.array([4, 4, 4, 4, 4, 4, 4, 4, 4, 16]) * deck_amount
card_ranks_nodup = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


USE_CARD_AMOUNTS = False


def bj_sum_rank(*ranks, ini_sum=None):
    if ini_sum:
        bj_sum = copy.deepcopy(ini_sum)
    else:
        bj_sum = {
            "sum": 0,
            "soft": False
        }
    for r in ranks:
        if not bj_sum["soft"]:
            if r == 1:
                if bj_sum["sum"] + 11 > 21:
                    bj_sum["sum"] += 1
                else:
                    bj_sum["sum"] += 11
                    bj_sum["soft"] = True
            else:
                bj_sum["sum"] += r
        else:
            if r == 1:
                bj_sum["sum"] += 1
            elif bj_sum["sum"] + r > 21:
                bj_sum["sum"] = bj_sum["sum"] + r - 10
                bj_sum["soft"] = False
            else:
                bj_sum["sum"] = bj_sum["sum"] + r
    return bj_sum


def make_bj_sum(value, soft):
    return {"sum": value, "soft": soft}


def run_sims(initial_sum, true_initial=True, rel_card_amounts=None):
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    base_row = np.array([0, 0, 0, 0, 0, 0, 0])
    ini_sum_val = initial_sum["sum"]
    ini_sum_soft = initial_sum["soft"]
    if ini_sum_val > 21:
        base_row[5] = 1
        return base_row
    elif ini_sum_val == 21:
        if true_initial:
            base_row[6] = 1
        else:
            base_row[4] = 1
        return base_row
    elif ini_sum_val >= 18:
        base_row[ini_sum_val - 17] = 1
        return base_row
    elif (ini_sum_val == 17) and ((not ini_sum_soft) or rules["STAND_SOFT_17"]):
        base_row[0] = 1
        return base_row
    else:
        # Dealer must hit
        total_outcomes = 0
        for r in card_ranks_nodup:
            if USE_CARD_AMOUNTS:
                used_card_amount = rel_card_amounts[card_ranks.index(r)]
                new_sum = bj_sum_rank(r, ini_sum=initial_sum.copy())
                new_rel_card_amounts = rel_card_amounts.copy()
                new_rel_card_amounts[card_ranks.index(r)] -= 1
                recursive_sim = run_sims(new_sum.copy(), true_initial=False, rel_card_amounts=new_rel_card_amounts)
                base_row = np.add(base_row, recursive_sim * (used_card_amount/np.sum(rel_card_amounts)), casting="unsafe")
                total_outcomes += 1
            else:
                new_sum = bj_sum_rank(r, ini_sum=initial_sum.copy())
                recursive_sim = run_sims(new_sum.copy(), true_initial=False)
                base_row = np.add(base_row, recursive_sim * card_rank_probs[card_ranks.index(r)],
                                  casting="unsafe")
                total_outcomes += 1
        return base_row


def create_row(up_card_rank):
    possible_initial_sums = []
    for r in card_ranks:
        new_sum = bj_sum_rank(up_card_rank, r)
        possible_initial_sums.append(new_sum.copy())
    base_row = np.array([0, 0, 0, 0, 0, 0, 0])
    for s in possible_initial_sums:
        sims = run_sims(s.copy())
        base_row = np.add(base_row, sims * (1 / len(possible_initial_sums)))
    total_outcomes = np.sum(base_row)
    prob_row = base_row / total_outcomes
    return np.round(prob_row, 4)


def create_dealer_table():
    dealer_odds_table = Pt(["Up Card", "17", "18", "19", "20", "21", "Bust", "BJ"])
    for r in card_ranks_nodup:
        if r == 1:
            dealer_odds_table.add_row(np.append("Ace", create_row(r)))
        else:
            dealer_odds_table.add_row(np.append(str(r), create_row(r)))
    return dealer_odds_table


# Note: For EV, 1 Unit represents your bet. So +1 EV represents doubling up, -1 is losing your bet
def get_stand_ev(dealer_up_card, hand_sum):
    dealer_odds = create_row(dealer_up_card)
    ev = 0
    if hand_sum.val < 17:
        for i in range(5):
            ev -= 1 * dealer_odds[i]
        ev += 1 * dealer_odds[5]
    elif hand_sum.val <= 21:
        for i in range(5):
            if hand_sum.val < 17 + i:
                ev -= 1 * dealer_odds[i]
            elif hand_sum.val > 17 + i:
                ev += 1 * dealer_odds[i]
        ev += 1 * dealer_odds[5]
    else:
        ev = -1
    return ev


def get_double_ev(dealer_up_card, hand_sum, rel_card_amounts=None):
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    ev = 0
    for r in card_ranks_nodup:
        new_sum = bj_sum_rank(r, ini_sum=hand_sum)
        result_ev = get_stand_ev(dealer_up_card, new_sum)
        if USE_CARD_AMOUNTS:
            card_prob = rel_card_amounts[card_ranks_nodup.index(r)] / np.sum(rel_card_amounts)
            ev += result_ev * card_prob * 2
        else:
            card_prob = card_rank_probs[card_ranks_nodup.index(r)]
            ev += result_ev * card_prob * 2
    return ev


def get_hit_ev(dealer_up_card, hand_sum, rel_card_amounts=None):
    ev = 0
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    if hand_sum.val >= 21:
        ev = -1
    else:
        for r in card_ranks_nodup:
            if USE_CARD_AMOUNTS:
                card_prob = rel_card_amounts[card_ranks_nodup.index(r)] / np.sum(rel_card_amounts)
            else:
                card_prob = card_rank_probs[card_ranks_nodup.index(r)]
            new_sum = bj_sum_rank(r, ini_sum=hand_sum)
            result_ev = np.max([get_stand_ev(dealer_up_card, new_sum),
                                get_hit_ev(dealer_up_card, new_sum, (rel_card_amounts if USE_CARD_AMOUNTS else None))])
            # print(f"EV on {new_sum}: {result_ev}")
            ev += result_ev * card_prob
    return ev


# print(run_sims(make_bj_sum(16, False)))
# print(create_row(6))
# print(create_dealer_table())
print(get_stand_ev(10, BJSum(20, False)))
# print(get_double_ev(6,BJSum(20, False)))
print(get_hit_ev(10, BJSum(20, False))) # wrong
