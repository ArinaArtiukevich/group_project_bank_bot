# todo delete uvicorn fast_api:app --reload --port 9000
import numpy as np
from fastapi import FastAPI, Query, Response
from modules.currency import CurrencyParsing, CurrencyExchange
from typing import List

app = FastAPI()


# todo causes error Unresolved reference for variables
# @app.on_event("startup")
# async def startup_event():
    # currency_parsing = CurrencyParsing()
    # currency_exchange = CurrencyExchange()
    # currency_exchange.read_dataframe_csv()
    # currency_exchange.df_expand_conversion()


@app.get("/currency/uploaded_currency")
async def parse_currency():
    currency_parsing = CurrencyParsing()
    df = currency_parsing.create_currency_dataframe()
    return Response(df.to_json(orient="records"), media_type="application/json")


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
