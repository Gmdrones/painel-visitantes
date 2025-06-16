from flask import Flask, render_template, request, redirect, session, send_file, url_for
import sqlite3
from datetime import datetime
import os
from waitress import serve

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

# Cria o banco de dados e a tabela
DB_FILE = 'visitantes.db'
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT UNIQUE,
            identidade TEXT UNIQUE,
            placa TEXT,
            bloco TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Rota de Login ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # lógica do login
        ...
    return render_template("login.html")
    msg = ""
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == 'porteiro' and senha == '1234':
            session['usuario'] = 'porteiro'
            return redirect('/painel')
        elif usuario == 'admin' and senha == 'admin':
            session['usuario'] = 'admin'
            return redirect('/painel')
        else:
            msg = 'Usuário ou senha incorretos.'
    return render_template('login.html', msg=msg)

# --- Painel Principal ---
@app.route('/painel', methods=['GET'])
def painel():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('index.html', usuario=session['usuario'])

# --- Cadastro ---
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if 'usuario' not in session:
        return redirect('/')

    try:
        dados = (
            request.form['nome'],
            request.form['cpf'],
            request.form['identidade'],
            request.form['placa'],
            request.form['bloco']
        )

        # Validações básicas
        cpf = dados[1]
        placa = dados[3]
        if cpf and not cpf.count('.') == 2 or '-' not in cpf:
            raise ValueError("CPF inválido. Use o formato 123.456.789-00 ou deixe em branco.")
        if placa and not (len(placa) == 8 and '-' in placa):
            raise ValueError("Placa inválida. Use ABC-1234 ou ABC-1D34 ou deixe em branco.")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visitantes (nome, cpf, identidade, placa, bloco)
            VALUES (?, ?, ?, ?, ?)
        ''', dados)
        conn.commit()
        conn.close()
        return render_template('index.html', sucesso="Cadastro realizado com sucesso!", usuario=session['usuario'])

    except sqlite3.IntegrityError as e:
        erro = "CPF ou Identidade já cadastrados."
    except ValueError as e:
        erro = str(e)
    except Exception:
        erro = "Erro no cadastro."

    return render_template('index.html', erro=erro, usuario=session['usuario'])

# --- Busca ---
@app.route('/buscar', methods=['POST'])
def buscar():
    if 'usuario' not in session:
        return redirect('/')
    termo = request.form['termo']
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM visitantes
        WHERE nome LIKE ? OR cpf LIKE ? OR identidade LIKE ?
        ORDER BY data_hora DESC LIMIT 5
    ''', (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
    resultados = cursor.fetchall()
    conn.close()
    return render_template('index.html', resultados=resultados, usuario=session['usuario'])

# --- Download do banco ---
@app.route('/download')
def download():
    if 'usuario' in session and session['usuario'] == 'admin':
        return send_file(DB_FILE, as_attachment=True)
    return redirect('/')

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- Executar no Render ---
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=10000)
