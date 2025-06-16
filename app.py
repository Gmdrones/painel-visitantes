from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime
import os
from waitress import serve

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

# Caminho do banco
DB_FILE = 'visitantes.db'

# Inicializa o banco de dados
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

# --- Página de Login ---
@app.route("/", methods=["GET", "POST"])
def login():
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

# --- Painel após login ---
@app.route("/painel", methods=["GET"])
def painel():
    if 'usuario' not in session:
        return redirect('/')
    return render_template("index.html", usuario=session['usuario'])

# --- Cadastro de visitante ---
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    if 'usuario' not in session:
        return redirect('/')

    try:
        nome = request.form['nome']
        cpf = request.form['cpf']
        identidade = request.form['identidade']
        placa = request.form['placa']
        bloco = request.form['bloco']

        # Validação CPF
        if cpf and (len(cpf) != 14 or cpf.count('.') != 2 or '-' not in cpf):
            raise ValueError("CPF inválido. Use o formato 123.456.789-00 ou deixe em branco.")

        # Validação Placa
        if placa and not (len(placa) == 8 and '-' in placa):
            raise ValueError("Placa inválida. Use ABC-1234 ou ABC-1D34 ou deixe em branco.")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visitantes (nome, cpf, identidade, placa, bloco)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, cpf, identidade, placa, bloco))
        conn.commit()
        conn.close()

        return render_template("index.html", sucesso="Cadastro realizado com sucesso!", usuario=session['usuario'])

    except sqlite3.IntegrityError as e:
        erro = "CPF já cadastrado." if "cpf" in str(e) else "Identidade já cadastrada."
    except ValueError as e:
        erro = str(e)
    except:
        erro = "Erro no cadastro."

    return render_template("index.html", erro=erro, usuario=session['usuario'])

# --- Buscar visitante ---
@app.route("/buscar", methods=["POST"])
def buscar():
    if 'usuario' not in session:
        return redirect('/')
    termo = request.form['termo']
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM visitantes
        WHERE nome LIKE ? OR cpf LIKE ? OR identidade LIKE ?
        ORDER BY data_hora DESC LIMIT 10
    ''', (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
    resultados = cursor.fetchall()
    conn.close()
    return render_template("index.html", resultados=resultados, usuario=session['usuario'])

# --- Download do banco (somente admin) ---
@app.route("/download")
def download():
    if 'usuario' in session and session['usuario'] == 'admin':
        return send_file(DB_FILE, as_attachment=True)
    return redirect('/')

# --- Logout ---
@app.ro
