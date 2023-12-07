import os
import random
import subprocess
from collections import deque
from collections.abc import Callable

import chess
import chess.engine
import chess.gaviota
import chess.polyglot
import chess.syzygy
from chess.variant import find_variant

from aliases import DTM, DTZ, Message, Offer_Draw, Outcome, Performance, Resign, UCI_Move
from api import API
from botli_dataclasses import Game_Information
from enums import Game_Status, Variant

from ChatChess import ChatChess

class ChatGPT_Engline: # placeholder engine to use in chat
    def __init__(self):
        self.id = {"name": "ChatGPT using ChatChess"}

class Lichess_Game:
    def __init__(self, api: API, game_information: Game_Information, config: dict) -> None:
        self.config = config
        self.api = api
        self.game_info = game_information
        self.white_time_ms = game_information.state['wtime']
        self.black_time_ms = game_information.state['btime']
        self.status = Game_Status(game_information.state['status'])
        self.draw_enabled: bool = config['engine']['offer_draw']['enabled']
        self.resign_enabled: bool = config['engine']['resign']['enabled']
        self.ponder_enabled: bool = True
        self.out_of_book_counter = 0
        self.opening_explorer_counter = 0
        self.out_of_opening_explorer_counter = 0
        self.cloud_counter = 0
        self.out_of_cloud_counter = 0
        self.chessdb_counter = 0
        self.out_of_chessdb_counter = 0
        consecutive_draw_moves = config['engine']['offer_draw']['consecutive_moves']
        self.draw_scores: deque[chess.engine.PovScore] = deque(maxlen=consecutive_draw_moves)
        consecutive_resign_moves = config['engine']['resign']['consecutive_moves']
        self.resign_scores: deque[chess.engine.PovScore] = deque(maxlen=consecutive_resign_moves)
        self.last_message = 'No eval available yet.'

        # New / edited variables

        self.engine = ChatGPT_Engline()
        self.board = self._setup_board()
        self.bot = self.setupChatGPT()

    # ChatGPT functions

    def setupChatGPT(self):
        bot = ChatChess.Game(self.config["API_key"])
        bot.maxTokens = self.config["GPT_Settings"]["Max_tokens"]
        bot.maxFails = self.config["GPT_Settings"]["Max_fails"]
        bot.maxTime = self.config["GPT_Settings"]["Max_time"]
        return bot

    def make_move(self) -> tuple[UCI_Move, Offer_Draw, Resign]:
        self.bot.board = self.board

        resign = False

        try:
            self.bot.getGPTMove()
            self.last_message = self.bot.message
            move = self.bot.move["ChatGPT"]["uci"]
        except:
            self.last_message = "ERROR - ChatGPT could not respond"
            resign = True
            try:
                move = self.board.parse_san(str(self.board.legal_moves).split("(")[1].split(",")[0])
            except:
                move = self.board.parse_san(str(self.board.legal_moves).split("(")[1].split(",")[0])[:-2]

        print(self.last_message)

        return move.uci(), False and self.draw_enabled, resign and True

    def update(self, gameState_event: dict) -> bool:
        self.status = Game_Status(gameState_event['status'])

        moves = gameState_event['moves'].split()
        if len(moves) <= len(self.board.move_stack):
            return False

        self.board.push(chess.Move.from_uci(moves[-1]))
        self.white_time_ms = gameState_event['wtime']
        self.black_time_ms = gameState_event['btime']

        return True

    # Other functions

    @property
    def is_our_turn(self) -> bool:
        return self.game_info.is_white == self.board.turn

    @property
    def is_game_over(self) -> bool:
        return self.board.is_checkmate() or \
            self.board.is_stalemate() or \
            self.board.is_insufficient_material() or \
            self.board.is_fifty_moves() or \
            self.board.is_repetition()

    @property
    def is_abortable(self) -> bool:
        return len(self.board.move_stack) < 2

    @property
    def is_finished(self) -> bool:
        return self.status != Game_Status.STARTED

    def _setup_board(self) -> chess.Board:
        board = chess.Board() # ChatGPT can only play standard

        for uci_move in self.game_info.state['moves'].split():
            board.push_uci(uci_move)

        return board

    # Functions associated with engine called in other files

    def end_game(self) -> None:
        return

    def start_pondering(self):
        return
