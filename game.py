import random

from telegram_token import TELEGRAM_TOKEN_PY
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from random import choice

import user_interface as ui

app = None
game_table_size = 3
game_count_for_win = 3
game_table = []

game_count_players = 2
game_id_player_win = 0
game_id_player_current = 0

game_markers = ['X', '0']
game_marker_zero = '_'
game_marker_player_1 = 'X'
game_marker_player_2 = '0'


def init(size=3, count_for_win=3):
    global app
    app = ApplicationBuilder().token(TELEGRAM_TOKEN_PY).build()

    global game_table
    global game_table_size
    global game_count_for_win
    global game_id_player_win
    global game_id_player_current
    game_table_size = size
    game_count_for_win = count_for_win
    game_table = [game_marker_zero] * (game_table_size ** 2)
    game_id_player_win = 0
    game_id_player_current = 1


def load( dict_data ):
    if 'game_table_size' in dict_data:
        global game_table_size
        game_table_size = int(dict_data['game_table_size'])
    if 'game_count_for_win' in dict_data:
        global game_count_for_win
        game_count_for_win = int(dict_data['game_count_for_win'])
    if 'game_count_players' in dict_data:
        global game_count_players
        game_count_players = int(dict_data['game_count_players'])
    if 'game_id_player_win' in dict_data:
        global game_id_player_win
        game_id_player_win = int(dict_data['game_id_player_win'])
    if 'game_id_player_current' in dict_data:
        global game_id_player_current
        game_id_player_current = int(dict_data['game_id_player_current'])
    if 'game_marker_zero' in dict_data:
        global game_marker_zero
        game_marker_zero = dict_data['game_marker_zero']
    if 'game_markers' in dict_data:
        global game_markers
        game_markers = dict_data['game_markers']
    if 'game_table' in dict_data:
        global game_table
        game_table = dict_data['game_table']


def set_marker_player(marker):
    global game_markers
    global game_marker_player_1
    global game_marker_player_2

    if marker == 'X':
        game_markers = ['X', '0']
        game_marker_player_1, game_marker_player_2 = game_markers
    else:
        game_markers = ['0', 'X']
        game_marker_player_1, game_marker_player_2 = game_markers


def get_id_player_current():
    return game_id_player_current


def set_id_player_current(id_player):
    global game_id_player_current
    game_id_player_current = id_player


def change_id_player_current():
    global game_id_player_current
    game_id_player_current += 1
    if game_id_player_current > game_count_players:
        game_id_player_current = 1
    return game_id_player_current


def get_marker_player(id_player):
    return game_markers[id_player - 1]


def get_marker_zero():
    return game_marker_zero


def get_data_from_table(id_place):
    if id_place < 0 or id_place > (game_table_size ** 2 - 1):
        return None
    return game_table[id_place]


def set_data_in_table(id_place, value):
    global game_table
    if id_place < 0 or id_place > (game_table_size ** 2 - 1):
        return False
    game_table[id_place] = value
    return True


def check_win_player_on_horizontal(table, marker_player):
    for row in range(game_table_size):
        marker_player_count = 0
        for col in range(game_table_size):
            if table[row * game_table_size + col] == marker_player:
                marker_player_count += 1
        if marker_player_count == game_count_for_win:
            return True


def check_win_player_on_vertical(table, marker_player):
    for col in range(game_table_size):
        marker_player_count = 0
        for row in range(game_table_size):
            if table[row * game_table_size + col] == marker_player:
                marker_player_count += 1
        if marker_player_count == game_count_for_win:
            return True


def check_win_player_on_main_diagonal(table, marker_player):
    marker_player_count = 0
    for i in range(game_table_size):
        if table[i + i * game_table_size] == marker_player:
            marker_player_count += 1
        if marker_player_count == game_count_for_win:
            return True


def check_win_player_on_reverse_diagonal(table, marker_player):
    marker_player_count = 0
    for i in range(game_table_size):
        if table[game_table_size * (i + 1) - i - 1] == marker_player:
            marker_player_count += 1
        if marker_player_count == game_count_for_win:
            return True


def check_win_player(table, marker_player):
    # проверяем горизонталь
    if check_win_player_on_horizontal(table, marker_player) == True:
        return True

    # проверяем вертикаль
    if check_win_player_on_vertical(table, marker_player) == True:
        return True

    # проверяем главную диагональ
    if check_win_player_on_main_diagonal(table, marker_player) == True:
        return True

    # проверяем обратную диагональ
    if check_win_player_on_reverse_diagonal(table, marker_player) == True:
        return True

    return False


def get_id_player_win():
    global game_id_player_win
    game_id_player_win = 0

    if check_win_player(game_table, game_marker_player_1):
        game_id_player_win = 1
        return game_id_player_win

    if check_win_player(game_table, game_marker_player_2):
        game_id_player_win = 2
        return game_id_player_win

    return game_id_player_win


def get_id_place_for_win(player_marker='0'):
    copy_game_table = game_table.copy()
    # для каждой свободной ячейка проверяем возможность выигрыша
    for i in range(len(game_table)):
        if game_table[i] == game_marker_zero:
            copy_game_table[i] = player_marker
            if check_win_player(copy_game_table, player_marker) == True:
                return i
            else:
                copy_game_table[i] = game_marker_zero
    return -1


def get_id_place_free():
    id_places = [i for i in range(len(game_table)) if game_table[i] == game_marker_zero]
    if len(id_places) > 0:
        return random.choice(id_places)
    return -1


def get_count_free_place():
    count = 0
    for d in game_table:
        if d == game_marker_zero:
            count += 1
    return count


def get_message_game_table():
    global game_table
    return ui.get_message_table(game_table_size, game_table)
