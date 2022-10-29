menu = {}


def get_message_table(size, data):
    mes = ''
    for row in range(size):
        # mes += '| '
        for col in range(size):
            mes += f'{data[row * size + col]}  '
            if col == size - 1:
                mes += '\n'
    return mes
