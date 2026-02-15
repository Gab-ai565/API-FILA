import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB = 'fila.db'

# Criar tabela com tipo
def criar_tabela():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS fila (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

criar_tabela()

# Helpers
def adicionar_item(item, tipo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO fila (item, tipo) VALUES (?, ?)", (item, tipo))
    conn.commit()
    conn.close()

def remover_item(tipo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, item FROM fila WHERE tipo=? ORDER BY id ASC LIMIT 1", (tipo,))
    row = c.fetchone()
    if row:
        c.execute("DELETE FROM fila WHERE id = ?", (row[0],))
        conn.commit()
    conn.close()
    return row

def listar_fila(tipo=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if tipo:
        c.execute("SELECT id, item, tipo FROM fila WHERE tipo=? ORDER BY id ASC", (tipo,))
    else:
        c.execute("SELECT id, item, tipo FROM fila ORDER BY tipo, id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "item": r[1], "tipo": r[2]} for r in rows]

# Rotas
@app.route('/enqueue', methods=['POST'])
def enqueue():
    data = request.json
    item = data.get('item')
    tipo = data.get('tipo')
    if not item or not tipo:
        return jsonify({"error": "Item ou tipo não fornecido"}), 400
    adicionar_item(item, tipo)
    return jsonify({"message": f"Item '{item}' adicionado à fila '{tipo}'", "fila": listar_fila(tipo)})

@app.route('/dequeue', methods=['POST'])
def dequeue():
    tipo = request.json.get('tipo')
    if not tipo:
        return jsonify({"error": "Tipo não fornecido"}), 400
    row = remover_item(tipo)
    if not row:
        return jsonify({"error": f"Fila '{tipo}' vazia"}), 400
    return jsonify({"message": f"Item '{row[1]}' removido da fila '{tipo}'", "fila": listar_fila(tipo)})

@app.route('/fila', methods=['GET'])
def ver_fila():
    tipo = request.args.get('tipo')
    return jsonify({"fila": listar_fila(tipo)})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)	
