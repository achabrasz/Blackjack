import tkinter as tk


class DeckGUI(tk.Toplevel):
    """A window to display all cards remaining in the deck"""

    def __init__(self, parent, deck):
        super().__init__(parent)
        self.deck = deck
        self.title("🃏 Deck Viewer")
        self.geometry("600x500")
        self.configure(bg="#2c2c2c")

        self._build_ui()

    def _build_ui(self):
        """Build the deck viewer UI"""
        # Title
        title = tk.Label(self, text="Cards Remaining in Deck",
                        font=("Arial", 18, "bold"), bg="#2c2c2c", fg="gold")
        title.pack(pady=10)

        # Card count
        card_count = len(self.deck.cards)
        count_label = tk.Label(self, text=f"Total Cards: {card_count}",
                              font=("Arial", 14, "bold"), bg="#2c2c2c", fg="#00ff00")
        count_label.pack(pady=5)

        # Container frame for cards list
        cards_container = tk.Frame(self, bg="#2c2c2c")
        cards_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable frame for cards
        canvas = tk.Canvas(cards_container, bg="#2c2c2c", highlightthickness=0)
        scrollbar = tk.Scrollbar(cards_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c2c2c")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display cards organized by suit
        suits = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
        suit_colors = {"Hearts": "#ff6666", "Diamonds": "#ff6666", "Clubs": "white", "Spades": "white"}

        # Group cards by suit
        cards_by_suit = {suit: [] for suit in suits.keys()}
        for card in self.deck.cards:
            cards_by_suit[card.suit].append(card)

        # Display each suit
        for suit, symbol in suits.items():
            if cards_by_suit[suit]:  # Only show suits that have cards
                # Suit header
                suit_frame = tk.LabelFrame(scrollable_frame, text=f"{symbol} {suit}",
                                          font=("Arial", 12, "bold"), bg="#1a1a1a",
                                          fg=suit_colors[suit], bd=2, relief="raised",
                                          padx=10, pady=5)
                suit_frame.pack(fill="x", padx=10, pady=5)

                # Cards in this suit
                cards_text = ", ".join(str(card) for card in sorted(cards_by_suit[suit],
                                                                    key=lambda c: ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"].index(c.rank)))
                cards_label = tk.Label(suit_frame, text=cards_text,
                                      font=("Courier", 11), bg="#1a1a1a",
                                      fg=suit_colors[suit], wraplength=550, justify="left")
                cards_label.pack(anchor="w")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Close button (below the cards list)
        close_btn = tk.Button(self, text="Close", command=self.destroy,
                            font=("Arial", 12, "bold"), bg="#f44336", fg="white",
                            activebackground="#da190b", width=15, height=2)
        close_btn.pack(pady=10)

