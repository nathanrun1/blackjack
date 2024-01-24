from blackjack import *
import math
import pickle

decisions = ["S", "H", "Su", "Sp", "D"]
decision_types = ["hand_action", "bet_sizing", "insurance"]


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


def basic_strategy_choice(hand, dealer_show, choices):
    hand_sum = blackjack_sum(hand.cards)
    dealer_show_rank = blackjack_rank(dealer_show.rank_val())
    decision_table = []
    if "Sp" in choices:
        # Split
        with open("./Tables/split.pickle", "rb") as handle:
            decision_table = pickle.load(handle)
        column_index = decision_table[0].index(dealer_show_rank)
        split_card_rank = blackjack_rank(hand.cards[0].rank_val())
        if split_card_rank == 10:
            row = next(row for row in decision_table[1:]
                       if row[0] == "TT")
        else:
            row = next(row for row in decision_table[1:]
                       if int(row[0][0]) == split_card_rank)
        decision = row[column_index]
        if isinstance(decision, tuple):
            print(decision)
            if decision[0] in choices:
                decision = decision[0]
            else:
                print(f"{decision[0]} not in {choices}")
                decision = decision[1]
        return decision
    elif hand_sum.soft:
        # Soft Sum
        with open("./Tables/soft_sum.pickle", "rb") as handle:
            decision_table = pickle.load(handle)
        column_index = decision_table[0].index(dealer_show_rank)
        row = next(row for row in decision_table[1:]
                   if int(row[0][1]) == blackjack_rank(hand.cards[0].rank_val()) or
                   int(row[0][1]) == blackjack_rank(hand.cards[1].rank_val()))
        decision = row[column_index]
        if isinstance(decision, tuple):
            if decision[0] in choices:
                decision = decision[0]
            else:
                decision = decision[1]
        return decision
    else:
        # Hard Sum
        with open("./Tables/hard_sum.pickle", "rb") as handle:
            decision_table = pickle.load(handle)
        column_index = decision_table[0].index(dealer_show_rank)
        if hand_sum.val >= 17:
            row = next(row for row in decision_table[1:]
                       if row[0] == 17)
        elif hand_sum.val <= 8:
            row = next(row for row in decision_table[1:]
                       if row[0] == 8)
        else:
            row = next(row for row in decision_table[1:]
                       if row[0] == hand_sum.val)
        decision = row[column_index]
        if isinstance(decision, tuple):
            print(decision)
            if decision[0] in choices:
                decision = decision[0]
            else:
                print(f"{decision[0]} not in {choices}")
                decision = decision[1]
        return decision


class Bot:
    def __init__(self, **kwargs):
        name = kwargs.get("name")
        bankroll = kwargs.get("bankroll")
        self.is_bot = True
        if bankroll:
            self.bankroll = bankroll
            self.initial_bankroll = bankroll
        else:
            self.bankroll = rules["DEFAULT_BANKROLL"]
            self.initial_bankroll = rules["DEFAULT_BANKROLL"]
        if name:
            self.name = name
        else:
            self.name = f"Bot{random.randint(0, 999)}"
        self.total_rounds = 0
        self.wins = 0
        self.losses = 0

        self.bet_strategy = "uston"

    def __str__(self):
        return self.name

    def stats(self):
        return (f"NAME: {self.name}\nBANKROLL: ${self.bankroll}\nINITIAL BANKROLL: ${self.initial_bankroll}"
                f"\nNET WINNINGS: ${self.bankroll - self.initial_bankroll}"
                f"\nEV/ROUND: ${round((self.bankroll - self.initial_bankroll)/self.total_rounds, 4)}"
                f"\nUNIT EV/ROUND: {round(((self.bankroll - self.initial_bankroll)/self.total_rounds)/rules["MIN_BET"], 4)}"
                f"\n~EV/HOUR: ${round(((self.bankroll - self.initial_bankroll)/self.total_rounds)*60, 4)}/hr")

    # decide(self, decision_type, choices, **kwargs) provides the bot's decision based on multiple factors
    def decide(self, decision_type, choices, **kwargs):
        if decision_type == "hand_action":
            hands = kwargs.get("hands")
            deck = kwargs.get("deck")
            drawn_cards = deck.drawn
            current_hand = next((h for h in hands if h.open))
            dealer_showing = kwargs.get("dealer_show")

            # temp:
            # return "S"
            return basic_strategy_choice(current_hand, dealer_showing, choices)
        elif decision_type == "bet_sizing":
            deck = kwargs.get("deck")
            # HILO
            if self.bet_strategy != "min":
                true_count = 0
                if self.bet_strategy == "hilo":
                    true_count = hilo(deck)
                    print(f"True count: {true_count}")
                if self.bet_strategy == "uston":
                    true_count = uston(deck)
                    print(f"True count: {true_count}")
                    if true_count > 1:
                        return rules["MIN_BET"] * (true_count - 1)
                    else:
                        return rules["MIN_BET"]
                bet = 0
                min_bet = rules["MIN_BET"]
                if true_count == 1:
                    bet = min_bet * 1.5
                elif true_count == 2:
                    bet = min_bet * 2
                elif true_count == 3:
                    bet = min_bet * 3
                elif true_count == 4:
                    bet = min_bet * 3
                elif true_count in (5, 6):
                    bet = min_bet * 18
                elif true_count > 7:
                    bet = min_bet * 20
                else:
                    bet = min_bet
                return bet
            else:
                return rules["MIN_BET"]
        elif decision_type == "insurance":
            return "y"



Blackjack(bots_playing=True, bots=[Bot()],rounds=10000)