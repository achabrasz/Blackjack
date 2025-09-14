import tkinter as tk
from game.Game import Game

class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack")
        self.resizable(False, False)

        self.game = Game()
        self._build_ui()
        self.start_new_round()

    def _build_ui(self):
        pad = 8
        dealer_frame = tk.LabelFrame(self, text="Dealer", padx=pad, pady=pad)
        dealer_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=pad, pady=pad)

        self.dealer_hand_label = tk.Label(dealer_frame, text="", font=("Helvetica", 12))
        self.dealer_hand_label.pack(anchor="w")

        self.dealer_value_label = tk.Label(dealer_frame, text="", font=("Helvetica", 10))
        self.dealer_value_label.pack(anchor="w")

        player_frame = tk.LabelFrame(self, text="Player", padx=pad, pady=pad)
        player_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=pad, pady=0)

        self.player_hand_label = tk.Label(player_frame, text="", font=("Helvetica", 12))
        self.player_hand_label.pack(anchor="w")

        self.player_value_label = tk.Label(player_frame, text="", font=("Helvetica", 10))
        self.player_value_label.pack(anchor="w")

        self.hit_button = tk.Button(self, text="Hit", width=12, command=self.on_hit)
        self.hit_button.grid(row=2, column=0, padx=pad, pady=pad)

        self.stand_button = tk.Button(self, text="Stand", width=12, command=self.on_stand)
        self.stand_button.grid(row=2, column=1, padx=pad, pady=pad)

        self.newgame_button = tk.Button(self, text="New Game", width=26, command=self.start_new_round)
        self.newgame_button.grid(row=3, column=0, columnspan=2, padx=pad, pady=(0, pad))

        self.status = tk.Label(self, text="", anchor="w")
        self.status.grid(row=4, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0, pad))

        self.bind("<Key-h>", lambda e: self.on_hit())
        self.bind("<Key-s>", lambda e: self.on_stand())

    def start_new_round(self):
        message = self.game.new_round()
        self._update_ui(hide_dealer=True)
        if message:
            self.status.config(text=message)
            self._update_ui(hide_dealer=False)

    def on_hit(self):
        message = self.game.player_hit()
        self._update_ui(hide_dealer=True)
        if message:
            self.status.config(text=message)
            self._update_ui(hide_dealer=False)

    def on_stand(self):
        message = self.game.player_stand()
        self._update_ui(hide_dealer=False)
        if message:
            self.status.config(text=message)

    def _update_ui(self, hide_dealer=True):
        dealer = self.game.dealer
        player = self.game.player

        self.dealer_hand_label.config(text=dealer.show_hand_str(hide_first=hide_dealer))
        self.dealer_value_label.config(
            text=f"Value: {dealer.calculate_value()}" if not hide_dealer else "Value: [Hidden]"
        )

        self.player_hand_label.config(text=player.show_hand_str())
        self.player_value_label.config(text=f"Value: {player.calculate_value()}")

        if not self.game.in_round:
            self.hit_button.config(state="disabled")
            self.stand_button.config(state="disabled")
        else:
            self.hit_button.config(state="normal")
            self.stand_button.config(state="normal")
