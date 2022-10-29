from datetime import datetime as dt


def add_log_game(id_user, message):
    time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(f'{id_user}.log', 'a') as file:
        file.write('{} {} {}\n'.format(time, id_user, message))


def add_log_game_step(id_user, name_player, marker_player, id_place):
    time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(f'{id_user}.log', 'a') as file:
        file.write('{} {} {} set \'{}\' to position {}\n'.format(time, id_user, name_player, marker_player, id_place))
