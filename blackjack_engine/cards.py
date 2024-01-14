import random
import math
import warnings

ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
suits = ["h", "d", "s", "c"]


class Card:
    def __init__(self, **cardinfo):
        if "rank" in cardinfo and cardinfo.get("rank") in ranks:
            self.rank = cardinfo.get("rank")
        else:
            self.rank = random.choice(ranks)

        if "suit" in cardinfo and cardinfo.get("suit") in suits:
            self.suit = cardinfo.get("suit")
        else:
            self.suit = random.choice(suits)

        if self.suit == "h":
            self.suit_name = "Hearts"
            self.suit_icon = "♥"
        elif self.suit == "d":
            self.suit_name = "Diamonds"
            self.suit_icon = "♦"
        elif self.suit == "s":
            self.suit_name = "Spades"
            self.suit_icon = "♠"
        else:
            self.suit_name = "Clubs"
            self.suit_icon = "♣"

        if self.rank == "A":
            self.rank_name = "Ace"
        elif self.rank == "J":
            self.rank_name = "Jack"
        elif self.rank == "Q":
            self.rank_name = "Queen"
        elif self.rank == "K":
            self.rank_name = "King"
        else:
            self.rank_name = self.rank

        self.prim_display_str = f"{self.rank_name} of {self.suit_name}"
        self.sec_display_str = f"{self.rank}{self.suit_icon}"

    def __str__(self):
        return self.sec_display_str

    def rank_val(self):
        if self.rank.isnumeric():
            return int(self.rank)
        elif self.rank == "A":
            return 1
        elif self.rank == "J":
            return 11
        elif self.rank == "Q":
            return 12
        else:
            return 13


class Deck:
    def __init__(self, size=1, shuffled=True, **kwargs):  # size: amount of decks (only if cards not specified)
        cards = kwargs.get('cards')
        self.drawn = []
        if cards or cards == []:
            self.cards = cards
        else:
            self.cards = []
            for i in range(size):
                for s in suits:
                    for r in ranks:
                        self.cards.append(Card(suit=s, rank=r))
            if shuffled:
                self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return " ".join(map(lambda card : card.sec_display_str, self.cards))

    def draw(self):
        if self.cards:
            drawn_card = self.cards.pop(0)
            self.drawn.append(drawn_card)
            return drawn_card
        else:
            return False

    def add(self, card):
        if isinstance(card, Card):
            self.cards.append(card)
        else:
            warnings.warn("Attempted to add non-card to Deck")

    def empty(self):
        self.cards = []













