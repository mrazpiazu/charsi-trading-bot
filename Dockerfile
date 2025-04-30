FROM python:3.12

#COPY requirements.txt requirements.txt
#COPY main.py main.py
#COPY utils utils
#COPY logs logs
#COPY .env .env

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]