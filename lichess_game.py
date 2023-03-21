import os
import random
import subprocess
from collections import deque

import chess
import chess.engine
import chess.gaviota
import chess.polyglot
import chess.syzygy
from chess.variant import find_variant

from aliases import DTM, DTZ, CP_Score, Depth, Learn, Offer_Draw, Outcome, Performance, Resign, UCI_Move, Weight
from api import API
from enums import Game_Status, Variant

from ChatChess import ChatChess

import yaml

with open('config.yml', 'r') as file:
    config_file = yaml.safe_load(file)

class Engine:
    def __init__(self, id):
        self.id = id

class Lichess_Game:
    def __init__(self, api: API, gameFull_event: dict, config: dict) -> None:
        self.config = config
        self.api = api
        self.board = self._setup_board(gameFull_event)
        self.username: str = self.api.user['username']
        self.white_name: str = gameFull_event['white'].get('name') or f'AI Level {gameFull_event["white"]["aiLevel"]}'
        self.black_name: str = gameFull_event['black'].get('name') or f'AI Level {gameFull_event["black"]["aiLevel"]}'
        self.is_white: bool = gameFull_event['white'].get('name') == self.username
        self.initial_time: int = gameFull_event['clock']['initial']
        self.increment: int = gameFull_event['clock']['increment']
        self.white_time: int = gameFull_event['state']['wtime']
        self.black_time: int = gameFull_event['state']['btime']
        self.variant = Variant(gameFull_event['variant']['key'])
        self.status = Game_Status(gameFull_event['state']['status'])
        self.draw_enabled: bool = config['engine']['offer_draw']['enabled']
        self.resign_enabled: bool = config['engine']['resign']['enabled']
        self.move_overhead = self._get_move_overhead()
        self.last_message = 'No eval available yet.'

        self.bot = self.setupChatGPT()
        self.engine = Engine
        self.engine.id = {"name": "ChatGPT"}

    def setupChatGPT(self):
        bot = ChatChess.Game(config_file["API_key"])
        bot.maxTokens = config_file["GPT_Settings"]["Max_tokens"]
        bot.maxFails = config_file["GPT_Settings"]["Max_fails"]
        bot.maxTime = config_file["GPT_Settings"]["Max_time"]
        return bot

    def make_move(self) -> tuple[UCI_Move, Offer_Draw, Resign]:
        self.bot.board = self.board
        try:
            self.bot.getGPTMove()
        except:
            pass

        self.last_message = self.bot.message
        move = self.bot.move["ChatGPT"]["uci"]

        print(self.last_message)

        return move.uci(), False and self.draw_enabled, False and self.resign_enabled

    def update(self, gameState_event: dict) -> bool:
        self.status = Game_Status(gameState_event['status'])

        moves = gameState_event['moves'].split()
        if len(moves) <= len(self.board.move_stack):
            return False

        self.board.push(chess.Move.from_uci(moves[-1]))
        self.white_time = gameState_event['wtime']
        self.black_time = gameState_event['btime']

        return True

    def get_result_message(self, winner: str | None) -> str:
        winning_name = self.white_name if winner == 'white' else self.black_name
        losing_name = self.white_name if winner == 'black' else self.black_name

        if winner:
            message = f'{winning_name} won'

            if self.status == Game_Status.MATE:
                message += ' by checkmate!'
            elif self.status == Game_Status.OUT_OF_TIME:
                message += f'! {losing_name} ran out of time.'
            elif self.status == Game_Status.RESIGN:
                message += f'! {losing_name} resigned.'
            elif self.status == Game_Status.VARIANT_END:
                message += ' by variant rules!'
        elif self.status == Game_Status.DRAW:
            if self.board.is_fifty_moves():
                message = 'Game drawn by 50-move rule.'
            elif self.board.is_repetition():
                message = 'Game drawn by threefold repetition.'
            elif self.board.is_insufficient_material():
                message = 'Game drawn due to insufficient material.'
            elif self.board.is_variant_draw():
                message = 'Game drawn by variant rules.'
            else:
                message = 'Game drawn by agreement.'
        elif self.status == Game_Status.STALEMATE:
            message = 'Game drawn by stalemate.'
        else:
            message = 'Game aborted.'

        return message

    @property
    def is_our_turn(self) -> bool:
        return self.is_white == self.board.turn

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

    def start_pondering(self) -> None:
        pass

    def stop_pondering(self) -> None:
        pass

    def end_game(self) -> None:
        pass

    def _is_drawish(self) -> bool:
        return False

    def _make_book_move(self) -> tuple[chess.Move, Weight, Learn] | None:
        return

    def _get_book_readers(self) -> list[chess.polyglot.MemoryMappedReader]:
        return []

    def _make_opening_explorer_move(self) -> tuple[chess.Move, Performance, tuple[int, int, int]] | None:
        return

    def _make_cloud_move(self) -> tuple[chess.Move, CP_Score, Depth] | None:
        return

    def _make_chessdb_move(self) -> chess.Move | None:
        return

    def _make_gaviota_move(self) -> tuple[chess.Move, Outcome, DTM, Offer_Draw, Resign] | None:
        return

    def _make_syzygy_move(self) -> tuple[chess.Move, Outcome, DTZ, Offer_Draw, Resign] | None:
        return

    def _value_to_wdl(self, value: int, halfmove_clock: int) -> int:
        if value > 0:
            if value + halfmove_clock <= 100:
                return 2
            else:
                return 1
        elif value < 0:
            if value - halfmove_clock >= -100:
                return -2
            else:
                return -1
        else:
            return 0

    def _get_syzygy_tablebase(self) -> chess.syzygy.Tablebase | None:
        return

    def _get_gaviota_tablebase(self) -> chess.gaviota.PythonTablebase | chess.gaviota.NativeTablebase | None:
        return

    def _make_egtb_move(self) -> tuple[UCI_Move, Outcome, DTZ, DTM | None, Offer_Draw, Resign] | None:
        return

    def _format_move(self, move: chess.Move) -> str:
        if self.board.turn:
            move_number = str(self.board.fullmove_number) + '.'
            return f'{move_number:4} {self.board.san(move)}'
        else:
            move_number = str(self.board.fullmove_number) + '...'
            return f'{move_number:6} {self.board.san(move)}'

    def _format_engine_info(self, info: chess.engine.InfoDict) -> str:
        return "_format_engine_info placeholder"

    def _format_number(self, number: int) -> str:
        return "_format_number placeholder"

    def _format_score(self, score: chess.engine.PovScore) -> str:
        return "_format_score placeholder"

    def _format_egtb_info(self, outcome: Outcome, dtz: DTZ | None = None, dtm: DTM | None = None) -> str:
        return "_format_egtb_info placeholder"

    def _format_book_info(self, weight: Weight, learn: Learn) -> str:
        return "_format_book_info placeholder"

    def _deserialize_learn(self, learn: int) -> tuple[Performance, tuple[float, float, float]]:
        performance = (learn >> 20) & 0b111111111111
        win = ((learn >> 10) & 0b1111111111) / 1020.0 * 100.0
        draw = (learn & 0b1111111111) / 1020.0 * 100.0
        loss = max(100.0 - win - draw, 0.0)

        return performance, (win, draw, loss)

    def _setup_board(self, gameFull_event: dict) -> chess.Board:
        if gameFull_event['variant']['key'] == 'chess960':
            board = chess.Board(gameFull_event['initialFen'], chess960=True)
        elif gameFull_event['variant']['name'] == 'From Position':
            board = chess.Board(gameFull_event['initialFen'])
        else:
            VariantBoard = find_variant(gameFull_event['variant']['name'])
            board = VariantBoard()

        for move in gameFull_event['state']['moves'].split():
            board.push_uci(move)

        return board

    def _get_move_overhead(self) -> int:
        multiplier = self.config.get('move_overhead_multiplier', 1.0)
        return max(int(self.initial_time / 60 * multiplier), 1000)

    def _has_time(self, min_time: int) -> bool:
        if len(self.board.move_stack) < 2:
            return True

        min_time *= 1000
        return self.white_time >= min_time if self.is_white else self.black_time >= min_time

    def _reduce_own_time(self, milliseconds: int) -> None:
        if self.is_white:
            self.white_time -= milliseconds
        else:
            self.black_time -= milliseconds

    def _is_repetition(self, move: chess.Move) -> bool:
        board = self.board.copy()
        board.push(move)
        return board.is_repetition(count=2)
