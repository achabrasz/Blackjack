import tkinter as tk
from game.Game import Game

class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack Table")
        self.resizable(False, False)

        self.game = Game(num_slots=7)
        self.player_seat = None  # chosen seat index
        self._build_ui()

    def _build_ui(self):
        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.canvas.pack()

        # draw 7 seat circles
        self.seat_coords = []
        radius = 30
        self.player_texts = []  # holds card text per seat

        for i in range(7):
            x = 100 + i * 100
            y = 500
            seat = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                           fill="gray", tags=f"seat{i}")
            self.canvas.tag_bind(seat, "<Button-1>", lambda e, idx=i: self.choose_seat(idx))
            self.seat_coords.append((x, y))

            # card text placeholder for this seat
            text_id = self.canvas.create_text(x, y - 50, text="", fill="black", font=("Helvetica", 12))
            self.player_texts.append(text_id)

        # dealer label
        self.dealer_text = self.canvas.create_text(400, 100, text="Dealer", fill="black", font=("Helvetica", 16))
        self.dealer_hand_text = self.canvas.create_text(400, 150, text="", fill="black", font=("Helvetica", 12))

        # status bar
        self.status = tk.Label(self, text="", anchor="w", bg="black", fg="yellow", font=("Helvetica", 12))
        self.status.pack(fill="x")

        # controls
        controls = tk.Frame(self, bg="grey")
        controls.pack(pady=10)

        self.hit_button = tk.Button(controls, text="Hit", command=self.on_hit, state="disabled")
        self.hit_button.grid(row=0, column=0, padx=10)

        self.stand_button = tk.Button(controls, text="Stand", command=self.on_stand, state="disabled")
        self.stand_button.grid(row=0, column=1, padx=10)

        self.newgame_button = tk.Button(controls, text="New Round", command=self.start_new_round, state="disabled")
        self.newgame_button.grid(row=0, column=2, padx=10)

    def choose_seat(self, idx):
        if self.player_seat is None:
            if self.game.sit_down(idx, "You"):
                self.player_seat = idx
                self.canvas.itemconfig(f"seat{idx}", fill="blue")
                self.status.config(text=f"You sat down at seat {idx+1}")
                self.newgame_button.config(state="normal")

    def start_new_round(self):
        message = self.game.new_round()
        self.update_ui(hide_dealer=True)
        self.hit_button.config(state="normal")
        self.stand_button.config(state="normal")
        if message:
            self.status.config(text=message)
            self.update_ui(hide_dealer=False)

    def on_hit(self):
        message = self.game.player_hit(self.player_seat)
        self.update_ui(hide_dealer=True)
        if message:
            self.status.config(text=message)
            self.update_ui(hide_dealer=False)
            self.hit_button.config(state="disabled")
            self.stand_button.config(state="disabled")

    def on_stand(self):
        message = self.game.player_stand(self.player_seat)
        self.update_ui(hide_dealer=False)
        if message:
            self.status.config(text=message)
            self.hit_button.config(state="disabled")
            self.stand_button.config(state="disabled")

    def update_ui(self, hide_dealer=True):
        dealer = self.game.dealer

        if hide_dealer:
            self.canvas.itemconfig(
                self.dealer_hand_text,
                text=f"{dealer.show_hand_str(hide_first=True)} = [Hidden]"
            )
        else:
            dvals = dealer.possible_values()
            dealer_score = str(dealer.best_value()) if self.game.in_round else ", ".join(str(v) for v in dvals)
            self.canvas.itemconfig(
                self.dealer_hand_text,
                text=f"{dealer.show_hand_str()} = {dealer_score}"
            )

        for i, player in enumerate(self.game.slots):
            if player:
                if player.finished:
                    player_score = str(player.best_value())
                else:
                    pvals = player.possible_values()
                    player_score = ", ".join(str(v) for v in pvals)
                self.canvas.itemconfig(
                    self.player_texts[i],
                    text=f"{player.show_hand_str()} = {player_score}"
                )
            else:
                self.canvas.itemconfig(self.player_texts[i], text="")


