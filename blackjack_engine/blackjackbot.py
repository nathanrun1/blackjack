from blackjack import *

decisions = ["S", "H", "Su", "Sp", "D"]
decision_types = ["hand_action", "bet_sizing", "insurance"]


# hilo(cards) returns Hi-Lo blackjack running count for all provided dealt cards
def hilo(cards):
    count = 0
    for card in cards:
        bj_rank = blackjack_rank(card.rank_val())
        if 2 <= bj_rank <= 6:
            count += 1
        elif bj_rank == 10:
            count -= 1
    return count


def basic_strategy_choice(hand, dealer_show, choices):
    hand_sum = blackjack_sum(hand.cards)
    dealer_show_rank = blackjack_rank(dealer_show.rank_val())


class Bot:
    def __init__(self, **kwargs):
        name = kwargs.get("name")
        bankroll = kwargs.get("bankroll")
        if bankroll:
            self.bankroll = bankroll
            self.initial_bankroll = bankroll
        else:
            self.bankroll = DEFAULT_BANKROLL
            self.initial_bankroll = DEFAULT_BANKROLL
        if name:
            self.name = name
        else:
            self.name = f"Bot{random.randint(0, 999)}"

    def __str__(self):
        return self.name

    def stats(self):
        return (f"NAME: {self.name}\nBANKROLL: ${self.bankroll}\nINITIAL BANKROLL: ${self.initial_bankroll}"
                f"\nNET WINNINGS: ${self.bankroll - self.initial_bankroll}")

    # decide(self, decision_type, choices, **kwargs) provides the bot's decision based on multiple factors
    def decide(self, decision_type, choices, **kwargs):
        if decision_type == "hand_action":
            hands = kwargs.get("hands")
            deck = kwargs.get("deck")
            drawn_cards = deck.drawn
            current_hand = next((h for h in hands if h.open))
            dealer_showing = kwargs.get("dealer_show")

            # temp:
            return "S"
        elif decision_type == "bet_sizing":
            return MIN_BET
        elif decision_type == "insurance":
            return "y"



Blackjack(bots_playing=True, bots=[Bot()],rounds=100)