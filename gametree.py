"""CSC111 Winter 2021: Project Phase 2

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students and Faculty
involved in CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2021 Shayaan Khan, Markus Nimi, Matthew Chan and Aabid Anas."""

from __future__ import annotations
from typing import Optional

GAME_START_MOVE = -1


class GameTree:
    """ A decision tree for Connect3 moves.

    Each node in the tree stores a Connect3 move as well as a boolean representing
    whether the current player is Red or Yellow.

    Instance Attributes:
        - move: the column of the move (0 to 4 inclusive), or GAME_START_MOVE if this is
        the root tree
        - is_yellow_move: whether yellow is the current player to move
        - win_probability: value from 0 to 1 inclusive, following modified
        definitions from A2, where:
            - 1: guaranteed win for computer
            - 0: guaranteed win for other computer/human player
            - A draw results in a value of 0.5
        - _subtrees: the subtrees of this tree, which represent the game trees after a
        possible move by the current player
    """
    move: int
    is_yellow_move: bool
    win_probability: float
    _subtrees: list[GameTree]
    player_selection: str

    def __init__(self, player_selection: str, move: int = GAME_START_MOVE,
                 is_yellow_move: bool = True, win_probability: Optional[float] = 0.0) -> None:
        """Initialize the variables of this new game tree.

        On the root tree, move is the starting move and yellow goes first
        """
        self.move = move
        self.is_yellow_move = is_yellow_move
        self.win_probability = win_probability
        self._subtrees = []
        self.player_selection = player_selection

    def __str__(self) -> str:
        """Return a string representation of this tree."""
        return self._str_indented(0)

    def _str_indented(self, depth: int) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_yellow_move:
            turn_desc = "Yellow's move"
        else:
            turn_desc = "Red's move"
        move_desc = f'{self.move} -> {turn_desc} ({self.win_probability})\n'
        s = '  ' * depth + move_desc
        if self._subtrees == []:
            return s
        else:
            for subtree in self._subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def add_subtree(self, subtree: GameTree) -> None:
        """Add a subtree to this game tree."""
        self._subtrees.append(subtree)
        self._update_win_probability()

    def get_subtrees(self) -> list[GameTree]:
        """Return the subtrees of this game tree."""
        return self._subtrees

    def get_subtree_by_move(self, move: int) -> Optional[GameTree]:
        """Return the subtree corresponding to the given move.

        Return None if no subtree corresponds to that move.
        """
        for subtree in self._subtrees:
            if subtree.move == move:
                return subtree
        return None

    def get_optimal_subtree(self) -> Optional[GameTree]:
        """Return the left-most subtree corresponding to the largest or smallest yellow win
        probability.

        Return None if no subtree corresponds to that probability or there are no subtrees.
        """
        if self._subtrees == []:
            # There are no subtrees; this is uncharted territory
            return None
        else:
            maximum = max(tree.win_probability for tree in self.get_subtrees())
            for subtree in self._subtrees:
                if subtree.win_probability == maximum:
                    return subtree
            return None

    def insert_move_sequence(self, moves: list[int], win_probability: float = 0.0) -> None:
        """Insert the given sequence of moves into this tree.
        """
        move_in_tree = self.get_subtree_by_move(moves[0])
        moves_mutable = moves.copy()
        moves_mutable.reverse()
        prob = win_probability

        # Case 1: move[0] is not a child of the trees root
        if move_in_tree is None:
            turn = False
            self._next_move(moves_mutable, turn, prob)
            return
        # Case 2: moves[0] is a child of this trees root
        elif move_in_tree is not None:
            turn = True
            moves_mutable.pop()
            move_in_tree._next_move(moves_mutable, turn, prob)
            return

    def _next_move(self, moves: list[int], turn: bool, win_probability: float) -> None:
        """Recursive helper function that calls list.pop() in order to add the next move"""
        if moves == []:  # if the moves list gets popped before this method is called
            return None
        move = moves.pop()
        if self.get_subtree_by_move(move) is not None:
            next_turn = not turn
            self._update_win_probability()
            self.get_subtree_by_move(move)._next_move(moves, next_turn, win_probability)
        else:
            self.add_subtree(GameTree(self.player_selection, move, turn, win_probability))
            next_turn = not turn
            self.get_subtree_by_move(move)._next_move(moves, next_turn, win_probability)
        return None

    def _update_win_probability(self) -> None:
        """ Recalculate the win probability of this tree given the red or yellow player

        When this subtree is for this player, take the max because we can choose the path
        When this subtree is for the opponent, take the average because we don't choose the path
        """
        if self.get_subtrees() == []:
            return None
        elif (self.player_selection == "Red" and self.is_yellow_move) \
                or (self.player_selection == "Yellow" and not self.is_yellow_move):
            self.win_probability = \
                max(tree.win_probability for tree in self.get_subtrees())
        else:
            self.win_probability = \
                sum(subtree.win_probability for subtree in self.get_subtrees()) / \
                len(self.get_subtrees())
        return None

# if __name__ == "__main__":

# import python_ta.contracts
# python_ta.contracts.check_all_contracts()

# import python_ta
# python_ta.check_all(config={
#     'extra-imports': [],  # the names (strs) of imported modules
#    'allowed-io': [],  # the names (strs) of functions that call print/open/input
#     'max-line-length': 100,
#     'disable': ['E1136']
# })
