"""CSC111 Winter 2021: Project Phase 2

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students and Faculty
involved in CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2021 Shayaan Khan, Markus Nimi, Matthew Chan and Aabid Anas."""

from __future__ import annotations
import random
from typing import Optional
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from gametree import GameTree

ROW_COUNT = 4
COLUMN_COUNT = 5


################################################################################
# Player classes
################################################################################

class Player:
    """An abstract class representing a Connect3 AI.

    This class can be subclassed to implement different strategies for playing chess.
    """

    def make_move(self, game: Connect3Game, previous_move: Optional[int]) -> int:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        raise NotImplementedError


class RandomPlayer(Player):
    """A Connect3 AI whose strategy is always picking a random move."""

    def make_move(self, game: Connect3Game, previous_move: Optional[int]) -> int:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        possible_moves = game.get_valid_moves()
        return random.choice(possible_moves)


class ExploringPlayer(Player):
    """A Connect3 AI that plays greedily sometimes and randomly other times

    _exploration_probability is a value between 0 and 1, where 1 corresponds to a completely
    random player, and 0 corresponds to an optimal player.
    """

    _game_tree: Optional[GameTree]
    _exploration_probability: float

    def __init__(self, game_tree: GameTree, exploration_probability: float) -> None:
        """Initialize this player."""
        self._game_tree = game_tree
        self._exploration_probability = exploration_probability

    def make_move(self, game: Connect3Game, previous_move: Optional[int]) -> int:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        # First update self._game_tree
        if previous_move is None or self._game_tree is None:
            # White's first move or the game tree is already none
            pass
        elif self._game_tree.get_subtrees() == [] or \
                self._game_tree.get_subtree_by_move(previous_move) is None:
            # We are at a leaf, or the move wasn't expected, or the game tree was already None
            self._game_tree = None
        else:
            # A previous move was given and exists as a subtree
            self._game_tree = self._game_tree.get_subtree_by_move(previous_move)

        # Pick a move
        if self._game_tree is None or self._game_tree.get_subtrees() == [] or \
                random.random() < self._exploration_probability:
            # Either self._game_tree is None or it is a leaf or _exploration_probability
            # In this case, we must revert back to our random tactic
            possible_moves = game.get_valid_moves()
            chosen_move = random.choice(possible_moves)
            if self._game_tree is not None:
                self._game_tree = self._game_tree.get_subtree_by_move(chosen_move)

            return chosen_move
        else:
            # Pick the best move from its subtrees
            best_subtree = self._game_tree.get_optimal_subtree()
            chosen_move = best_subtree.move
            self._game_tree = best_subtree
            return chosen_move


################################################################################
# Game classes and functions
################################################################################

