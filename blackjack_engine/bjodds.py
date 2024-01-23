import copy
import sys
import warnings
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
deck_amount = 80
card_amounts = np.array([4, 4, 4, 4, 4, 4, 4, 4, 4, 16]) * deck_amount
card_ranks_nodup = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


USE_CARD_AMOUNTS = False


def normalize(ls):
    ls_sum = np.sum(ls)
    for i in range(len(ls)):
        ls[i] = ls[i]/ls_sum
    return ls


def bj_sum_rank(*ranks, ini_sum=None):
    if ini_sum:
        bj_sum = copy.deepcopy(ini_sum)
    else:
        bj_sum = BJSum(0, False)
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
                new_sum = bj_sum_rank(r, ini_sum=copy.deepcopy(initial_sum))
                new_rel_card_amounts = rel_card_amounts.copy()
                new_rel_card_amounts[card_ranks.index(r)] -= 1
                recursive_sim = run_sims(copy.deepcopy(new_sum), true_initial=False, rel_card_amounts=new_rel_card_amounts)
                base_row = np.add(base_row, recursive_sim * (used_card_amount/np.sum(rel_card_amounts)), casting="unsafe")
                total_outcomes += 1
            else:
                new_sum = bj_sum_rank(r, ini_sum=copy.deepcopy(initial_sum))
                recursive_sim = run_sims(copy.deepcopy(new_sum), true_initial=False)
                base_row = np.add(base_row, recursive_sim * card_rank_probs[card_ranks.index(r)],
                                  casting="unsafe")
                total_outcomes += 1
        return base_row


def create_row(up_card_rank, rel_card_amounts=None):
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    possible_initial_sums = []
    for r in card_ranks:
        new_sum = bj_sum_rank(up_card_rank, r)
        possible_initial_sums.append(copy.deepcopy(new_sum))
    base_row = np.array([0, 0, 0, 0, 0, 0, 0])
    for s in possible_initial_sums:
        sims = run_sims(copy.deepcopy(s), rel_card_amounts=rel_card_amounts)
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
def get_stand_ev(dealer_up_card, hand_sum, rel_card_amounts=None):
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    dealer_odds = create_row(dealer_up_card, rel_card_amounts=rel_card_amounts)[slice(6)]
    dealer_odds = normalize(dealer_odds)
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


def get_hit_ev(dealer_up_card, hand_sum, rel_card_amounts=None, ev_results_storage=None):
    ev = 0
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    if ev_results_storage is None:
        ev_results_storage = {}
    if hand_sum.val >= 21:
        ev = -1
    else:
        for r in card_ranks_nodup:
            if USE_CARD_AMOUNTS:
                card_prob = rel_card_amounts[card_ranks_nodup.index(r)] / np.sum(rel_card_amounts)
            else:
                card_prob = card_rank_probs[card_ranks_nodup.index(r)]
            new_sum = bj_sum_rank(r, ini_sum=hand_sum)
            if new_sum in ev_results_storage.keys():
                result_ev = ev_results_storage[new_sum]
            else:
                result_ev = np.max([get_stand_ev(dealer_up_card, new_sum, rel_card_amounts=rel_card_amounts),
                                    get_hit_ev(dealer_up_card, new_sum, rel_card_amounts=rel_card_amounts,
                                               ev_results_storage=ev_results_storage)])
                ev_results_storage[new_sum] = result_ev
            # print(f"EV on {new_sum}: {result_ev}")
            ev += result_ev * card_prob
    return ev


def get_split_ev(dealer_up_card, player_card, rel_card_amounts=None):
    ev = 0
    if rel_card_amounts is None:
        rel_card_amounts = card_amounts
    hand_sum = bj_sum_rank(player_card,player_card)
    for r in card_ranks_nodup:
        if r != player_card:
            if USE_CARD_AMOUNTS:
                card_prob = rel_card_amounts[card_ranks_nodup.index(r)] / np.sum(rel_card_amounts)
            else:
                card_prob = card_rank_probs[card_ranks_nodup.index(r)]
            new_sum = bj_sum_rank(r, player_card)
            decision_evs = [get_stand_ev(dealer_up_card, new_sum, rel_card_amounts=rel_card_amounts)]
            if player_card != 1 or rules["HIT_AFTER_SPLIT_ACE"]:
                # print("getting hit ev")
                decision_evs.append(get_hit_ev(dealer_up_card, new_sum, rel_card_amounts=rel_card_amounts))
            if rules["DOUBLE_AFTER_SPLIT"]:
                # print('getting double ev')
                decision_evs.append(get_double_ev(dealer_up_card, new_sum, rel_card_amounts=rel_card_amounts))
            result_ev = np.max(decision_evs)
            ev += result_ev * card_prob
    expected_extra_hands = 0
    if player_card != 1 or rules["RE_SPLIT_ACE"]:
        for i in range(rules["MAX_SPLIT"] - 2):  # For every extra hand that could be split
            if USE_CARD_AMOUNTS:
                i_extra_prob = 1
                for j in range(i+1):
                    card_amount = max(card_amounts[card_ranks_nodup.index(player_card)] - j, 0)
                    card_prob = card_amount/np.sum(card_amounts)
                    i_extra_prob *= card_prob
            else:
                card_prob = card_rank_probs[card_ranks_nodup.index(player_card)]
                i_extra_prob = card_prob ** (i + 1)
            expected_extra_hands += i_extra_prob
    ev *= (2 + expected_extra_hands)
    return ev


