import numpy as np
from numba import jit, prange
import time


class MonteCarloSimulator:
    """Monte Carlo simulation to estimate win probability for each possible action

    Optimized with Numba JIT compilation for Python 3.14+ with parallel execution
    """

    def __init__(self, num_simulations=1000, parallel=True):
        self.num_simulations = num_simulations
        self.parallel = parallel

    def simulate_action(self, game_state, action):
        """
        Simulate an action n times and return win probability and time taken

        Args:
            game_state: Current game state (dealer hand, player hand, deck)
            action: 'hit', 'stand', 'double', or 'split'

        Returns:
            tuple: (win_probability, time_taken_in_seconds)
        """
        start = time.time()

        # Convert Card objects to numpy arrays for Numba
        # Fix: If dealer has exactly 2 cards, one is the hole card which should be unknown.
        # We use only the visible card (first one) and add the hole card back to the deck for simulation.
        # This prevents the "Perfect Information" cheat where the agent sees the hidden card.
        sim_dealer_hand = game_state['dealer_hand']
        sim_deck = game_state['deck_cards']
        
        if len(sim_dealer_hand) == 2:
            # Assume first card is visible, second is hole card
            # Use only visible card for dealer
            # Add hole card to deck pool (as it's unknown)
            # Create new lists to avoid modifying original game_state
            hole_card = sim_dealer_hand[1]
            sim_dealer_hand = [sim_dealer_hand[0]]
            sim_deck = sim_deck + [hole_card]
            
        player_values, player_ace_flags = self._cards_to_arrays(game_state['player_hand'])
        dealer_values, dealer_ace_flags = self._cards_to_arrays(sim_dealer_hand)
        deck_values, deck_ace_flags = self._cards_to_arrays(sim_deck)

        # Validate we have enough cards to simulate
        if len(deck_values) < 10:
            # Not enough cards to simulate properly
            print(f"[WARNING] Only {len(deck_values)} cards in deck, using basic estimation")
            return (0.5, 0.0)  # Return neutral probability

        # Convert action to integer code
        action_code = {'hit': 0, 'stand': 1, 'double': 2, 'split': 3}.get(action, 1)

        # Run simulations with parallel option
        if self.parallel:
            wins = _simulate_numba_parallel(
                player_values, player_ace_flags,
                dealer_values, dealer_ace_flags,
                deck_values, deck_ace_flags,
                action_code, self.num_simulations
            )
        else:
            wins = _simulate_numba(
                player_values, player_ace_flags,
                dealer_values, dealer_ace_flags,
                deck_values, deck_ace_flags,
                action_code, self.num_simulations
            )

        total_time = time.time() - start
        win_probability = wins / self.num_simulations

        sim_type = " (PARALLEL)" if self.parallel else ""
        print(f"[DEBUG] {action.upper()}{sim_type} - {self.num_simulations} sims: {win_probability:.1%} in {total_time:.4f}s ({self.num_simulations/total_time:.0f} sims/sec)")

        return (win_probability, total_time)

    def _cards_to_arrays(self, cards):
        """Convert list of Card objects to numpy arrays of values and ace flags"""
        # Filter out None values (hidden cards)
        valid_cards = [c for c in cards if c is not None]
        
        if not valid_cards:
            return np.array([], dtype=np.int32), np.array([], dtype=np.int32)
        
        values = np.array([card.value for card in valid_cards], dtype=np.int32)
        ace_flags = np.array([1 if card.rank == "A" else 0 for card in valid_cards], dtype=np.int32)
        return values, ace_flags

    def get_action_probabilities(self, game_state, available_actions):
        """
        Get win probabilities and timing for all available actions

        Args:
            game_state: Current game state
            available_actions: List of available actions (e.g., ['hit', 'stand', 'double', 'split'])

        Returns:
            dict: {action: [probability, time_taken]}
        """
        probabilities = {}
        total_time = 0.0

        for action in available_actions:
            prob, time_taken = self.simulate_action(game_state, action)
            probabilities[action] = [prob, time_taken]
            total_time += time_taken

        print(f"\n[TOTAL] All actions completed in {total_time:.4f}s\n")
        return probabilities


