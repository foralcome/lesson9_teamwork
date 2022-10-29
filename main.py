from telegram_token import TELEGRAM_TOKEN_PY

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import game as mod_game
import file_game as mod_file
import log_game as mod_log

START_MENU, CHOICE_START_MENU, LOAD_GAME, SAVE_GAME, CHOICE_MARKER, CHOICE_GAME_STEP, GAME_FINISH, GAME_NOBODYWIN, REPEATE_GAME, CLOSE = range(
    10)


async def repeate_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Да':
        mod_game.init()
        reply_keyboard = [["X", "0"]]
        await update.message.reply_text(
            "Please select marker: ",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="X or 0?"
            ),
        )
        return CHOICE_MARKER
    if update.message.text == 'Нет':
        reply_keyboard = [["new game", "load game", "save game", "close"]]
        await update.message.reply_text(
            "Choice item:",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="menu"
            ),
        )
        return CHOICE_START_MENU


async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["new game", "load game", "save game", "close"]]

    await update.message.reply_text(
        "Choice item:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="menu"
        ),
    )

    return CHOICE_START_MENU


async def choice_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    if update.message.text == 'new game':
        mod_log.add_log_game(user.id, 'start new game')
        # создаём новую игру 3х3
        mod_game.init()

        reply_keyboard = [["X", "0"]]
        await update.message.reply_text(
            "Please select marker: ",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="X or 0?"
            ),
        )
        return CHOICE_MARKER
    if update.message.text == 'load game':
        mod_log.add_log_game(user.id, 'load game')
        await update.message.reply_text("Load game...")
        # загрузить информацию об игре из файла
        mod_file.load_game_from_file_csv(f'{user.id}.csv')
        # показать поле игры
        await update.message.reply_text(mod_game.get_message_game_table())

        reply_keyboard = [["new game", "load game", "save game", "close"]]
        await update.message.reply_text(
            "Choice item:",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="menu"
            ),
        )
        return CHOICE_START_MENU
    if update.message.text == 'save game':
        mod_log.add_log_game(user.id, 'save game')
        await update.message.reply_text("Save game...")
        mod_file.save_game_to_file_csv(f'{user.id}.csv')

        reply_keyboard = [["new game", "load game", "save game", "close"]]
        await update.message.reply_text(
            "Choice item:",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="menu"
            ),
        )
        return CHOICE_START_MENU
    if update.message.text == 'close':
        mod_log.add_log_game(user.id, 'close game')
        # logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            f"Bye, {user.name}!", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        mod_log.add_log_game(user.id, 'close game')
        return ConversationHandler.END


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('STEP')
    await update.message.reply_text(update.message.text)
    reply_keyboard = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"]
    ]
    await update.message.reply_text(
        mod_game.get_message_game_table(),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
        ),
    )
    return CHOICE_GAME_STEP


async def choice_market_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    mod_game.set_marker_player(update.message.text)
    mod_log.add_log_game(user.id, 'player select marker - ' + update.message.text)
    await update.message.reply_text('Your marker is ' + update.message.text)

    reply_keyboard = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"]
    ]
    await update.message.reply_text(
        mod_game.get_message_game_table(),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
        ),
    )

    return CHOICE_GAME_STEP


