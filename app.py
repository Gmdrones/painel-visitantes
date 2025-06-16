from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

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
    try:
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

        # Verifica CPF
        if dados[1]:
            cursor.execute('SELECT * FROM visitantes WHERE cpf = ?', (dados[1],))
            if cursor.fetchone():
                return render_template('index.html', mensagem="CPF já cadastrado")

        # Verifica Identidade
        if dados[2]:
            cursor.execute('SELECT * FROM visitantes WHERE identidade = ?', (dados[2],))
            if cursor.fetchone():
                return render_template('index.html', mensagem="Identidade já cadastrada")

        cursor.execute('''
            INSERT INTO visitantes (nome, cpf, identidade, placa, bloco, apartamento, morador)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', dados)
        conn.commit()
        conn.close()
        return render_template('index.html', mensagem="Cadastro realizado")
    
    except Exception as e:
        print("Erro:", e)
        return render_template('index.html', mensagem="Erro no cadastro")

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

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)