@jit(nopython=True)
def _simulate_numba(player_vals, player_ace_flags, dealer_vals, dealer_ace_flags,
                   deck_vals, deck_ace_flags, action_code, num_sims):
    """
    Numba-compiled simulation function (serial)
    Returns: number of wins
    """
    wins = 0
    deck_size = len(deck_vals)
    max_hand_size = 12

    for sim in range(num_sims):
        wins += _run_single_sim(
            player_vals, player_ace_flags,
            dealer_vals, dealer_ace_flags,
            deck_vals, deck_ace_flags,
            action_code, deck_size, max_hand_size
        )

    return wins


@jit(nopython=True, parallel=True)
def _simulate_numba_parallel(player_vals, player_ace_flags, dealer_vals, dealer_ace_flags,
                            deck_vals, deck_ace_flags, action_code, num_sims):
    """
    Numba-compiled simulation function (parallel with prange)
    Returns: number of wins
    """
    wins = 0
    deck_size = len(deck_vals)
    max_hand_size = 12
    
    # Use prange for parallel loop
    results = np.zeros(num_sims, dtype=np.int32)
    for sim in prange(num_sims):
        results[sim] = _run_single_sim(
            player_vals, player_ace_flags,
            dealer_vals, dealer_ace_flags,
            deck_vals, deck_ace_flags,
            action_code, deck_size, max_hand_size
        )
    
    return np.sum(results)


@jit(nopython=True)
def _run_single_sim(player_vals, player_ace_flags, dealer_vals, dealer_ace_flags,
                   deck_vals, deck_ace_flags, action_code, deck_size, max_hand_size):
    """Run a single simulation"""
    # Create copies for this simulation
    p_hand_size = len(player_vals)
    p_hand = np.zeros(max_hand_size, dtype=np.int32)
    p_hand[:p_hand_size] = player_vals
    p_aces = int(np.sum(player_ace_flags))

    d_hand_size = len(dealer_vals)
    d_hand = np.zeros(max_hand_size, dtype=np.int32)
    d_hand[:d_hand_size] = dealer_vals
    d_aces = int(np.sum(dealer_ace_flags))

    # Shuffle deck (Fisher-Yates shuffle)
    deck = deck_vals.copy()
    d_ace_flags = deck_ace_flags.copy()

    for i in range(deck_size - 1, 0, -1):
        j = int(np.random.random() * (i + 1))
        deck[i], deck[j] = deck[j], deck[i]
        d_ace_flags[i], d_ace_flags[j] = d_ace_flags[j], d_ace_flags[i]

    deck_idx = 0

    # Execute the action
    if action_code == 0:  # HIT
        if deck_idx < deck_size and p_hand_size < max_hand_size:
            p_hand[p_hand_size] = deck[deck_idx]
            p_aces += d_ace_flags[deck_idx]
            p_hand_size += 1
            deck_idx += 1

        p_val = _calculate_value_fast(p_hand, p_hand_size, p_aces)
        if p_val > 21:
            return 0  # Loss - bust

        # Play out player hand
        p_hand, p_hand_size, p_aces, deck_idx = _play_player_hand_fast(
            p_hand, p_hand_size, p_aces, deck, d_ace_flags, deck_idx, deck_size, max_hand_size)

    elif action_code == 1:  # STAND
        pass  # Do nothing

    elif action_code == 2:  # DOUBLE
        if deck_idx < deck_size and p_hand_size < max_hand_size:
            p_hand[p_hand_size] = deck[deck_idx]
            p_aces += d_ace_flags[deck_idx]
            p_hand_size += 1
            deck_idx += 1

        p_val = _calculate_value_fast(p_hand, p_hand_size, p_aces)
        if p_val > 21:
            return 0  # Loss - bust

    elif action_code == 3:  # SPLIT
        # Simplified: just hit once
        if deck_idx < deck_size and p_hand_size < max_hand_size:
            p_hand[p_hand_size] = deck[deck_idx]
            p_aces += d_ace_flags[deck_idx]
            p_hand_size += 1
            deck_idx += 1

        p_hand, p_hand_size, p_aces, deck_idx = _play_player_hand_fast(
            p_hand, p_hand_size, p_aces, deck, d_ace_flags, deck_idx, deck_size, max_hand_size)

    # Check if player busted
    player_value = _calculate_value_fast(p_hand, p_hand_size, p_aces)
    if player_value > 21:
        return 0  # Loss

    # Play dealer's hand
    d_hand, d_hand_size, d_aces, deck_idx = _play_dealer_hand_fast(
        d_hand, d_hand_size, d_aces, deck, d_ace_flags, deck_idx, deck_size, max_hand_size)
    dealer_value = _calculate_value_fast(d_hand, d_hand_size, d_aces)

    # Determine outcome
    if dealer_value > 21:
        return 1  # Player wins (dealer bust)
    elif player_value > dealer_value:
        return 1  # Player wins
    else:
        return 0  # Loss or push


