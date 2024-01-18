import random
from cards import Deck, Card

DEFAULT_BANKROLL = 1000
BLACKJACK_PAYS = 3/2 # (e.g. 3/2 i.e. 3/2)
MIN_BET = 10
MAX_BET = 100000000000
DECKS_AMOUNT = 6
CARDS_BEFORE_SHUFFLING = 0.5 # (e.g 0.5 or 50%)
INSURANCE = True
STAND_SOFT_17 = True
MAX_SPLIT = 4 # How many hands made by splitting max
RE_SPLIT_ACE = False
HIT_AFTER_SPLIT_ACE = False
DOUBLE_AFTER_SPLIT = True
SURRENDER = True


def blackjack_rank(rank_val):
    if rank_val > 10:
        return 10
    else:
        return rank_val


def blackjack_sum(cards):
    bj_sum = {
        "sum": 0,
        "soft": False
    }
    for c in cards:
        v = blackjack_rank(c.rank_val())
        if not bj_sum["soft"]:
            if v == 1:
                if bj_sum["sum"] + 11 > 21:
                    bj_sum["sum"] += 1
                else:
                    bj_sum["sum"] += 11
                    bj_sum["soft"] = True
            else:
                bj_sum["sum"] += v
        else:
            if v == 1:
                bj_sum["sum"] += 1
            elif bj_sum["sum"] + v > 21:
                bj_sum["sum"] = bj_sum["sum"] + v - 10
                bj_sum["soft"] = False
            else:
                bj_sum["sum"] = bj_sum["sum"] + v
    return bj_sum


class Player:
    def __init__(self, **kwargs):
        name = kwargs.get("name")
        bankroll = kwargs.get("bankroll")
        if bankroll:
            self.bankroll = bankroll
        else:
            self.bankroll = DEFAULT_BANKROLL
        if name:
            self.name = name
        else:
            self.name = f"Player{random.randint(0,999)}"

    def __str__(self):
        return self.name


class Hand:
    def __init__(self, cards, player, bet, deck):
        self.player = player
        self.bet = bet
        self.player.bankroll -= self.bet
        self.deck = deck
        if cards:
            self.cards = cards
        else:
            self.cards = []
        self.sum = blackjack_sum(self.cards)
        self.open = True
        self.can_hit = True
        self.has_split = False
        self.can_split = False
        self.can_double = False
        self.can_surrender = False
        self.refresh()

    def __str__(self):
        return (" ".join(map(lambda card: card.sec_display_str, self.cards)) + f" ({self.sum["sum"]}"
                + (", Soft)" if (self.sum["soft"] and self.sum["sum"] != 21) else ")"))

    def refresh(self):
        self.sum = blackjack_sum(self.cards)
        if self.sum["sum"] >= 21:
            self.open = False
            return
        if not HIT_AFTER_SPLIT_ACE and self.has_split and self.cards[0].rank_val() == 1:
            self.can_hit = False
        else:
            self.can_hit = True
        if len(self.cards) == 2:
            if not DOUBLE_AFTER_SPLIT and self.has_split:
                self.can_double = False
            else:
                if self.player.bankroll >= self.bet:
                    self.can_double = True
                else:
                    self.can_double = False
            if SURRENDER and not self.has_split:
                self.can_surrender = True
            else:
                self.can_surrender = False
            if (self.player.bankroll >= self.bet and blackjack_rank(self.cards[0].rank_val())
                    == blackjack_rank(self.cards[1].rank_val())):
                if not RE_SPLIT_ACE and self.cards[0].rank_val() == 1 and self.has_split:
                    self.can_split = False
                else:
                    self.can_split = True
            else:
                self.can_split = False
        else:
            self.can_split = False
            self.can_double = False
            self.can_surrender = False

    def hit(self, card):
        self.cards.append(card)
        self.refresh()

    def stand(self):
        self.open = False
        self.refresh()

    def double(self, card):
        self.cards.append(card)
        self.open = False
        self.player.bankroll -= self.bet
        self.bet *= 2
        self.refresh()

    def split(self):
        new_hand = Hand([self.cards.pop()], self.player, self.bet, self.deck, self.index+1)
        self.hit(self.deck.draw())
        self.has_split = True
        new_hand.has_split = True
        if self.cards[0].rank_val() == 1:
            self.open = False
            new_hand.open = False
        new_hand.hit(self.deck.draw())
        self.refresh()
        return new_hand

    # def remove_last(self):
    #     self.cards.pop()
    #     self.sum = blackjack_sum(self.cards)
    #     if (len(self.cards) == 2 and
    #         blackjack_rank(self.cards[0].rank_val()) == blackjack_rank(self.cards[1].rank_val())):
    #         self.splittable = True


