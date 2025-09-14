from entities.Deck import Deck
from entities.Player import Player

class Game:
    def __init__(self):
        self.deck = Deck(num_decks=1)
        self.player = Player("You")
        self.dealer = Player("Dealer")
        self.in_round = False

    def new_round(self):
        self.player.reset_hand()
        self.dealer.reset_hand()
        self.in_round = True

        if len(self.deck) < 15:
            self.deck.build()

        for _ in range(2):
            self.player.add_card(self.deck.deal_card())
            self.dealer.add_card(self.deck.deal_card())

        return self.check_blackjack()

    def check_blackjack(self):
        pval, dval = self.player.calculate_value(), self.dealer.calculate_value()
        if pval == 21 and dval == 21:
            self.in_round = False
            return "Push: both have Blackjack!"
        elif pval == 21:
            self.in_round = False
            return "Blackjack! You win!"
        elif dval == 21:
            self.in_round = False
            return "Dealer has Blackjack. You lose."
        return None

    def player_hit(self):
        if not self.in_round:
            return None
        self.player.add_card(self.deck.deal_card())
        if self.player.is_busted():
            self.in_round = False
            return "You busted! Dealer wins."
        return None

    def player_stand(self):
        if not self.in_round:
            return None
        return self.dealer_play()

    def dealer_play(self):
        while self.dealer.calculate_value() < 17:
            self.dealer.add_card(self.deck.deal_card())

        if self.dealer.is_busted():
            self.in_round = False
            return "Dealer busted! You win!"

        pval, dval = self.player.calculate_value(), self.dealer.calculate_value()
        self.in_round = False
        if dval > pval:
            return "Dealer wins."
        elif dval < pval:
            return "You win!"
        else:
            return "Push: it's a tie."
