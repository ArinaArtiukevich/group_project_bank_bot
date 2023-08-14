import numpy as np
import pymorphy2
import joblib
import datetime
import uvicorn
from typing import List


from pydantic import BaseModel
from fastapi import FastAPI, Query
from sklearn.metrics.pairwise import cosine_similarity
from modules.finding_nearest_ATM_Minsk import nearest_atm
from apscheduler.schedulers.background import BackgroundScheduler
from modules.currency import CurrencyParsing, CurrencyExchange


morpher = pymorphy2.MorphAnalyzer()
key_lemmas_vectors = joblib.load('./utilities/lemmas.pickle')
vectorizer = joblib.load('./utilities/vectorizer.pickle')
X = joblib.load('./utilities/keys_responses.pickle')

app = FastAPI()

# @app.on_event("startup")
# def parse_currency():
#     currency_parsing = CurrencyParsing()
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(
#         currency_parsing.create_currency_dataframe,
#         "interval",
#         seconds=60,
#         start_date=datetime.datetime(2023, 7, 12, 17, 58, 0)
#     )
#     scheduler.start()


# todo same but only seconds param is available
# todo function must be async
# @app.on_event("startup")
# @repeat_every(seconds=60 * 60 * 24)
# async def parse_currency():
#     await currency_parsing.create_currency_dataframe()
#

@app.get("/currency/BYN")
async def exchange_byn(currency_to: List[str] | None = Query(), exchange_way: List[str] | None = Query()):
    currency_exchange = CurrencyExchange()
    currency_exchange.read_dataframe_csv()
    currency_exchange.df_expand_conversion()
    df = currency_exchange.get_currency_exchange(
        currency_from=np.array(currency_to),
        exchange_way=np.array(exchange_way),
    )
    response = currency_exchange.df_prettifier(df)
    return response.encode('utf-8')


@app.get("/currency/conversion")
async def exchange_byn(currency_to: List[str] | None = Query(), exchange_way: List[str] | None = Query(),
                       currency_from: List[str] | None = Query()):
    currency_exchange = CurrencyExchange()
    currency_exchange.read_dataframe_csv()
    currency_exchange.df_expand_conversion()
    df = currency_exchange.get_currency_exchange(
        currency_from=np.array(currency_from),
        aim=np.array(['sell']),
        exchange_way=np.array(exchange_way),
        currency_to=np.array(currency_to)
    )
    response = currency_exchange.df_prettifier(df)
    return response.encode('utf-8')

@app.get("/respond_on_question/{txt}")
async def respond_on_question(txt: str):
    user_message = txt.lower()
    user_query_splited = user_message.split()
    final_query = []
    for word in user_query_splited:
        final_query.append(morpher.parse(word)[0].normal_form)
    user_query_vector = vectorizer.transform([' '.join(map(str, final_query))])
    similarity_scores = cosine_similarity(key_lemmas_vectors, user_query_vector)
    most_similar_index = similarity_scores.argmax()
    return X['Response'].iloc[most_similar_index].encode('utf-8')

class Address(BaseModel):
    address: str

@app.post("/find")
def find_nearest(request: Address):
    response = nearest_atm(request.address)
    return response.encode('utf-8')

if __name__ == "__main__":
    uvicorn.run("fast_api:app", host="127.0.0.1", port=8000, log_level="info")