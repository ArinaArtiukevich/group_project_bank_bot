FROM python:slim

WORKDIR /frontend

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY .env /tmp/.env

ENV $(cat /tmp/.env | xargs)

RUN rm /tmp/.env

COPY . .

CMD ["python", "telegram_bot.py"]