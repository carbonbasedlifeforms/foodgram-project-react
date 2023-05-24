FROM python:3.7-slim

LABEL author='Ravil Bikkulov' version=1 curse_words=42

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
