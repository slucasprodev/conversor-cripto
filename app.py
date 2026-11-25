import os
import time
from collections import defaultdict, deque

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request

load_dotenv()

app = Flask(__name__)

IS_PRODUCTION = os.getenv("FLASK_ENV", "production") != "development"


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'"
    )
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


@app.before_request
def force_https():
    if IS_PRODUCTION and request.headers.get("X-Forwarded-Proto", "https") != "https":
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


_request_log = defaultdict(deque)
RATE_LIMIT = 20
RATE_WINDOW_SECONDS = 60


def rate_limited(ip: str) -> bool:
    now = time.time()
    log = _request_log[ip]
    while log and now - log[0] > RATE_WINDOW_SECONDS:
        log.popleft()
    if len(log) >= RATE_LIMIT:
        return True
    log.append(now)
    return False


API_KEY = os.getenv("COINGECKO_API_KEY")
API_URL = "https://api.coingecko.com/api/v3/simple/price"

MOEDAS_VALIDAS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "XRP": "ripple",
}
MOEDAS_FIAT_VALIDAS = {"BRL", "USD", "EUR"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/convert")
def convert():
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if rate_limited(client_ip):
        return jsonify({"error": "Muitas requisições. Espere um minuto e tente de novo."}), 429

    amount_raw = request.args.get("amount", "")
    try:
        amount = float(amount_raw)
    except ValueError:
        return jsonify({"error": "Quantidade inválida. Envie um número."}), 400

    if amount <= 0:
        return jsonify({"error": "A quantidade deve ser maior que zero."}), 400

    coin = request.args.get("coin", "BTC").upper()
    currency = request.args.get("currency", "BRL").upper()

    if coin not in MOEDAS_VALIDAS:
        return jsonify({"error": "Criptomoeda não suportada."}), 400
    if currency not in MOEDAS_FIAT_VALIDAS:
        return jsonify({"error": "Moeda de destino não suportada."}), 400

    if not API_KEY:
        return jsonify({"error": "Chave de API não configurada no servidor."}), 500

    coin_id = MOEDAS_VALIDAS[coin]
    currency_lower = currency.lower()
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {"ids": coin_id, "vs_currencies": currency_lower}

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        price = data[coin_id][currency_lower]
    except requests.RequestException:
        return jsonify({"error": "Erro ao consultar a API externa. Tente novamente."}), 502
    except (KeyError, TypeError):
        return jsonify({"error": "Resposta inesperada da API."}), 502

    total = amount * price

    return jsonify({
        "coin": coin,
        "currency": currency,
        "amount": amount,
        "price": round(price, 4),
        "total": round(total, 4),
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=not IS_PRODUCTION)