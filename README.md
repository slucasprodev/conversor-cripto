# Conversor Cripto

Conversor de criptomoedas para reais, dólares e euros. O backend em Flask guarda a chave da API da CoinGecko, e o frontend só conversa com o seu servidor.

## Rodando localmente

1. Crie e ative um ambiente virtual:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   No Mac ou Linux, use `source venv/bin/activate`.

2. Instale as dependências:

   ```
   pip install -r requirements.txt
   ```

3. Crie um arquivo chamado `.env` na pasta do projeto com:

   ```
   COINGECKO_API_KEY=sua_chave_aqui
   ```

   A chave é gratuita: crie uma conta em https://www.coingecko.com/en/api/pricing e use o plano Demo.

4. Rode o servidor:

   ```
   python app.py
   ```

5. Abra http://127.0.0.1:5000 no navegador.

## Estrutura

```
cripto-app/
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── requirements.txt
├── .gitignore
└── README.md
```

## Publicando

O projeto tem backend em Python, então precisa de um serviço que rode Python. Render e Railway têm planos gratuitos que funcionam.

1. Suba o código para o GitHub. O `.env` não vai junto, o `.gitignore` já cuida disso.
2. Crie um Web Service no serviço escolhido e conecte o repositório.
3. Em **Environment**, adicione:
   - `COINGECKO_API_KEY` com a sua chave
   - `FLASK_ENV` com `production`
4. O serviço roda `pip install -r requirements.txt` e depois `python app.py`.

## Segurança

- A chave da API fica só no servidor, nunca chega ao navegador.
- O `.gitignore` impede que `.env` e `venv/` subam para o repositório.
- Cabeçalhos de segurança em todas as respostas (`Content-Security-Policy`, `X-Frame-Options`, entre outros).
- HTTPS forçado em produção.
- Limite de 20 requisições por minuto por IP, para proteger sua cota da CoinGecko.
- O modo debug só fica ligado quando `FLASK_ENV=development`.

## Créditos

Dados de preço fornecidos pela [CoinGecko](https://www.coingecko.com).