def run_player_round(deck, plr, dealer_show, bet, ini_hand, bots_playing=False):
    plr_hands = [ini_hand]
    if ini_hand.sum["sum"] == 21:
        print(f"{plr}, you were dealt:\n{ini_hand}, Blackjack")
    else:
        print(f"{plr}, you were dealt:\n{ini_hand}")
        while True:
            hand = next((h for h in plr_hands if h.open), None)
            if not hand:
                break
            ind = plr_hands.index(hand)
            print("-------------------------")
            print(f"Dealer: {dealer_show} ??")
            print(f"Bankroll: ${plr.bankroll}")
            if len(plr_hands) > 1:
                print(f"Hands: {", ".join(f"Hand {plr_hands.index(h) + 1}: " + h.__str__() for h in plr_hands)}")
            print((f"Current Hand (Hand {ind + 1}):\n" if len(plr_hands) > 1 else
                   "Hand:\n") + f"{hand}")
            can_hit = hand.can_hit
            can_double = hand.can_double
            can_surrender = hand.can_surrender
            can_split = hand.can_split and len(plr_hands) < MAX_SPLIT
            if not bots_playing:
                action = input("Action? (S)tand" +
                               (" (H)it" if can_hit else "") +
                               (" (D)ouble" if can_double else "") +
                               (" (Su)rrender" if can_surrender else "") +
                               (" (Sp)lit" if can_split else "") + "\n")
            else:
                bot_choices = ["S"]
                if can_hit:
                    bot_choices.append("H")
                if can_double:
                    bot_choices.append("D")
                if can_surrender:
                    bot_choices.append("Su")
                if can_split:
                    bot_choices.append("Sp")
                action = plr.decide("hand_action", bot_choices, hands=plr_hands, deck=deck)
            if action == "S":
                print(f"{plr} stands" + (f" Hand {ind + 1}" if len(plr_hands) > 1 else "")
                      + f" with {hand.sum["sum"]}")
                hand.stand()
            elif action == "H" and hand.can_hit:
                new_card = deck.draw()
                print(f"{plr} hits" + (f" Hand {ind + 1}" if len(plr_hands) > 1 else "")
                + f", receives {new_card}")
                hand.hit(new_card)
                print(f"\nNew Hand: {hand}" +
                      (f", Bust" if hand.sum["sum"] > 21 else ""))
            elif action == "D" and hand.can_double:
                new_card = deck.draw()
                print(f"{plr} doubles down " +
                      (f"on Hand {hand.index} " if len(plr_hands) > 1 else "") +
                      f"for additional ${hand.bet}, receives {new_card}")
                hand.double(new_card)
                print(f"\nNew Hand: {hand}" +
                      (f", Bust" if hand.sum["sum"] > 21 else ""))
            elif action == "Su" and hand.can_surrender:
                print(f"{plr} surrenders. Return: ${bet / 2}")
                plr.bankroll += bet / 2
                plr_hands = []
            elif action == "Sp" and hand.can_split and len(plr_hands) < MAX_SPLIT:
                print(f"{plr} splits the hand.")
                new_hand = hand.split()
                plr_hands.append(new_hand)
                print(f"Hand {ind + 1}: {hand}, Hand {plr_hands.index(new_hand) + 1}: {new_hand}")
            else:
                print("Invalid action")
        # turn over
        if plr_hands:
            print(f"{plr}'s turn is over. Hands summary:")
        else:
            print(f"{plr}'s turn is over, Surrendered.")
        print(", ".join(h.__str__() for h in plr_hands))
        return plr_hands


def show_cards(cards):
    card_sum = blackjack_sum(cards)
    return (" ".join(map(lambda card: card.sec_display_str, cards)) + (f" ({card_sum["sum"]}"
    + (", Soft)" if card_sum["soft"] and card_sum["sum"] != 21 else ")")))