@jit(nopython=True)
def _calculate_value_fast(hand, hand_size, num_aces):
    """Calculate best hand value (Numba-optimized)"""
    total = 0
    for i in range(hand_size):
        total += hand[i]

    aces = num_aces
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


@jit(nopython=True)
def _play_player_hand_fast(hand, hand_size, aces, deck, deck_ace_flags, deck_idx, deck_size, max_hand_size):
    """Play out player's hand with basic strategy (Stand on Hard 17+ or Soft 18+)"""
    while True:
        value = _calculate_value_fast(hand, hand_size, aces)

        # Basic Strategy Logic:
        # 1. Hard 17 or more: Stand
        # 2. Soft 18 or more: Stand
        # 3. Soft 17: Hit (aggressive, common in casinos)
        # 4. Anything else: Hit
        
        should_hit = False
        
        if value >= 18:
            should_hit = False
        elif value == 17:
             # Hit only if it's a "soft" 17 (meaning we are using an Ace as 11)
             # To check if soft: if we have aces, calculate value assuming aces=0.
             # If total is value - 10, then one ace is active as 11.
             
             # Simpler check: we know total=17.
             # If we subtract 10 and still have a valid hand, it was soft.
             # But _calculate_value_fast hides the raw sum.
             
             # Let's re-verify "softness"
             # raw_sum = sum(hand)
             # if raw_sum <= 11 and aces > 0 -> then value is soft
             
             raw_sum = 0
             for i in range(hand_size):
                 raw_sum += hand[i]
                 
             if raw_sum <= 7 and aces > 0: # e.g. A,6 (1+6=7) -> 17. Soft.
                 should_hit = True # Hit soft 17
             else:
                 should_hit = False # Stand hard 17
                 
        else: # value <= 16
            should_hit = True

        if should_hit:
            if deck_idx < deck_size and hand_size < max_hand_size:
                hand[hand_size] = deck[deck_idx]
                aces += deck_ace_flags[deck_idx]
                hand_size += 1
                deck_idx += 1
            else:
                break
        else:
            break

        if _calculate_value_fast(hand, hand_size, aces) > 21:
            break

    return hand, hand_size, aces, deck_idx


@jit(nopython=True)
def _play_dealer_hand_fast(hand, hand_size, aces, deck, deck_ace_flags, deck_idx, deck_size, max_hand_size):
    """Play out dealer's hand (hit until 17+)"""
    while True:
        value = _calculate_value_fast(hand, hand_size, aces)

        if value >= 17:
            break

        if deck_idx < deck_size and hand_size < max_hand_size:
            hand[hand_size] = deck[deck_idx]
            aces += deck_ace_flags[deck_idx]
            hand_size += 1
            deck_idx += 1
        else:
            break

    return hand, hand_size, aces, deck_idx
