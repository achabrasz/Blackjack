from entities.Deck import Deck
from entities.Player import Player

class Game:
    def __init__(self, num_slots=7):
        self.deck = Deck(num_decks=1)
        self.dealer = Player("Dealer")
        self.slots = [None] * num_slots  # seats around the table
        self.in_round = False

    def sit_down(self, seat_index, name="You"):
        """Put a player into a seat if it is empty."""
        if self.slots[seat_index] is None:
            self.slots[seat_index] = Player(name)
            return True
        return False

    def new_round(self):
        self.dealer.reset_hand()
        for player in self.slots:
            if player:
                player.reset_hand()
        self.in_round = True

        if len(self.deck) < 15:
            self.deck.build()

        for _ in range(2):
            for player in self.slots:
                if player:
                    player.add_card(self.deck.deal_card())
            self.dealer.add_card(self.deck.deal_card())

        return self.check_blackjack()

    def check_blackjack(self):
        for player in self.slots:
            if not player:
                continue
            pval, dval = player.calculate_value(), self.dealer.calculate_value()
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

    def player_hit(self, seat_index):
        player = self.slots[seat_index]
        if not self.in_round or not player:
            return None
        player.add_card(self.deck.deal_card())
        if player.is_busted():
            player.finished = True
            self.in_round = False
            return "You busted! Dealer wins."
        return None

    def player_stand(self, seat_index):
        if not self.in_round or not self.slots[seat_index]:
            return None
        self.slots[seat_index].finished = True
        return self.dealer_play(seat_index)

    def dealer_play(self, seat_index):
        while self.dealer.calculate_value() < 17:
            self.dealer.add_card(self.deck.deal_card())

        if self.dealer.is_busted():
            self.in_round = False
            return "Dealer busted! You win!"

        pval = self.slots[seat_index].calculate_value()
        dval = self.dealer.calculate_value()
        self.in_round = False
        if dval > pval:
            return "Dealer wins."
        elif dval < pval:
            return "You win!"
        else:
            return "Push: it's a tie."
