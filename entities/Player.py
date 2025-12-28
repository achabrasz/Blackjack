from entities.Card import Card

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.finished = False  # whether the player is done (stood or busted)
        self.split_hand = None  # second hand if player splits
        self.doubled = False  # whether player has doubled down
        self.active_hand = 0  # 0 for main hand, 1 for split hand

    def reset_hand(self):
        self.hand = []
        self.finished = False
        self.split_hand = None
        self.doubled = False
        self.active_hand = 0

    def add_card(self, card):
        self.hand.append(card)

    def possible_values(self):
        total = sum(card.value for card in self.hand)
        aces = sum(1 for c in self.hand if c.rank == "A")
        values = {total}
        for _ in range(aces):
            total -= 10
            values.add(total)
        # Filter busted values if at least one non-busted exists
        non_bust = [v for v in values if v <= 21]
        if non_bust:
            return sorted(non_bust)
        return sorted(values)  # if all busted, return the busted values

    def best_value(self):
        values = self.possible_values()
        under_or_equal = [v for v in values if v <= 21]
        return max(under_or_equal) if under_or_equal else min(values)

    def calculate_value(self):
        return self.best_value()

    def is_busted(self):
        return all(v > 21 for v in self.possible_values())

    def show_hand_str(self, hide_first=False):
        if hide_first and len(self.hand) > 0:
            return "[Hidden], " + ", ".join(str(c) for c in self.hand[1:])
        return ", ".join(str(c) for c in self.hand)

    def can_split(self):
        """Check if player can split (2 cards with same value)"""
        return (len(self.hand) == 2 and
                self.split_hand is None and
                self.hand[0].value == self.hand[1].value)

    def can_double(self):
        """Check if player can double down (exactly 2 cards in current hand)"""
        current_hand = self.get_current_hand()
        return len(current_hand) == 2 and not self.doubled

    def get_current_hand(self):
        """Get the currently active hand"""
        if self.active_hand == 1 and self.split_hand is not None:
            return self.split_hand
        return self.hand

    def get_current_value(self):
        """Get value of current active hand"""
        current = self.get_current_hand()
        total = sum(card.value for card in current)
        aces = sum(1 for c in current if c.rank == "A")
        values = {total}
        for _ in range(aces):
            total -= 10
            values.add(total)
        non_bust = [v for v in values if v <= 21]
        if non_bust:
            return max(non_bust)
        return min(values)

    def is_current_hand_busted(self):
        """Check if current active hand is busted"""
        current = self.get_current_hand()
        total = sum(card.value for card in current)
        aces = sum(1 for c in current if c.rank == "A")
        values = {total}
        for _ in range(aces):
            total -= 10
            values.add(total)
        return all(v > 21 for v in values)

