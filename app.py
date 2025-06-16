from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Cria o banco de dados e a tabela, se ainda não existir
def init_db():
    conn = sqlite3.connect('visitantes.db')
    cursor = conn.cursor()
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = (
        request.form['nome'],
        request.form['cpf'],
        request.form['identidade'],
        request.form['placa'],
        request.form['bloco'],
        request.form['apartamento'],
        request.form['morador']
    )
    conn = sqlite3.connect('visitantes.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO visitantes (nome, cpf, identidade, placa, bloco, apartamento, morador)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', dados)
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/buscar', methods=['POST'])
def buscar():
    termo = request.form['termo']
    conn = sqlite3.connect('visitantes.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM visitantes
        WHERE nome LIKE ? OR cpf LIKE ? OR identidade LIKE ?
        ORDER BY data_hora DESC LIMIT 5
    ''', (f'%{termo}%', f'%{termo}%', f'%{termo}%'))
    resultados = cursor.fetchall()
    conn.close()
    return render_template('index.html', resultados=resultados)

# Para uso no Render
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
