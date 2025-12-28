import tkinter as tk
from game.Game import Game
from GUI.DeckGUI import DeckGUI

class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("♠ Blackjack Game ♥")
        self.resizable(False, False)
        self.configure(bg="#1a5f1a")  # green felt background

        self.game = Game(num_slots=7)
        self.player_seat = None  # chosen seat index
        self._build_ui()

    def _build_ui(self):
        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Deck menu
        deck_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Deck", menu=deck_menu)
        deck_menu.add_command(label="View Deck", command=self.show_deck_window)

        # Main container
        main_frame = tk.Frame(self, bg="#1a5f1a", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        title = tk.Label(main_frame, text="♠ ♥ BLACKJACK ♣ ♦",
                        font=("Arial", 24, "bold"), bg="#1a5f1a", fg="gold")
        title.pack(pady=(0, 20))

        # Dealer section
        dealer_frame = tk.LabelFrame(main_frame, text="🎩 DEALER",
                                     font=("Arial", 14, "bold"), bg="#0d400d", fg="white",
                                     bd=3, relief="raised", padx=15, pady=15)
        dealer_frame.pack(fill="x", pady=(0, 30))

        self.dealer_cards_label = tk.Label(dealer_frame, text="Waiting for game to start...",
                                          font=("Courier", 12), bg="#0d400d", fg="white",
                                          wraplength=700, justify="center")
        self.dealer_cards_label.pack()

        self.dealer_value_label = tk.Label(dealer_frame, text="",
                                          font=("Arial", 14, "bold"), bg="#0d400d", fg="yellow")
        self.dealer_value_label.pack(pady=(5, 0))

        # Player section
        player_frame = tk.LabelFrame(main_frame, text="👤 YOUR HAND",
                                     font=("Arial", 14, "bold"), bg="#0d400d", fg="white",
                                     bd=3, relief="raised", padx=15, pady=15)
        player_frame.pack(fill="x", pady=(0, 20))

        self.player_cards_label = tk.Label(player_frame, text="Choose a seat to start playing",
                                          font=("Courier", 12), bg="#0d400d", fg="white",
                                          wraplength=700, justify="center")
        self.player_cards_label.pack()

        self.player_value_label = tk.Label(player_frame, text="",
                                          font=("Arial", 14, "bold"), bg="#0d400d", fg="yellow")
        self.player_value_label.pack(pady=(5, 0))

        # Seat selection
        seat_frame = tk.LabelFrame(main_frame, text="🪑 Choose Your Seat",
                                  font=("Arial", 12, "bold"), bg="#1a5f1a", fg="white",
                                  bd=2, relief="groove", padx=10, pady=10)
        seat_frame.pack(fill="x", pady=(0, 20))

        seats_container = tk.Frame(seat_frame, bg="#1a5f1a")
        seats_container.pack()

        self.seat_buttons = []
        for i in range(7):
            btn = tk.Button(seats_container, text=f"Seat {i+1}",
                          font=("Arial", 11, "bold"), width=10, height=2,
                          bg="#555555", fg="white", activebackground="#777777",
                          command=lambda idx=i: self.choose_seat(idx),
                          relief="raised", bd=3)
            btn.grid(row=0, column=i, padx=5)
            self.seat_buttons.append(btn)

        # Status bar
        self.status = tk.Label(main_frame, text="Welcome! Please choose a seat to begin.",
                              font=("Arial", 11), bg="#333333", fg="#00ff00",
                              relief="sunken", bd=2, padx=10, pady=8)
        self.status.pack(fill="x", pady=(0, 15))

        # Controls
        controls = tk.Frame(main_frame, bg="#1a5f1a")
        controls.pack()

        button_style = {
            "font": ("Arial", 12, "bold"),
            "width": 12,
            "height": 2,
            "bd": 3,
            "relief": "raised"
        }

        self.hit_button = tk.Button(controls, text="🃏 HIT", command=self.on_hit,
                                   state="disabled", bg="#4CAF50", fg="white",
                                   activebackground="#45a049", **button_style)
        self.hit_button.grid(row=0, column=0, padx=10)

        self.stand_button = tk.Button(controls, text="✋ STAND", command=self.on_stand,
                                     state="disabled", bg="#f44336", fg="white",
                                     activebackground="#da190b", **button_style)
        self.stand_button.grid(row=0, column=1, padx=10)

        self.double_button = tk.Button(controls, text="💰 DOUBLE", command=self.on_double,
                                      state="disabled", bg="#FF9800", fg="white",
                                      activebackground="#F57C00", **button_style)
        self.double_button.grid(row=0, column=2, padx=10)

        self.split_button = tk.Button(controls, text="✂️ SPLIT", command=self.on_split,
                                     state="disabled", bg="#9C27B0", fg="white",
                                     activebackground="#7B1FA2", **button_style)
        self.split_button.grid(row=0, column=3, padx=10)

        self.newgame_button = tk.Button(controls, text="🔄 NEW ROUND", command=self.start_new_round,
                                       state="disabled", bg="#2196F3", fg="white",
                                       activebackground="#0b7dda", **button_style)
        self.newgame_button.grid(row=0, column=4, padx=10)

    def choose_seat(self, idx):
        if self.player_seat is None:
            if self.game.sit_down(idx, "You"):
                self.player_seat = idx
                # Update seat button to show it's taken
                self.seat_buttons[idx].config(bg="#FFD700", fg="black", text=f"Seat {idx+1}\n(YOU)",
                                             state="disabled")
                # Disable all other seat buttons
                for i, btn in enumerate(self.seat_buttons):
                    if i != idx:
                        btn.config(state="disabled")

                self.status.config(text=f"✓ You're seated at Seat {idx+1}. Click 'NEW ROUND' to start playing!",
                                  fg="#00ff00")
                self.newgame_button.config(state="normal")

    def start_new_round(self):
        message = self.game.new_round()

        # If dealer or player has blackjack, show all cards immediately
        if self.game.dealer_has_blackjack or self.game.player_has_blackjack:
            self.update_ui(hide_dealer=False)
        else:
            self.update_ui(hide_dealer=True)

        self.hit_button.config(state="normal")
        self.stand_button.config(state="normal")
        self.double_button.config(state="normal")
        self.split_button.config(state="normal")
        #self.newgame_button.config(state="disabled")

        # Check if split is actually available
        if self.player_seat is not None:
            player = self.game.slots[self.player_seat]
            if player and not player.can_split():
                self.split_button.config(state="disabled")

        if message:
            # Determine color and icon based on outcome
            if "win" in message.lower() and "blackjack" in message.lower():
                color = "#FFD700"  # gold for blackjack win
                icon = "🎉"
            elif "push" in message.lower():
                color = "yellow"
                icon = "🤝"
            else:  # dealer blackjack
                color = "#ff6666"
                icon = "😔"

            self.status.config(text=f"{icon} {message}", fg=color)
            self.update_ui(hide_dealer=False)
            self.hit_button.config(state="disabled")
            self.stand_button.config(state="disabled")
            self.double_button.config(state="disabled")
            self.split_button.config(state="disabled")
            self.newgame_button.config(state="normal")
        else:
            self.status.config(text="🎮 Round started! Choose HIT, STAND, DOUBLE, or SPLIT.", fg="#00ff00")

    def on_hit(self):
        message = self.game.player_hit(self.player_seat)
        self.update_ui(hide_dealer=True)

        # After first hit, can't double or split anymore
        self.double_button.config(state="disabled")
        self.split_button.config(state="disabled")

        if message:
            # Check if it's a split hand transition message
            if "split hand" in message.lower() and "playing" in message.lower():
                self.status.config(text=f"🔄 {message}", fg="#FFD700")
                self.update_ui(hide_dealer=True)
                # Re-enable double if we can
                if self.player_seat is not None:
                    player = self.game.slots[self.player_seat]
                    if player and player.can_double():
                        self.double_button.config(state="normal")
            elif "double down complete" in message.lower():
                self.status.config(text=f"💰 {message}", fg="#FFD700")
                self.update_ui(hide_dealer=True)
            elif any(outcome in message.lower() for outcome in ["win", "lose", "push", "dealer"]):
                # This is a final result message (e.g., from dealer_play after second hand busts)
                self.update_ui(hide_dealer=False)

                # Determine color based on outcome
                if "blackjack" in message.lower() and "dealer" in message.lower():
                    color = "#ff6666"
                    icon = "😔"
                elif "win" in message.lower():
                    color = "#00ff00"
                    icon = "🎉"
                elif "lose" in message.lower() or ("busted" in message.lower() and "both" in message.lower()):
                    color = "#ff6666"
                    icon = "😔"
                else:
                    color = "yellow"
                    icon = "🤝"

                self.status.config(text=f"{icon} {message}", fg=color)
                self.hit_button.config(state="disabled")
                self.stand_button.config(state="disabled")
                self.newgame_button.config(state="normal")
            else:
                # Single hand bust
                self.status.config(text=f"💥 {message}", fg="#ff6666")
                self.update_ui(hide_dealer=False)
                self.hit_button.config(state="disabled")
                self.stand_button.config(state="disabled")
                self.newgame_button.config(state="normal")
        else:
            self.status.config(text="🃏 Card dealt! HIT again or STAND.", fg="#00ff00")

    def on_stand(self):
        message = self.game.player_stand(self.player_seat)
        self.update_ui(hide_dealer=False)

        # Disable double and split once we stand
        self.double_button.config(state="disabled")
        self.split_button.config(state="disabled")

        if message:
            # Check if it's a split hand transition message
            if "split hand" in message.lower() and "playing" in message.lower():
                self.status.config(text=f"🔄 {message}", fg="#FFD700")
                self.update_ui(hide_dealer=True)
                # Re-enable buttons for second hand
                self.hit_button.config(state="normal")
                self.stand_button.config(state="normal")
                if self.player_seat is not None:
                    player = self.game.slots[self.player_seat]
                    if player and player.can_double():
                        self.double_button.config(state="normal")
                return

            # Determine color based on outcome
            if "blackjack" in message.lower() and "dealer" in message.lower():
                color = "#ff6666"  # red for dealer blackjack
                icon = "😔"
            elif "win" in message.lower():
                color = "#00ff00"  # green
                icon = "🎉"
            elif "lose" in message.lower() or "busted" in message.lower():
                color = "#ff6666"  # red
                icon = "😔"
            else:
                color = "yellow"  # tie/push
                icon = "🤝"

            self.status.config(text=f"{icon} {message}", fg=color)
            self.hit_button.config(state="disabled")
            self.stand_button.config(state="disabled")
            self.newgame_button.config(state="normal")

    def on_double(self):
        """Handle double down action"""
        message = self.game.player_double(self.player_seat)

        # Disable all action buttons immediately
        self.double_button.config(state="disabled")
        self.split_button.config(state="disabled")

        if message:
            if "cannot" in message.lower():
                self.status.config(text=f"❌ {message}", fg="#ff6666")
            elif "split hand" in message.lower() and "playing" in message.lower():
                # Transitioning to second split hand
                self.update_ui(hide_dealer=True)
                self.status.config(text=f"💰 {message}", fg="#FFD700")
                # Re-enable buttons for second hand
                self.hit_button.config(state="normal")
                self.stand_button.config(state="normal")
                if self.player_seat is not None:
                    player = self.game.slots[self.player_seat]
                    if player and player.can_double():
                        self.double_button.config(state="normal")
            else:
                # Game over - dealer has played
                self.update_ui(hide_dealer=False)

                # Determine color based on outcome
                if "blackjack" in message.lower() and "dealer" in message.lower():
                    color = "#ff6666"
                    icon = "😔"
                elif "win" in message.lower():
                    color = "#00ff00"
                    icon = "🎉"
                elif "lose" in message.lower() or "busted" in message.lower():
                    color = "#ff6666"
                    icon = "😔"
                else:
                    color = "yellow"
                    icon = "🤝"

                self.status.config(text=f"{icon} {message}", fg=color)
                self.hit_button.config(state="disabled")
                self.stand_button.config(state="disabled")
                self.newgame_button.config(state="normal")
        else:
            self.status.config(text="💰 Doubled down! One card dealt, automatically standing...", fg="#FFD700")

    def on_split(self):
        """Handle split action"""
        message = self.game.player_split(self.player_seat)
        self.update_ui(hide_dealer=True)

        if message:
            if "cannot" in message.lower():
                self.status.config(text=f"❌ {message}", fg="#ff6666")
            else:
                self.status.config(text=f"✂️ {message}", fg="#FFD700")
                # Disable split button (can only split once)
                self.split_button.config(state="disabled")
                # Keep other buttons enabled for first hand
                if self.player_seat is not None:
                    player = self.game.slots[self.player_seat]
                    if player and not player.can_double():
                        self.double_button.config(state="disabled")

    def update_ui(self, hide_dealer=True):
        dealer = self.game.dealer

        # Update dealer display
        if hide_dealer:
            dealer_cards = dealer.show_hand_str(hide_first=True)
            self.dealer_cards_label.config(text=dealer_cards)
            self.dealer_value_label.config(text="Value: [Hidden]")
        else:
            dealer_cards = dealer.show_hand_str()
            dealer_score = dealer.best_value()
            self.dealer_cards_label.config(text=dealer_cards)

            if dealer.is_busted():
                self.dealer_value_label.config(text=f"Value: {dealer_score} (BUSTED!)", fg="#ff6666")
            elif dealer_score == 21:
                self.dealer_value_label.config(text=f"Value: {dealer_score} (BLACKJACK!)", fg="#FFD700")
            else:
                self.dealer_value_label.config(text=f"Value: {dealer_score}", fg="yellow")

        # Update player display
        if self.player_seat is not None:
            player = self.game.slots[self.player_seat]
            if player:
                # Check if player has split
                if player.split_hand is not None:
                    # Show both hands
                    hand1_str = ", ".join(str(c) for c in player.hand)
                    hand2_str = ", ".join(str(c) for c in player.split_hand)

                    # Calculate hand values
                    hand1_val = player.calculate_value()

                    split_total = sum(card.value for card in player.split_hand)
                    split_aces = sum(1 for c in player.split_hand if c.rank == "A")
                    split_values = {split_total}
                    for _ in range(split_aces):
                        split_total -= 10
                        split_values.add(split_total)
                    split_non_bust = [v for v in split_values if v <= 21]
                    hand2_val = max(split_non_bust) if split_non_bust else min(split_values)

                    # Highlight active hand
                    if player.active_hand == 0:
                        player_cards = f"▶ Hand 1: {hand1_str}\n  Hand 2: {hand2_str}"
                        value_text = f"Hand 1: {hand1_val} | Hand 2: {hand2_val}"
                    else:
                        player_cards = f"  Hand 1: {hand1_str}\n▶ Hand 2: {hand2_str}"
                        value_text = f"Hand 1: {hand1_val} | Hand 2: {hand2_val}"

                    self.player_cards_label.config(text=player_cards)
                    self.player_value_label.config(text=value_text, fg="yellow")
                else:
                    # Single hand display
                    player_cards = player.show_hand_str()
                    player_score = player.best_value()
                    self.player_cards_label.config(text=player_cards)

                    if player.is_busted():
                        self.player_value_label.config(text=f"Value: {player_score} (BUSTED!)", fg="#ff6666")
                    elif player_score == 21 and len(player.hand) == 2:
                        self.player_value_label.config(text=f"Value: {player_score} (BLACKJACK!)", fg="#FFD700")
                    elif player_score == 21:
                        self.player_value_label.config(text=f"Value: {player_score}", fg="#00ff00")
                    else:
                        # Show all possible values
                        possible = player.possible_values()
                        if len(possible) > 1:
                            values_str = " or ".join(str(v) for v in possible)
                            self.player_value_label.config(text=f"Value: {values_str}", fg="yellow")
                        else:
                            self.player_value_label.config(text=f"Value: {player_score}", fg="yellow")

    def show_deck_window(self):
        """Open a new window to display all cards remaining in the deck"""
        DeckGUI(self, self.game.deck)
