import os, sqlite3, json
from datetime import date, datetime, timedelta
from flask import Flask, g, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave")
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manicure.db")

# nome, preço, custo direto, horas que leva (edite na tela Serviços)
PADRAO = [
    ("Alongamento em gel — Molde F1", 100, 9, 2.5),
    ("Alongamento em gel — Tips", 110, 9.4, 2.5),
    ("Blindagem", 80, 7, 2),
    ("Esmaltação em gel", 60, 7.5, 1.5),
    ("Pedicure com esmaltação em Gel", 60, 10, 1.5),
    ("Manutenção", 70, 5, 2),
    ("ALONGAMENTO FIBRA DE VIDRO", 120, 11, 3),
    ("POSTIÇA REALISTA", 80, 9.5, 2),
]
SCHEMA = """
CREATE TABLE IF NOT EXISTS servicos(id INTEGER PRIMARY KEY, nome TEXT, preco REAL, custo REAL, horas REAL DEFAULT 1, ativo INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY, nome TEXT, contato TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS agendamentos(id INTEGER PRIMARY KEY, cliente_id INT, servico_id INT, data TEXT, hora TEXT,
  preco REAL, custo REAL, horas REAL, status TEXT DEFAULT 'agendado', obs TEXT);
CREATE TABLE IF NOT EXISTS despesas(id INTEGER PRIMARY KEY, data TEXT, descricao TEXT, valor REAL);
CREATE TABLE IF NOT EXISTS config(chave TEXT PRIMARY KEY, valor TEXT);
"""

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close(_):
    d = g.pop("db", None)
    if d: d.close()

def init_db():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    if not c.execute("SELECT 1 FROM servicos").fetchone():
        c.executemany("INSERT INTO servicos(nome,preco,custo,horas) VALUES(?,?,?,?)", PADRAO)
    c.execute("INSERT OR IGNORE INTO config VALUES('pct_salario','60')")
    c.commit(); c.close()

@app.template_filter("brl")
def brl(v):
    return "R$ " + f"{(v or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
@app.template_filter("dia_br")
def dia_br(s):
    d = date.fromisoformat(s)
    return f"{DIAS[d.weekday()]}, {d:%d/%m}"

@app.template_filter("fim")
def fim(a):
    t = datetime.strptime(a["hora"], "%H:%M") + timedelta(hours=a["horas"] or 0)
    return t.strftime("%H:%M")

# ---------- INÍCIO ----------
@app.route("/")
def inicio():
    off = int(request.args.get("s", 0))
    ini = date.today() - timedelta(days=date.today().weekday()) + timedelta(weeks=off)
    f = ini + timedelta(days=6)
    rows = db().execute("""SELECT a.*, c.nome cliente, c.contato, s.nome servico FROM agendamentos a
        JOIN clientes c ON c.id=a.cliente_id JOIN servicos s ON s.id=a.servico_id
        WHERE a.data BETWEEN ? AND ? ORDER BY a.data, a.hora""", (ini.isoformat(), f.isoformat())).fetchall()
    dias = {}
    for i in range(7):
        dias[(ini + timedelta(days=i)).isoformat()] = []
    for r in rows: dias[r["data"]].append(r)
    return render_template("inicio.html", dias=dias, ini=ini, f=f, off=off, hoje=date.today().isoformat())

@app.post("/status/<int:i>/<st>")
def status(i, st):
    if st in ("agendado", "concluido", "cancelado"):
        db().execute("UPDATE agendamentos SET status=? WHERE id=?", (st, i)); db().commit()
    return redirect(request.referrer or url_for("inicio"))

# ---------- SERVIÇOS ----------
@app.route("/servicos")
def servicos():
    return render_template("servicos.html", lista=db().execute("SELECT * FROM servicos WHERE ativo=1 ORDER BY nome").fetchall())

@app.post("/servicos/salvar")
def servico_salvar():
    f = request.form
    v = lambda k: float((f.get(k) or "0").replace(",", "."))
    if f.get("id"):
        db().execute("UPDATE servicos SET nome=?,preco=?,custo=?,horas=? WHERE id=?",
                     (f["nome"], v("preco"), v("custo"), v("horas"), f["id"]))
    else:
        db().execute("INSERT INTO servicos(nome,preco,custo,horas) VALUES(?,?,?,?)", (f["nome"], v("preco"), v("custo"), v("horas")))
    db().commit(); flash("Serviço salvo ✨")
    return redirect(url_for("servicos"))

@app.post("/servicos/<int:i>/excluir")
def servico_excluir(i):  # só desativa, para não quebrar o histórico
    db().execute("UPDATE servicos SET ativo=0 WHERE id=?", (i,)); db().commit()
    return redirect(url_for("servicos"))

