from entities.Deck import Deck
from entities.Player import Player

class Game:
    def __init__(self, num_slots=7):
        self.deck = Deck(num_decks=5)
        self.dealer = Player("Dealer")
        self.slots = [None] * num_slots  # seats around the table
        self.in_round = False
        self.dealer_has_blackjack = False
        self.player_has_blackjack = False

    def sit_down(self, seat_index, name="You"):
        """Put a player into a seat if it is empty."""
        if self.slots[seat_index] is None:
            self.slots[seat_index] = Player(name)
            return True
        return False

    def new_round(self):
        self.dealer.reset_hand()
        self.dealer_has_blackjack = False
        self.player_has_blackjack = False
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
        """Check only for player blackjack at the start of the round.
        Dealer blackjack is checked only after player finishes their turn."""
        for player in self.slots:
            if not player:
                continue
            pval = player.calculate_value()
            # Only check if player has blackjack, not dealer
            if pval == 21:
                self.in_round = False
                self.player_has_blackjack = True
                # Check dealer blackjack only if player also has it
                dval = self.dealer.calculate_value()
                if dval == 21:
                    self.dealer_has_blackjack = True
                    return "Push: both have Blackjack!"
                return "Blackjack! You win!"
        return None

    def player_hit(self, seat_index):
        player = self.slots[seat_index]
        if not self.in_round or not player:
            return None

        # Add card to current active hand
        current_hand = player.get_current_hand()
        current_hand.append(self.deck.deal_card())

        if player.is_current_hand_busted():
            # If split hand exists and we're on first hand, move to second hand
            if player.split_hand is not None and player.active_hand == 0:
                player.active_hand = 1
                return "First hand busted! Playing split hand now."
            elif player.split_hand is not None and player.active_hand == 1:
                # Second split hand busted, but first hand might still win
                player.finished = True
                return self.dealer_play(seat_index)
            else:
                # Single hand busted
                player.finished = True
                self.in_round = False
                return "You busted! Dealer wins."

        # If doubled, automatically stand after one card
        if player.doubled:
            if player.split_hand is not None and player.active_hand == 0:
                player.active_hand = 1
                player.doubled = False  # Reset doubled flag for second hand
                return "Double down complete! Playing split hand now."
            else:
                player.finished = True
                return self.dealer_play(seat_index)

        return None

    def player_double(self, seat_index):
        """Double down: double bet, get one card, automatically stand"""
        player = self.slots[seat_index]
        if not self.in_round or not player:
            return None

        if not player.can_double():
            return "Cannot double! You need exactly 2 cards."

        player.doubled = True
        # Deal one card and automatically stand
        return self.player_hit(seat_index)

    def player_split(self, seat_index):
        """Split a pair into two separate hands"""
        player = self.slots[seat_index]
        if not self.in_round or not player:
            return None

        if not player.can_split():
            return "Cannot split! You need two cards of the same value."

        # Split the hand
        player.split_hand = [player.hand.pop()]

        # Deal one card to each hand
        player.hand.append(self.deck.deal_card())
        player.split_hand.append(self.deck.deal_card())

        return "Hand split! Playing first hand."

    def player_stand(self, seat_index):
        if not self.in_round or not self.slots[seat_index]:
            return None

        player = self.slots[seat_index]

        # If we have a split hand and we're on the first hand, move to second hand
        if player.split_hand is not None and player.active_hand == 0:
            player.active_hand = 1
            return "First hand complete! Playing split hand now."

        player.finished = True
        return self.dealer_play(seat_index)

    def dealer_play(self, seat_index):
        """Dealer plays after player stands. Check for dealer blackjack first."""
        player = self.slots[seat_index]
        dval = self.dealer.calculate_value()
        pval = player.calculate_value()

        # Check if dealer has blackjack (21 with 2 cards)
        if dval == 21 and len(self.dealer.hand) == 2:
            self.dealer_has_blackjack = True
            self.in_round = False
            return "Dealer has Blackjack. You lose."

        # Dealer draws cards until reaching 17 or more
        while self.dealer.calculate_value() < 17:
            self.dealer.add_card(self.deck.deal_card())

        if self.dealer.is_busted():
            self.in_round = False
            # Check split hand
            if player.split_hand is not None:
                return "Dealer busted! You win both hands!"
            return "Dealer busted! You win!"

        dval = self.dealer.calculate_value()
        self.in_round = False

        # Handle split hands
        if player.split_hand is not None:
            pval1 = player.calculate_value()

            # Calculate split hand value
            split_total = sum(card.value for card in player.split_hand)
            split_aces = sum(1 for c in player.split_hand if c.rank == "A")
            split_values = {split_total}
            for _ in range(split_aces):
                split_total -= 10
                split_values.add(split_total)
            split_non_bust = [v for v in split_values if v <= 21]
            pval2 = max(split_non_bust) if split_non_bust else min(split_values)

            # Check if split hand is busted
            hand1_busted = player.is_busted()
            hand2_busted = all(v > 21 for v in split_values)

            if hand1_busted and hand2_busted:
                return "Both hands busted! Dealer wins."
            elif hand1_busted:
                if dval > pval2:
                    return "Hand 1 busted, Hand 2 lost. Dealer wins both."
                elif dval < pval2:
                    return "Hand 1 busted, Hand 2 won! Push overall."
                else:
                    return "Hand 1 busted, Hand 2 push."
            elif hand2_busted:
                if dval > pval1:
                    return "Hand 2 busted, Hand 1 lost. Dealer wins both."
                elif dval < pval1:
                    return "Hand 2 busted, Hand 1 won! Push overall."
                else:
                    return "Hand 2 busted, Hand 1 push."
            else:
                # Neither hand busted
                wins = 0
                if pval1 > dval:
                    wins += 1
                elif pval1 < dval:
                    wins -= 1

                if pval2 > dval:
                    wins += 1
                elif pval2 < dval:
                    wins -= 1

                if wins == 2:
                    return "You win both hands!"
                elif wins == 1:
                    return "You win one hand, push on the other!"
                elif wins == 0:
                    return "Both hands push!"
                elif wins == -1:
                    return "You lose one hand, push on the other!"
                else:
                    return "Dealer wins both hands."

        # Single hand logic
        if dval > pval:
            return "Dealer wins."
        elif dval < pval:
            return "You win!"
        else:
            return "Push: it's a tie."