def get_optimal_decision(dealer_up_card, ini_card_ranks=None, hand_sum=None):
    if hand_sum is None and ini_card_ranks:
        hand_sum = bj_sum_rank(ini_card_ranks[0], ini_card_ranks[1])
        can_split = (ini_card_ranks[0] == ini_card_ranks[1])
    elif ini_card_ranks is None and hand_sum:
        can_split = False
    else:
        warnings.warn("get_optimal_decision() called without sufficient info")
        return False  # Not enough info
    stand = get_stand_ev(dealer_up_card, hand_sum)
    hit = get_hit_ev(dealer_up_card, hand_sum)
    double = get_double_ev(dealer_up_card, hand_sum)
    surrender = -0.5
    split = None
    if can_split:
        split = get_split_ev(dealer_up_card, ini_card_ranks[0])
    decisions = [stand, hit, double, surrender]
    if can_split:
        decisions.append(split)
    decisions_sorted = np.sort(decisions)[::-1]
    decision_names_sorted = []
    for decision in decisions_sorted:
        if stand == decision:
            decision_names_sorted.append("S")
        elif hit == decision:
            decision_names_sorted.append("H")
        elif double == decision:
            decision_names_sorted.append("D")
        elif split == decision:
            decision_names_sorted.append("Sp")
        else:
            decision_names_sorted.append("Su")
    top_dec = decision_names_sorted[0]
    sec_dec = decision_names_sorted[1]
    if top_dec == "Su" or top_dec == "Sp" or top_dec == "D":
        return f"{top_dec} | {sec_dec}"
    else:
        return top_dec

def create_gto_tables(h=True,s=True,sp=True):
    hard_table = Pt(["", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Ace"])
    soft_table = Pt(["", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Ace"])
    split_table = Pt(["", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Ace"])
    if h:
        # Hard Sum Table:
        progress = 0
        for i in range(10):
            c_sum = 17 - i
            row = [str(c_sum)]
            for r in card_ranks_nodup:
                progress += 1
                b = "Creating Hard Sum Table... " + str(progress) + "%"
                sys.stdout.write('\r'+b)
                row.append(get_optimal_decision(r, hand_sum=BJSum(c_sum, False)))
            ace_col = row.pop(1)
            row.append(ace_col)
            hard_table.add_row(row)
        print("\n")
        print(hard_table)
    if s:
        # Soft Sum Table:
        progress = 0
        for i in range(8):
            c_sum = 20 - i
            row = [f"A{c_sum-11}"]
            for r in card_ranks_nodup:
                progress += (1/80) * 100
                b = "Creating Soft Sum Table... " + str(progress) + "%"
                sys.stdout.write('\r' + b)
                row.append(get_optimal_decision(r, hand_sum=BJSum(c_sum, True)))
            ace_col = row.pop(1)
            row.append(ace_col)
            soft_table.add_row(row)
        print("\n")
        print(soft_table)
    if sp:
        # Split Table:
        progress = 0
        for i in range(10):
            card = i + 1
            row = []
            if i == 1:
                row.append("AA")
            else:
                row.append(f"{card}{card}")
            for r in card_ranks_nodup:
                progress += 1
                b = "Creating Split Table... " + str(progress) + "%"
                sys.stdout.write('\r' + b)
                row.append(get_optimal_decision(r, ini_card_ranks=[card, card]))
            ace_col = row.pop(1)
            row.append(ace_col)
            split_table.add_row(row)
        print("\n")
        print(split_table)



create_gto_tables(h=False, s=False, sp=True)
# print(run_sims(make_bj_sum(16, False)))
# print(create_row(6))
# print(create_dealer_table())
# print(get_stand_ev(10, BJSum(16, False)))
# print(get_double_ev(6,BJSum(20, False)))
# print(get_optimal_decision(10, [2, 2]))
# dealer_odds = create_row(10)
# dealer_odds = dealer_odds[0:6]