class Connect3Game:
    """A class to represent the game board and all the methods associated with it."""
    # Private instance attributes:
    #   - _board: a two-dimensional representation of the Connect 3 board.
    #   - _valid_moves: a list of valid moves possible with the game state,
    #     where each element corresponds to the index of an available column.
    #   - _is_yellow_active: a boolean to check the active color.
    #   - _move_count: an integer for the number of moves so far

    _board: np.ndarray
    _valid_moves: list[int]
    _is_yellow_active: bool
    _move_count: int

    def __init__(self, board: np.ndarray = None, yellow_active: bool = True) -> None:
        """Initialize an actual Connect3 game. This includes the game board, the possible moves
        (when the game starts), who's turn it is, and the number of moves that have been made so far
        """
        if board is not None:
            self._board = board
        else:
            self._board = np.zeros((ROW_COUNT, COLUMN_COUNT))
        self._valid_moves = [0, 1, 2, 3, 4]
        self._is_yellow_active = yellow_active

    def get_valid_moves(self) -> list:
        """Return a list of valid moves for the active player.
        """
        return self._valid_moves

    def get_board(self) -> np.ndarray:
        """Return self._board"""
        return self._board

    def is_yellow_move(self) -> bool:
        """Return whether the yellow player is to move next.
        """
        return self._is_yellow_active

    def update_valid_moves(self) -> None:
        """Update self._valid_moves.
        """
        game_state = self._board
        top_of_columns = game_state[3]
        self._valid_moves = [i for i in range(COLUMN_COUNT) if top_of_columns[i] == 0]

    def make_move(self, col: int) -> None:
        """Place a disk for the current player in the specified column
        Change self._is_yellow_active afterwards

        Preconditions:
            - col in self._valid_moves
        """
        self.update_valid_moves()

        if col in self._valid_moves:
            # The move is valid
            game_state = self._board
            lowest_row_for_col = 0
            for i in range(0, 4):
                if game_state[i][col] == 0.0:
                    lowest_row_for_col = i
                    break

            if self._is_yellow_active:
                val = 1
            else:
                val = 2
            self._board[lowest_row_for_col][col] = val
            self._is_yellow_active = not self._is_yellow_active

    def get_winner(self) -> Optional[str]:
        """Returns the winner of the current game state.

        Return None if there is no winner
        """
        if self._valid_moves == []:
            return 'Draw'
        elif self._is_winning_move():
            # make_move() changes _is_yellow_active, so we are checking if the last player won
            return 'Red' if self._is_yellow_active else 'Yellow'
        else:
            return None

    def _is_winning_move(self) -> bool:
        """Check if the current player has 3 in a row somewhere and has won the game
        Return True if so, False otherwise

        Preconditions:
            - piece == 1 or piece == 2
        """
        board = self._board

        if self._is_yellow_active:
            piece = 2
        else:
            piece = 1

        # Check horizontal locations for win
        for c in range(0, COLUMN_COUNT - 2):
            for r in range(ROW_COUNT):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece:
                    return True

        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT - 2):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece:
                    return True

        # Check positively sloped diagonals
        for c in range(COLUMN_COUNT - 2):
            for r in range(ROW_COUNT - 2):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and \
                        board[r + 2][c + 2] == piece:
                    return True

        # Check negatively sloped diagonals
        for c in range(COLUMN_COUNT - 2):
            for r in range(2, ROW_COUNT):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and \
                        board[r - 2][c + 2] == piece:
                    return True

        return False


def run_game(yellow: Player, red: Player) -> tuple[str, list[int]]:
    """Run a Connect3 game between the two given players.

    Return the winner and list of moves made in the game.
    """
    game = Connect3Game()

    move_sequence = []
    previous_move = None
    current_player = yellow
    while game.get_winner() is None:

        previous_move = current_player.make_move(game, previous_move)
        game.make_move(previous_move)
        move_sequence.append(previous_move)

        if current_player is yellow:
            current_player = red
        else:
            current_player = yellow

    return game.get_winner(), move_sequence


def plot_game_statistics(results: list[str], player: str) -> None:
    """Plot the outcomes and win probabilities for a given list of Connect3 game results.

    Preconditions:
        - all(r in {'Yellow', 'Red', 'Draw'} for r in results)
    """
    if player == 'Red':
        computer = 'Yellow'
    else:
        computer = 'Red'
    outcomes = []
    for result in results:
        if result == computer:
            outcomes.append(1)
        elif result == 'Draw':
            outcomes.append(0.5)
        else:
            outcomes.append(0)

    cumulative_win_probability = [sum(outcomes[0:i]) / i for i in range(1, len(outcomes) + 1)]
    rolling_win_probability = \
        [sum(outcomes[max(i - 50, 0):i]) / min(50, i) for i in range(1, len(outcomes) + 1)]

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Scatter(y=outcomes, mode='markers',
                             name='Outcome (1 = ' + computer + ' win, 0 = ' + player
                                  + ' win, 0.5 = Draw)'), row=1, col=1)
    fig.add_trace(go.Scatter(y=cumulative_win_probability, mode='lines',
                             name=computer + ' win percentage (cumulative)'), row=2, col=1)
    fig.add_trace(go.Scatter(y=rolling_win_probability, mode='lines',
                             name=computer + ' win percentage (most recent 50 games)'),
                  row=2, col=1)
    fig.update_yaxes(range=[0.0, 1.0], row=2, col=1)

    fig.update_layout(title='Connect3 Game Results', xaxis_title='Game')
    fig.show()

# if __name__ == "__main__":

#     import python_ta.contracts
#     python_ta.contracts.check_all_contracts()

#     import python_ta
#     python_ta.check_all(config={
#         'extra-imports': ["random", "gametree", "plotly.graph_objects",
#                           "plotly.subplots", "numpy"],
#         'allowed-io': [],
#         'max-line-length': 100,
#         'disable': ['E1136']
#     })
