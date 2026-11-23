# Agenda & Finanças da Manicure 💅
Flask + SQLite, feito para celular.

## Rodar
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Abra http://localhost:5000 (no celular: http://IP-DO-PC:5000 na mesma rede).
O banco `manicure.db` é criado sozinho, já com os 8 serviços cadastrados.
Para publicar: defina a variável `SECRET_KEY` e use um servidor como gunicorn (`gunicorn app:app`).
