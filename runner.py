"""CSC111 Winter 2021: Project Phase 2

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students and Faculty
involved in CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2021 Shayaan Khan, Markus Nimi, Matthew Chan and Aabid Anas."""

import connect3
import gametree


def run_learning_algorithm(exploration_probabilities: list[float], player_selection: str,
                           show_stats: bool = True) -> gametree.GameTree:
    """ Play a sequence of Connect3 games using an ExploringPlayer based on the selected player.

    Preconditions:
        - player_selection in {'Red', 'Yellow'}
        - all(0.0 <= probability <= 1.0 for probability in exploration_probabilities)
    """
    game_tree = gametree.GameTree(player_selection)

    results_so_far = []
    count = []
    for i in range(0, len(exploration_probabilities)):
        if player_selection == 'Red':
            yellow_player = connect3.ExploringPlayer(game_tree, exploration_probabilities[i])
            red_player = connect3.RandomPlayer()
        else:
            red_player = connect3.ExploringPlayer(game_tree, exploration_probabilities[i])
            yellow_player = connect3.RandomPlayer()
        winner, moves = connect3.run_game(yellow_player, red_player)
        if winner == player_selection:
            win_prob = 0.0
        elif winner == "Draw":
            win_prob = 0.5
        else:
            win_prob = 1.0
        count.append(winner)
        game_tree.insert_move_sequence(moves, win_prob)
        results_so_far.append(winner)

    if show_stats:
        connect3.plot_game_statistics(results_so_far, player_selection)

    last_20_percent = count[round(len(exploration_probabilities) * 0.8):]

    print("========== ExploringPlayer Learning Algorithm Results (Playing against "
          + str(player_selection) + ") ==========")

    print("---Cumulative:---")

    print("Red: " + str(count.count('Red')) + " (" + str(100 * count.count('Red')
                                                         / len(exploration_probabilities)) + "%)")
    print("Yellow: " + str(count.count('Yellow')) + " (" + str(100 * count.count('Yellow')
                                                               / len(exploration_probabilities))
          + "%)")
    print("---Last 20% of games:---")

    print("Red: " + str(last_20_percent.count('Red')) + " (" + str(
        100 * last_20_percent.count('Red')
        / len(last_20_percent)) + "%)")
    print("Yellow: " + str(last_20_percent.count('Yellow')) + " (" + str(
        100 * last_20_percent.count('Yellow')
        / len(last_20_percent)) + "%)")

    return game_tree


def runner_train_and_play(games: int, tree_player: str) -> gametree.GameTree:
    """Run example with the player as the exploring player, where the AI
    Trains for 80% of games and plays optimally for the last 20%

    Preconditions:
        - tree_player in {'Red', 'Yellow'}
    """

    probabilities = [1.0] * int(games * 0.8) + [0.0] * int(games * 0.2)
    return run_learning_algorithm(probabilities, tree_player)


def runner_train_only(games: int, tree_player: str) -> gametree.GameTree:
    """Run example with the player as the exploring player, where the AI
    Trains for 80% of games and plays optimally for the last 20%

    Preconditions:
        - tree_player in {'Red', 'Yellow'}
    """

    probabilities = [1.0] * games
    return run_learning_algorithm(probabilities, tree_player)

# if __name__ == "__main__":
#     import python_ta.contracts
#     python_ta.contracts.check_all_contracts()

#     import python_ta
#     python_ta.check_all(config={
#         'extra-imports': ['connect3', 'gametree'],  # the names (strs) of imported modules
#         'allowed-io': ['run_learning_algorithm'],
#         # the names (strs) of functions that call print/open/input
#         'max-line-length': 100,
#         'disable': ['E1136']
#     })
