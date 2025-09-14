from entities.Card import Card

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def reset_hand(self):
        self.hand = []

    def add_card(self, card: Card):
        self.hand.append(card)

    def calculate_value(self):
        value = sum(card.value for card in self.hand)
        aces = sum(1 for card in self.hand if card.rank == "A")
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_busted(self):
        return self.calculate_value() > 21

    def show_hand_str(self, hide_first=False):
        if hide_first and len(self.hand) > 0:
            return "[Hidden], " + ", ".join(str(c) for c in self.hand[1:])
        return ", ".join(str(c) for c in self.hand)