def get_splitter_deck(rank):
    deck = Deck(cards=[])
    print(deck)
    for i in range(52*6):
        deck.cards.append(Card(rank=rank))
    return deck


class Blackjack:
    def __init__(self, bots_playing=False, bots=None, rounds=None):
        self.rounds_played = 0
        if bots is None:
            bots = []
        print("Table has opened!")
        if not bots_playing:
            print(bots_playing)
            plrs = []
            first_plr_name = input("Enter first player's name:\n")
            plrs.append(Player(name=first_plr_name))
            if input("Add another player? (y/n)\n") == "y":
                while True:
                    next_plr_name = input("Enter next player's name:\n")
                    plrs.append(Player(name=next_plr_name))
                    if input("Add another player? (y/n)\n") == "y":
                        continue
                    else:
                        break
        else:
            plrs = bots
        print("Dealer has arrived. Deck is shuffled, table is open for play.")
        deck = Deck(size=DECKS_AMOUNT)
        # deck = get_splitter_deck("A")
        while True:
            if rounds and self.rounds_played >= rounds:
                print("Rounds are over, stats:")
                if bots_playing:
                    for bot in bots:
                        print(bot.stats)
            rounds += 1
            if not bots_playing:
                choice = input("Play next round? (y/n):\n")
                if choice != "y":
                    print("\nTable closed, goodbye")
                    break
            print("\n\n---------- NEW ROUND ----------\n\n")
            if len(deck.cards) < DECKS_AMOUNT * 52 * CARDS_BEFORE_SHUFFLING:
                print("**Cut card reached last round, deck reshuffled**")
                deck = Deck(size=DECKS_AMOUNT)
            dealer_hand = [deck.draw(), deck.draw()]
            bets = []
            insured = []
            blackjacks = []
            hands = []
            results = []
            for plr in plrs:
                if (not bots_playing) and plr.bankroll < MIN_BET:
                    print(f"{plr} does not have sufficient bankroll. They will be sitting out from now on.")
                    plrs.remove(plr)
                    continue
                print(f"{plr}'s turn to place bet. Bankroll: ${plr.bankroll}.")
                if not bots_playing:
                    bet = input(f"Place your bet (Min: ${MIN_BET}, Max: ${MAX_BET}\n$")
                    # set bet to bot decision
                    if bet.replace(".","").isnumeric():
                        bet = float(bet)
                        if MIN_BET <= bet <= MAX_BET and plr.bankroll >= bet:
                            bets.append((plr, bet))
                        else:
                            print("Invalid bet sizing, turn skipped.")
                            continue
                    else:
                        print("Invalid bet, turn skipped.")
                        continue
                else:
                    bet = plr.decide("bet_sizing", None)
            if not plrs:
                print("All players have insufficient bankrolls. Table closed.")
                break
            if not bets:
                print("No players this round.")
                continue
            print(f"Dealer is showing {dealer_hand[0]}")

            if INSURANCE and dealer_hand[0].rank_val() == 1:
                # Insurance
                print(f"Dealer is showing an Ace, Insurance is open.")
                for bet in bets:
                    plr = bet[0]
                    plr_bet = bet[1]
                    if not bots_playing:
                        insurance_choice = input(f"{plr}, take insurance (${plr_bet/2})? (y/n)\n")
                    else:
                        insurance_choice = plr.decide("insurance", ["y","n"], deck=deck)
                    if insurance_choice == "y":
                        print(f"{plr} has taken insurance for ${plr_bet/2}.")
                        plr.bankroll -= plr_bet/2
                        insured.append((plr, plr_bet/2))
                    else:
                        print(f"Insurance not taken.")

            for bet in bets:
                plr = bet[0]
                plr_bet = bet[1]
                plr_hand = Hand(cards=[deck.draw(),deck.draw()], player=plr,deck=deck,bet=plr_bet)
                hands.append((plr,plr_hand,plr_bet))
                if blackjack_sum(plr_hand.cards) == 21:
                    # Player Blackjack
                    blackjacks.append((plr, plr_bet))

            print("Player hands:")
            print(", ".join(f"{h[0]}: " + h[1].__str__() for h in hands))

            if blackjack_sum(dealer_hand) == 21:
                print(f"Dealer has blackjack: {show_cards(dealer_hand)}")
                if blackjacks:
                    print(f"Some players had blackjack.")
                    print(f"The following players Push:\n{", ".join(bj[0].__str__() for bj in blackjacks)}")
                    for bj in blackjacks:
                        plr = bj[0]
                        plr_bet = bj[1]
                        plr.bankroll += plr_bet
                if insured:
                    for i in insured:
                        plr = i[0]
                        val = i[1]
                        plr.bankroll += val + val * 2  # Insurance pays 2:1
                    print("Some players had taken insurance, payouts:")
                    print("\n".join(f"{i[0]}:\n  PAYOUT: ${i[1] + i[1] * 2}\n  NET WINNINGS: $0" for i in insured))
                    print("All other players lose their bets.")
                elif dealer_hand[0].rank_val() == 1 and INSURANCE:
                    print("No players had taken insurance, all players lose their bets.")
                else:
                    print("All players lose their bets.")
                print("ROUND OVER.")
                continue
            elif dealer_hand[0].rank_val() == 1 or blackjack_rank(dealer_hand[0].rank_val()) == 10:
                print("**Dealer did not have blackjack**")

            for hand in hands:
                plr = hand[0]
                plr_ini_hand = hand[1]
                plr_bet = hand[2]
                print("\n--------------\n")
                print(f"{plr}'s turn.")
                # bet = input(f"Place your bet (Min: ${MIN_BET}, Max: ${MAX_BET}\n$")
                # if bet.replace(".","").isnumeric():
                #     bet = float(bet)
                #     if bet < MIN_BET or bet > MAX_BET:
                #         print("Invalid bet sizing, turn skipped.")
                #         continue
                # else:
                #     print("Invalid bet, turn skipped.")
                #     continue

                plr_hands = run_player_round(deck, plr, dealer_hand[0], plr_bet, plr_ini_hand, bots_playing=bots_playing)
                results.append((plr, plr_hands))
            print("\n----------\nAll players' turns over. Dealer's turn.")
            print(f"Dealer reveals {dealer_hand[1]}")
            print(f"Dealer has {show_cards(dealer_hand)}")
            while True:
                dealer_sum = blackjack_sum(dealer_hand)
                if dealer_sum["sum"] < 17 or ((not STAND_SOFT_17) and dealer_sum["soft"]
                                              and dealer_sum["sum"] < 18):
                    new_card = deck.draw()
                    print(f"Dealer hits, receives {new_card}")
                    dealer_hand.append(new_card)
                    print(f"Dealer now has {show_cards(dealer_hand)}")
                elif dealer_sum["sum"] < 21:
                    print(f"Dealer stands with {show_cards(dealer_hand)}")
                    break
                elif dealer_sum["sum"] == 21:
                    print("Dealer has 21")
                    break
                else:
                    print("Dealer busts")
                    break
            print("\n ROUND OVER, RESULTS:")
            for result in results:
                plr = result[0]
                dealer_sum = blackjack_sum(dealer_hand)
                payout = 0
                net = 0
                for plr_hand in result[1]:
                    if plr_hand.sum["sum"] > 21:
                        net -= plr_hand.bet
                        # Player Bust
                    elif dealer_sum["sum"] > 21:
                        payout += plr_hand.bet * 2
                        net += plr_hand.bet
                        # Dealer Bust
                    elif plr_hand.sum["sum"] == 21 and len(plr_hand.cards) == 2:
                        payout += plr_hand.bet + plr_hand.bet * BLACKJACK_PAYS
                        net += plr_hand.bet * BLACKJACK_PAYS
                        # Player Blackjack
                    elif plr_hand.sum["sum"] > dealer_sum["sum"]:
                        payout += plr_hand.bet * 2
                        net += plr_hand.bet
                        # Player Win
                    elif plr_hand.sum["sum"] == dealer_sum["sum"]:
                        payout += plr_hand.bet
                        # Push
                    elif plr_hand.sum["sum"] < dealer_sum["sum"]:
                        net -= plr_hand.bet
                        # Player Loss
                result[0].bankroll += payout
                print("---------")
                print(f"{result[0]}:\n  PAYOUT: ${payout}\n"
                      f"  NET WINNINGS: ${net}\n  HANDS:{", ".join(h.__str__() for h in result[1])}")
            print("\n--- END OF RESULTS\n")














