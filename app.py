
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
conn = sqlite3.connect("visitantes.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS visitantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cpf TEXT,
    identidade TEXT,
    placa TEXT,
    bloco TEXT,
    apartamento TEXT,
    morador TEXT,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

@app.route("/")
def index():
    cursor.execute("SELECT * FROM visitantes ORDER BY data_hora DESC")
    visitantes = cursor.fetchall()
    return render_template("index.html", visitantes=visitantes)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    data = (
        request.form["nome"],
        request.form["cpf"],
        request.form["identidade"],
        request.form["placa"],
        request.form["bloco"],
        request.form["apartamento"],
        request.form["morador"]
    )
    cursor.execute("""
        INSERT INTO visitantes (nome, cpf, identidade, placa, bloco, apartamento, morador)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
