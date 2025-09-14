from entities.Card import Card

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.finished = False  # whether the player is done (stood or busted)

    def reset_hand(self):
        self.hand = []
        self.finished = False

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
