import math
from blackjack import blackjack_rank


# hilo(cards) returns Hi-Lo blackjack running count for all provided dealt cards
def hilo(deck):
    count = 0
    drawn = deck.drawn
    for card in drawn:
        bj_rank = blackjack_rank(card.rank_val())
        if 2 <= bj_rank <= 6:
            count += 1
        elif bj_rank == 10 or bj_rank == 1:
            count -= 1
    true_count = round(count / (len(deck.cards) / 52))
    return true_count


def uston(deck):
    count = 0
    drawn = deck.drawn
    for card in drawn:
        bj_rank = blackjack_rank(card.rank_val())
        if bj_rank == 10 or bj_rank == 1:
            count -= 3
        elif bj_rank == 9:
            count -= 1
        elif bj_rank == 8 or bj_rank == 2:
            count += 1
        elif bj_rank in (3, 4, 6, 7):
            count += 2
        elif bj_rank == 5:
            count += 3
    count += 3 * math.floor(len(deck.drawn) / 13)
    true_count = round(count / (len(deck.cards) / 26))
    return true_count
