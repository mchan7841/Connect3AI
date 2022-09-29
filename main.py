"""CSC111 Winter 2021: Project Phase 2

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students and Faculty
involved in CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file has been modified from https://github.com/KeithGalli/Connect4-Python
This file is Copyright (c) 2021 Shayaan Khan, Markus Nimi, Matthew Chan and Aabid Anas."""

from __future__ import annotations
import sys
import math
import tkinter as tk
import numpy as np
import pygame

import runner
import connect3
import gametree

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 4
COLUMN_COUNT = 5

SQUARE_SIZE = 100
WINDOW_WIDTH = COLUMN_COUNT * SQUARE_SIZE
WINDOW_HEIGHT = (ROW_COUNT + 1) * SQUARE_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
RADIUS = int(SQUARE_SIZE / 2 - 5)


class MainGUI:
    """A class that sets up a GUI that the player can interact with to choose their color"""
    color_var: tk.StringVar
    ai_var: tk.StringVar
    main: tk.Tk
    main_title: tk.Label
    color_label: tk.Label
    color_select1: tk.Radiobutton
    color_select2: tk.Radiobutton
    ai_label: tk.Label
    ai_select1: tk.Radiobutton
    ai_select2: tk.Radiobutton
    play: tk.Button

    def __init__(self, main: tk.Tk) -> None:
        self.color_var = tk.StringVar(main, "Yellow")
        self.ai_var = tk.StringVar(main, "Random")

        self.main = main
        main.title("Connect 3: Rise of the AI")

        self.main_title = tk.Label(text="Connect 3: Rise of the AI", font="bold")
        self.main_title.pack(padx=20, pady=20)

        self.color_label = tk.Label(text="Choose color to play as: ")
        self.color_label.pack(padx=10, pady=10)

        self.color_select1 = tk.Radiobutton(main, text="Play as Yellow", variable=self.color_var,
                                            value="Yellow")
        self.color_select1.pack(anchor="w")

        self.color_select2 = tk.Radiobutton(main, text="Play as Red", variable=self.color_var,
                                            value="Red")
        self.color_select2.pack(anchor="w")

        self.ai_label = tk.Label(text="Choose AI type to play against: ")
        self.ai_label.pack(padx=10, pady=10)

        self.ai_select1 = tk.Radiobutton(
            main, text="Play against Randomized AI", variable=self.ai_var, value="Random")
        self.ai_select1.pack(anchor="w")

        self.ai_select2 = tk.Radiobutton(
            main, text="Play against Optimized AI", variable=self.ai_var, value="Optimized")
        self.ai_select2.pack(anchor="w")

        self.play = tk.Button(main, text="Play game", command=self.run_game)
        self.play.pack(padx=10, pady=10)

    def run_game(self) -> None:
        """A method to run the game"""
        color_choice = self.color_var.get()
        ai_choice = self.ai_var.get()
        playing_gametree = None
        if ai_choice == "Optimized":
            ai_optimized = True
            playing_gametree = runner.runner_train_and_play(20000, color_choice)
        else:
            ai_optimized = False
        create_and_run_game(color_choice, ai_optimized, playing_gametree)


def draw_board(board: np.ndarray, screen: pygame.display) -> None:
    """Create the virtual Connect3 board that we play in.
    """
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE,
                              SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (
                int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                int(r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 2:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                    WINDOW_HEIGHT - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, YELLOW, (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                    WINDOW_HEIGHT - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
    pygame.display.update()


def create_and_run_game(player_color: str, ai_is_optimal: bool,
                        game_tree: gametree.GameTree) -> None:
    """Create a pop up window to visualize a game with the player against the AI

    Parameters:
        - player_color: the color that the player chooses
        - ai_is_optimal: whether we are using an ExploringPlayer or RandomPlayer
        - game_tree: the gametree used by an ExploringPlayer
        - print_board: whether to print the board state after every move

    Preconditions:
        - player_color in {"Yellow", "Red"}
    """
    pygame.init()
    FONT = pygame.font.SysFont("monospace", 85)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    connect3_game = connect3.Connect3Game()
    draw_board(connect3_game.get_board(), screen)
    pygame.display.update()
    game_over = False
    turn = 1

    previous_human_move = None

    # if player is yellow, player goes first -> even turn is player
    # if player is red, ai goes first -> odd turn is player

    ai = connect3.ExploringPlayer(game_tree, 0) if ai_is_optimal else connect3.RandomPlayer()

    while not game_over:
        if ((turn % 2) == 0 and player_color == "Red") or (
                (turn % 2) == 1 and player_color == "Yellow"):
            # Player turn
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Quit game event
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    # Mouse move event
                    pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, SQUARE_SIZE))
                    pygame.draw.circle(screen, RED if turn == 0 else YELLOW,
                                       (event.pos[0], int(SQUARE_SIZE / 2)), RADIUS)
                    pygame.display.update()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Mouse click event
                    pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, SQUARE_SIZE))
                    connect3_game.update_valid_moves()

                    if int(math.floor(event.pos[0] / SQUARE_SIZE)) in \
                            connect3_game.get_valid_moves():
                        # If the move is valid, drop piece and
                        # check win conditions for the given turn
                        connect3_game.make_move(int(math.floor(event.pos[0] / SQUARE_SIZE)))

                        color = RED if turn == 0 else YELLOW

                        previous_human_move = int(math.floor(event.pos[0] / SQUARE_SIZE))

                        if connect3_game.get_winner() is not None:
                            screen.blit(FONT.render("You win!", True, color), (60, 10))
                            game_over = True

                        draw_board(connect3_game.get_board(), screen)
                        turn = (turn + 1) % 2

                        if game_over:
                            while True:
                                pygame.event.wait()
                                for event2 in pygame.event.get():
                                    if event2.type == pygame.QUIT:
                                        sys.exit()
        else:
            # AI turn
            prev_turn = previous_human_move
            connect3_game.update_valid_moves()
            connect3_game.make_move(ai.make_move(connect3_game, prev_turn))

            # Set the player and colour for the turn
            color = RED if turn == 0 else YELLOW

            if connect3_game.get_winner() is not None:
                screen.blit(FONT.render("AI wins!", True, color), (40, 10))
                game_over = True

            draw_board(connect3_game.get_board(), screen)
            turn = (turn + 1) % 2

            if game_over:
                while True:
                    pygame.event.wait()
                    for event2 in pygame.event.get():
                        if event2.type == pygame.QUIT:
                            sys.exit()


if __name__ == "__main__":
    # Run the MainGUI class
    root = tk.Tk()
    gui = MainGUI(root)
    root.mainloop()

    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    #
    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ["sys", "math", "tkinter",
    #                       "numpy", "pygame", "runner", "connect3", "gametree"],
    #     'allowed-io': ["runner.run_learning_algorithm"],
    #     'max-line-length': 100,
    #     'disable': ['E1136']
    # })
