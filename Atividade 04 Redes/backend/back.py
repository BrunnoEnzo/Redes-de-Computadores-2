from flask import Flask, request, jsonify
import sqlite3
import os
from sqlite3 import Error

app = Flask(__name__)
DATABASE = 'devices.db'

def create_connection():
    """Cria uma conexão com o banco de dados SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return conn

def verify_database():
    """Verifica e prepara o banco de dados com a estrutura correta"""
    db_exists = os.path.exists(DATABASE)
    conn = create_connection()
    
    if conn is not None:
        cursor = conn.cursor()
        
        try:
            # Verifica se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Verifica a estrutura da tabela
                cursor.execute("PRAGMA table_info(devices)")
                columns = cursor.fetchall()
                expected_columns = {
                    'id': 'INTEGER',
                    'ip': 'TEXT',
                    'name': 'TEXT',
                    'traffic_rate': 'REAL'
                }
                
                current_columns = {col[1]: col[2] for col in columns}
                
                if current_columns != expected_columns:
                    # Se a estrutura for diferente, recria a tabela
                    print("Estrutura da tabela incorreta. Recriando tabela...")
                    cursor.execute("DROP TABLE devices")
                    create_table(conn)
            else:
                # Se a tabela não existe, cria
                create_table(conn)
        except Error as e:
            print(f"Erro ao verificar estrutura do banco: {e}")
            create_table(conn)
        finally:
            conn.close()
    else:
        print("Não foi possível conectar ao banco de dados")

def create_table(conn):
    """Cria a tabela devices com a estrutura correta"""
    try:
        sql = '''CREATE TABLE devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    name TEXT NOT NULL,
                    traffic_rate REAL NOT NULL
                );'''
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print("Tabela 'devices' criada com sucesso.")
    except Error as e:
        print(f"Erro ao criar tabela: {e}")

# Endpoints da API
@app.route('/devices', methods=['POST'])
def add_device():
    data = request.get_json()
    
    required_fields = ['ip', 'name', 'traffic_rate']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO devices (ip, name, traffic_rate) VALUES (?, ?, ?)",
            (data['ip'], data['name'], data['traffic_rate'])
        )
        conn.commit()
        device_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'id': device_id,
            'ip': data['ip'],
            'name': data['name'],
            'traffic_rate': data['traffic_rate']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip, name, traffic_rate FROM devices")
        devices = cursor.fetchall()
        conn.close()
        
        devices_list = [{
            'id': device[0],
            'ip': device[1],
            'name': device[2],
            'traffic_rate': device[3]
        } for device in devices]
            
        return jsonify(devices_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM devices WHERE id = ?", (device_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Dispositivo não encontrado'}), 404
            
        cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Dispositivo removido com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    verify_database()
    app.run(host='0.0.0.0', port=5000)