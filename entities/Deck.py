from entities.Card import Card
import random

class Deck:
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.build()

    def build(self):
        self.cards = [
            Card(suit, rank)
            for _ in range(self.num_decks)
            for suit in self.suits
            for rank in self.ranks
        ]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            self.build()  # reshuffle new deck automatically
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)