async def step_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    if mod_game.get_count_free_place() == 0:
        mod_log.add_log_game(user.id, 'game over')
        await update.message.reply_text('GAME OVER!')
        return GAME_FINISH

    id_player = mod_game.get_id_player_current()
    await update.message.reply_text(f'Your player id {id_player}')
    marker_player = mod_game.get_marker_player(id_player)
    await update.message.reply_text(f'Your marker is {marker_player}')
    marker_zero = mod_game.get_marker_zero()
    id_place_in_game_table = int(update.message.text)

    # обработка хода игрока
    if mod_game.get_data_from_table(id_place_in_game_table - 1) != marker_zero:
        mod_log.add_log_game(user.id, 'error step player in place #' + update.message.text)
        await update.message.reply_text(f'Неверный ход! Ячейка {id_place_in_game_table} занята!')
    else:
        mod_log.add_log_game_step(user.id, 'player', marker_player, update.message.text)
        mod_game.set_data_in_table(id_place_in_game_table - 1, marker_player)
        mod_game.change_id_player_current()
        await update.message.reply_text(f'Ваш ход сделан в ячейку {id_place_in_game_table}.')

        await update.message.reply_text(mod_game.get_message_game_table())

        # проверяем выигрыш игрока
        id_player = mod_game.get_id_player_current()
        id_player_win = mod_game.get_id_player_win()
        if id_player_win != 0:
            mod_log.add_log_game(user.id, f'finish game! won player {id_player_win}')
            await update.message.reply_text(mod_game.get_message_game_table())
            await update.message.reply_text(f'WON PLAYER {id_player_win}! CONGRATULATION!')
            reply_keyboard = [["Да", "Нет"]]
            await update.message.reply_text(
                "Ещё одна игра?",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Да или Нет?"
                ),
            )
            return REPEATE_GAME

        # обработка хода бота
        marker_bot = mod_game.get_marker_player(id_player)
        id_place_bot = mod_game.get_id_place_for_win(marker_bot)
        if id_place_bot != -1:
            mod_log.add_log_game_step(user.id, 'bot', marker_bot, id_place_bot + 1)
            await update.message.reply_text(f'Победа близко ...!')
            mod_game.set_data_in_table(id_place_bot, marker_bot)
            await update.message.reply_text(f'Бот: Я хожу в ячейку {id_place_bot + 1}.')
        else:
            id_place_bot = mod_game.get_id_place_for_win(marker_player)
            if id_place_bot != -1:
                mod_log.add_log_game_step(user.id, 'bot', marker_bot, id_place_bot + 1)
                await update.message.reply_text(f'Бот: Опасная ситуация. Хожу чтобы не проиграть в ...')
                mod_game.set_data_in_table(id_place_bot, marker_bot)
                await update.message.reply_text(f'Бот: Я хожу в ячейку {id_place_bot + 1}.')
            else:
                id_place_bot = mod_game.get_id_place_free()
                if id_place_bot != -1:
                    mod_log.add_log_game_step(user.id, 'bot', marker_bot, id_place_bot + 1)
                    await update.message.reply_text(f'Бот: Куда бы поставить? Например...!')
                    mod_game.set_data_in_table(id_place_bot, marker_bot)
                    await update.message.reply_text(f'Бот: Я хожу в ячейку {id_place_bot + 1}.')
                else:
                    mod_log.add_log_game(user.id, f'finish game! nobody won')
                    await update.message.reply_text(f'Бот: Похоже это ничья!')
                    reply_keyboard = [["Да", "Нет"]]
                    await update.message.reply_text(
                        "Ещё одна игра?",
                        reply_markup=ReplyKeyboardMarkup(
                            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Да или Нет?"
                        ),
                    )
                    return REPEATE_GAME

        mod_game.change_id_player_current()

        # проверяем выигрыш бота
        id_bot_win = mod_game.get_id_player_win()
        if id_bot_win != 0:
            mod_log.add_log_game(user.id, f'finish game! bot won')
            await update.message.reply_text(mod_game.get_message_game_table())
            await update.message.reply_text(f'WON PLAYER {id_bot_win}! CONGRATULATION!')
            reply_keyboard = [["Да", "Нет"]]
            await update.message.reply_text(
                "Ещё одна игра?",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Да или Нет?"
                ),
            )
            return REPEATE_GAME

    # запрос хода игрока в телеграм
    reply_keyboard = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"]
    ]
    await update.message.reply_text(
        mod_game.get_message_game_table(),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
        ),
    )
    return CHOICE_GAME_STEP


async def nobodywin_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["new game", "load game", "save game", "close"]]

    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="menu"
        ),
    )

    return CHOICE_START_MENU


async def finish_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id_player_win = mod_game.get_id_player_win()
    if id_player_win != 0:
        await update.message.reply_text(
            f'Player{id_player_win} win!'
        )
    else:
        await update.message.reply_text(
            f'Nobody won!'
        )
    return ConversationHandler.END


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        f"Bye, {user.name}!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# Create the Application and pass it your bot's token.
application = Application.builder().token(TELEGRAM_TOKEN_PY).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_menu)],
    states={
        START_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_menu)],
        CHOICE_START_MENU: [MessageHandler(filters.Regex("^(new game|load game|save game|close)$"), choice_start_menu)],
        CHOICE_MARKER: [MessageHandler(filters.Regex("^(X|0)$"), choice_market_game)],
        CHOICE_GAME_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_game)],
        GAME_NOBODYWIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, nobodywin_game)],
        REPEATE_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, repeate_game)],
        GAME_FINISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_game)],
        CLOSE: [MessageHandler(filters.COMMAND, close)],
    },
    fallbacks=[CommandHandler("close", close)],
)

application.add_handler(conv_handler)

application.run_polling()
