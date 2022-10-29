import game as mod_game
import os.path


def save_game_to_file_csv(file_name='game.csv', separator=';'):
    with open(file_name, 'w') as file_data:
        file_data.write('game_table_size' + separator)
        file_data.write('game_count_for_win' + separator)
        file_data.write('game_count_players' + separator)
        file_data.write('game_id_player_win' + separator)
        file_data.write('game_id_player_current' + separator)
        file_data.write('game_marker_zero' + separator)
        file_data.write('game_markers' + separator)
        file_data.write('game_table' + '\n')

        file_data.write(str(mod_game.game_table_size) + separator)
        file_data.write(str(mod_game.game_count_for_win) + separator)
        file_data.write(str(mod_game.game_count_players) + separator)
        file_data.write(str(mod_game.game_id_player_win) + separator)
        file_data.write(str(mod_game.game_id_player_current) + separator)
        file_data.write(mod_game.game_marker_zero + separator)
        file_data.write('|'.join(mod_game.game_markers) + separator)
        file_data.write('|'.join(mod_game.game_table) + '\n')
    return True


def load_game_from_file_csv(file_name='game.csv', separator=';'):
    if not os.path.exists(file_name):
        return False

    with open(file_name, 'r') as file_data:
        param_keys = file_data.readline().rstrip().split(separator)
        param_data = file_data.readline().rstrip().split(separator)
        dict_data = dict(zip(param_keys, param_data))
        dict_data['game_markers'] = dict_data['game_markers'].split('|')
        dict_data['game_table'] = dict_data['game_table'].split('|')
        mod_game.load(dict_data)
        return True
