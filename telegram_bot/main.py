import numpy as np
import requests
import pymorphy2
import re
import joblib

from constants import FAST_API_ARINA, API_KEY_ARINA
from sklearn.metrics.pairwise import cosine_similarity
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

DEFAULT_EXCHANGE, CURRENCY_FROM, CURRENCY_TO, EXCHANGE_WAY = range(4)
EXCHANGE_AIM = [["BYN", "Конверсия"]]
EXCHANGE_CHOICE_WAY = [['Цифровой банк', 'По карточке', 'Наличные']]
CURRENCY_AVAILABLE = [['USD', 'EUR', 'RUB']]

morpher = pymorphy2.MorphAnalyzer()
key_lemmas_vectors = joblib.load('./lemmas.pickle')
vectorizer = joblib.load('./vectorizer.pickle')
X = joblib.load('./keys_responses.pickle')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Добро пожаловать')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Помощь пока недоступна')


async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Для более точного ответа необходимо ответить на дополнительные вопросы.\n"
        "Команда /cancel, чтобы прекратить разговор.\n\n"
        "Пожалуйста, выберите интересующий обмен.",
        reply_markup=ReplyKeyboardMarkup(
            EXCHANGE_AIM, one_time_keyboard=True
        ),
    )
    return DEFAULT_EXCHANGE


async def default_exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    way_input = update.message.text
    result = ConversationHandler.END
    if way_input == EXCHANGE_AIM[0][0]:
        context.user_data["BYN"] = 1
        await update.message.reply_text(
            "Пожалуйста, выберите валюту.",
            reply_markup=ReplyKeyboardMarkup(
                CURRENCY_AVAILABLE, one_time_keyboard=True
            ),
        )
        result = CURRENCY_TO
    elif way_input == EXCHANGE_AIM[0][1]:
        context.user_data["BYN"] = 0
        await update.message.reply_text(
            "Пожалуйста, выберите имеющуюся валюту.",
            reply_markup=ReplyKeyboardMarkup(
                CURRENCY_AVAILABLE, one_time_keyboard=True
            ),
        )
        result = CURRENCY_FROM
    else:
        await update.message.reply_text(
            "Неверные данные, пожалуйста, попробуйте снова.",
            reply_markup=ReplyKeyboardRemove(),
        )
        result = ConversationHandler.END

    return result


async def currency_from_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    currency_from_input = np.array(re.findall(r'\w+', update.message.text))
    result = CURRENCY_TO
    if not np.isin(currency_from_input, CURRENCY_AVAILABLE).all:
        await update.message.reply_text(
            "Неверные данные, пожалуйста, попробуйте снова.",
            reply_markup=ReplyKeyboardRemove(),
        )
        result = ConversationHandler.END
    else:
        context.user_data["currency_from"] = currency_from_input
        await update.message.reply_text(
            "Пожалуйста, выберите интересуемую валюту.",
            reply_markup=ReplyKeyboardMarkup(
                CURRENCY_AVAILABLE, one_time_keyboard=True
            ),
        )
    return result


async def currency_to_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    currency_to_input = np.array(re.findall(r'\w+', update.message.text))
    result = EXCHANGE_WAY
    if not np.isin(currency_to_input, CURRENCY_AVAILABLE).all:
        await update.message.reply_text(
            "Неверные данные, пожалуйста, попробуйте снова.",
            reply_markup=ReplyKeyboardRemove()
        )
        result = ConversationHandler.END
    else:
        context.user_data["currency_to"] = currency_to_input
        if not context.user_data["BYN"]:
            currency_to = set(currency_to_input)
            currency_from = set(context.user_data["currency_from"])
            if currency_to & currency_from:
                await update.message.reply_text(
                    "Пожалуйста, выберите разные валюты.",
                    reply_markup=ReplyKeyboardRemove()
                )
                result = ConversationHandler.END
        if result is not ConversationHandler.END:
            await update.message.reply_text(
                "Пожалуйста, выберите способ обмена.",
                reply_markup=ReplyKeyboardMarkup(
                    EXCHANGE_CHOICE_WAY, one_time_keyboard=True
                ),
            )
    return result


async def exchange_way_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exchange_way = [
        way
        for way in EXCHANGE_CHOICE_WAY[0]
        if way[0] in update.message.text
    ]
    if not exchange_way:
        await update.message.reply_text(
            "Неверные данные, пожалуйста, попробуйте снова.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        # загружаю обновленный df в файл "../priorbank_currency_exchange.csv"
        # requests.get(FAST_API_ARINA + '/currency/uploaded_currency')
        if context.user_data['BYN']:
            request = FAST_API_ARINA + '/currency/BYN'
            params = {
                'currency_to': context.user_data['currency_to'],
                'exchange_way': exchange_way
            }
        else:
            request = FAST_API_ARINA + '/currency/conversion'
            params = {
                'currency_to': context.user_data['currency_to'],
                'exchange_way': exchange_way,
                'currency_from': context.user_data['currency_from']
            }

        response = requests.get(request, params)
        await update.message.reply_text(
            response.json()
        )
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Отмена операции.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def handle_response(text: str) -> str:
    user_message = text.lower()
    user_query_split = user_message.split()
    final_query = []
    for word in user_query_split:
        final_query.append(morpher.parse(word)[0].normal_form)
    user_query_vector = vectorizer.transform([' '.join(map(str, final_query))])
    similarity_scores = cosine_similarity(key_lemmas_vectors, user_query_vector)
    most_similar_index = similarity_scores.argmax()
    return X['Response'].iloc[most_similar_index]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    response = handle_response(text)

    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Bot Started')

    app = Application.builder().token(API_KEY_ARINA).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('currency', currency_command)],
        states={
            DEFAULT_EXCHANGE: [MessageHandler(filters.TEXT, default_exchange_command)],
            CURRENCY_FROM: [MessageHandler(filters.TEXT, currency_from_command)],
            CURRENCY_TO: [MessageHandler(filters.TEXT, currency_to_command)],
            EXCHANGE_WAY: [MessageHandler(filters.TEXT, exchange_way_command)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
    )
    app.add_handler(conv_handler)

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Bot polling')
    app.run_polling(poll_interval=3)
