from flask import Flask, render_template, request, redirect, session, send_file, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Banco de dados de visitantes
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

# Dados de login (exemplo fixo - ideal seria usar hash + banco separado)
USUARIOS = {
    'porteiro': {'senha': '1234', 'perfil': 'porteiro'},
    'admin': {'senha': 'admin123', 'perfil': 'admin'}
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def fazer_login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    user = USUARIOS.get(usuario)
    if user and user['senha'] == senha:
        session['usuario'] = usuario
        session['perfil'] = user['perfil']
        if user['perfil'] == 'admin':
            return redirect('/admin')
        else:
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
    if session.get('perfil') != 'porteiro':
        return redirect('/')
    return render_template('index.html')

@app.route('/admin')
def admin():
    if session.get('perfil') != 'admin':
        return redirect('/')
    return render_template('admin.html')

@app.route('/download')
def download():
    if session.get('perfil') != 'admin':
        return redirect('/')
    return send_file('visitantes.db', as_attachment=True)

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if session.get('perfil') != 'porteiro':
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
    except Exception:
        flash('Erro no cadastro.')
    return redirect('/painel')

@app.route('/buscar', methods=['POST'])
def buscar():
    if session.get('perfil') != 'porteiro':
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

# Render utiliza o waitress
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=10000)


# === DEPLOY ===
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
