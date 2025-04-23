FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requerimentos.txt

EXPOSE 5000 8501

CMD ["sh", "start.sh"]