# ---------- AGENDAR ----------
@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    d = db()
    if request.method == "POST":
        f = request.form
        nome, contato = f["nome"].strip(), f["contato"].strip()
        cli = d.execute("SELECT id FROM clientes WHERE contato=?", (contato,)).fetchone()
        if cli:
            cid = cli["id"]; d.execute("UPDATE clientes SET nome=? WHERE id=?", (nome, cid))
        else:
            cid = d.execute("INSERT INTO clientes(nome,contato) VALUES(?,?)", (nome, contato)).lastrowid
        s = d.execute("SELECT * FROM servicos WHERE id=?", (f["servico_id"],)).fetchone()
        d.execute("INSERT INTO agendamentos(cliente_id,servico_id,data,hora,preco,custo,horas,obs) VALUES(?,?,?,?,?,?,?,?)",
                  (cid, s["id"], f["data"], f["hora"], s["preco"], s["custo"], s["horas"], f.get("obs")))
        d.commit(); flash("Agendamento salvo 💖")
        return redirect(url_for("inicio"))
    clientes = [dict(r) for r in d.execute("SELECT * FROM clientes ORDER BY nome")]
    pre = d.execute("SELECT * FROM clientes WHERE id=?", (request.args.get("cliente"),)).fetchone()
    return render_template("agendar.html", clientes=clientes, cj=json.dumps(clientes), pre=pre,
                           pre_serv=request.args.get("servico", type=int), hoje=date.today().isoformat(),
                           servicos=d.execute("SELECT * FROM servicos WHERE ativo=1 ORDER BY nome").fetchall())

# ---------- FINANÇAS ----------
def periodo():
    p, h = request.args.get("p", "mes"), date.today()
    if p == "semana": ini = h - timedelta(days=h.weekday()); fim_ = ini + timedelta(days=6)
    elif p == "ano": ini, fim_ = date(h.year, 1, 1), date(h.year, 12, 31)
    elif p == "custom":
        try: ini, fim_ = date.fromisoformat(request.args["ini"]), date.fromisoformat(request.args["fim"])
        except Exception: ini, fim_ = h.replace(day=1), h
    else:
        p = "mes"; ini = h.replace(day=1)
        fim_ = (ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return p, ini.isoformat(), fim_.isoformat()

def resumo(ini, fim_):
    d = db()
    r = d.execute("SELECT COALESCE(SUM(preco),0) rec, COALESCE(SUM(custo),0) cus, COUNT(*) n FROM agendamentos WHERE status='concluido' AND data BETWEEN ? AND ?", (ini, fim_)).fetchone()
    desp = d.execute("SELECT COALESCE(SUM(valor),0) FROM despesas WHERE data BETWEEN ? AND ?", (ini, fim_)).fetchone()[0]
    lucro = r["rec"] - r["cus"] - desp
    pct = float(d.execute("SELECT valor FROM config WHERE chave='pct_salario'").fetchone()[0])
    sal = max(lucro, 0) * pct / 100
    rank = d.execute("""SELECT s.nome, COUNT(a.id) qtd, COALESCE(SUM(a.preco),0) total FROM servicos s
        LEFT JOIN agendamentos a ON a.servico_id=s.id AND a.status='concluido' AND a.data BETWEEN ? AND ?
        WHERE s.ativo=1 GROUP BY s.id ORDER BY qtd DESC, s.nome""", (ini, fim_)).fetchall()
    return dict(rec=r["rec"], cus=r["cus"], n=r["n"], desp=desp, lucro=lucro, pct=pct, sal=sal,
                reserva=lucro - sal if lucro > 0 else 0, rank=rank, max=max([x["qtd"] for x in rank] + [1]))

@app.route("/financas")
def financas():
    p, ini, fim_ = periodo()
    return render_template("financas.html", p=p, ini=ini, fim=fim_, r=resumo(ini, fim_))

@app.route("/caixa", methods=["GET", "POST"])
def caixa():
    d = db()
    if request.method == "POST":
        f = request.form
        if f["acao"] == "pct":
            d.execute("UPDATE config SET valor=? WHERE chave='pct_salario'", (min(max(float(f["pct"]), 0), 100),))
        elif f["acao"] == "despesa":
            d.execute("INSERT INTO despesas(data,descricao,valor) VALUES(?,?,?)", (f["data"], f["descricao"], float(f["valor"].replace(",", "."))))
        elif f["acao"] == "apagar":
            d.execute("DELETE FROM despesas WHERE id=?", (f["id"],))
        d.commit(); flash("Salvo ✨")
        return redirect(request.referrer or url_for("caixa"))
    p, ini, fim_ = periodo()
    desp = d.execute("SELECT * FROM despesas WHERE data BETWEEN ? AND ? ORDER BY data DESC", (ini, fim_)).fetchall()
    return render_template("caixa.html", p=p, ini=ini, fim=fim_, r=resumo(ini, fim_), desp=desp, hoje=date.today().isoformat())

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
