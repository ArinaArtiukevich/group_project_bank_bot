import pandas as pd
import pymorphy2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import constants
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import joblib

morpher = pymorphy2.MorphAnalyzer()
key_lemmas_vectors = joblib.load('./lemmas.pickle')
vectorizer = joblib.load('./vectorizer.pickle')
X = joblib.load('./keys_responses.pickle')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Добро пожаловать')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Помощь пока недоступна')


def handle_response(text: str) -> str:
    user_message = text.lower()
    user_query_splited = user_message.split()
    final_query = []
    for word in user_query_splited:
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

    app = Application.builder().token(constants.API_KEY).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Bot polling')
    app.run_polling(poll_interval=3)
