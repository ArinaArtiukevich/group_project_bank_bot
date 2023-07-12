import datetime
from typing import List

import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Query
from fastapi_utils.tasks import repeat_every

from telegram_bot.modules.currency import CurrencyParsing, CurrencyExchange

app = FastAPI()


@app.on_event("startup")
def parse_currency():
    currency_parsing = CurrencyParsing()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        currency_parsing.create_currency_dataframe,
        "interval",
        seconds=60,
        start_date=datetime.datetime(2023, 7, 12, 17, 58, 0)
    )
    scheduler.start()


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
