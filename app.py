from flask import Flask, render_template, request, redirect, session, send_file, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'segredo-super-seguro'

# === CONFIGURAÇÕES DE USUÁRIOS ===
USUARIOS = {
    'porteiro': {'senha': '1234', 'tipo': 'porteiro'},
    'admin': {'senha': 'admin123', 'tipo': 'admin'}
}

# === BANCO DE DADOS ===
def init_db():
    conn = sqlite3.connect('visitantes.db')
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

# === ROTAS ===
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def fazer_login():
    usuario = request.form['usuario']
    senha = request.form['senha']

    if usuario in USUARIOS and USUARIOS[usuario]['senha'] == senha:
        session['usuario'] = usuario
        session['tipo'] = USUARIOS[usuario]['tipo']
        if session['tipo'] == 'admin':
            return redirect('/admin')
        return redirect('/painel')
    else:
        flash('Usuário ou senha incorretos.')
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/painel')
def painel():
    if 'usuario' not in session or session['tipo'] != 'porteiro':
        return redirect('/')
    return render_template('index.html')

@app.route('/admin')
def admin():
    if 'usuario' not in session or session['tipo'] != 'admin':
        return redirect('/')
    return render_template('admin.html')

@app.route('/download')
def download():
    if 'usuario' in session and session['tipo'] == 'admin':
        return send_file('visitantes.db', as_attachment=True)
    return redirect('/')

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
        conn = sqlite3.connect('visitantes.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visitantes (nome, cpf, identidade, placa, bloco)
            VALUES (?, ?, ?, ?, ?)
        ''', dados)
        conn.commit()
        conn.close()
        flash('Cadastro realizado com sucesso.')
    except sqlite3.IntegrityError as e:
        if 'cpf' in str(e):
            flash('CPF já cadastrado.')
        elif 'identidade' in str(e):
            flash('Identidade já cadastrada.')
        else:
            flash('Erro no cadastro.')
    return redirect('/painel')

@app.route('/buscar', methods=['POST'])
def buscar():
    if 'usuario' not in session:
        return redirect('/')
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

# === DEPLOY ===
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
