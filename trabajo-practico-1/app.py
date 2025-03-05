from flask import Flask, request
import mysql.connector
from prometheus_flask_exporter import PrometheusMetrics

# Configuración de MariaDB
config = {
    'host': 'mariadb',
    'port': 3306,
    'user': 'wolfxyz',
    'password': 'wolfxyz',
    'database': 'ipmd',
}

# Leer el ID del contenedor desde /etc/hostname
try:
    with open('/etc/hostname', 'r') as f:
        container_id = f.read().strip()
except Exception:
    container_id = ""

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

@app.get("/")
def hello():
    """
    Endpoint de prueba que devuelve un mensaje con el ID del contenedor.

    Returns:
        dict: Mensaje de bienvenida con el ID del contenedor.
    """
    return {"Message": f"Hello from {container_id}. Proyecto de IPMD de Yeray2"}

@app.get("/data")
def get_database():
    """
    Obtiene todos los registros de la base de datos en formato JSON.

    Returns:
        list: Lista de registros de la tabla messages o un mensaje de error si la conexión falla.
    """
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception:
        return {"message": "Cannot connect to the database. Try again later."}

    cur.execute("SELECT * FROM messages")
    messages = cur.fetchall()
    
    cur.close()
    conn.close()
    return messages

@app.get("/data/<int:id>")
def get_id(id):
    """
    Obtiene un registro específico de la base de datos por su ID.

    Args:
        id (int): ID del registro a consultar.

    Returns:
        dict: Registro solicitado o mensaje de error si la conexión falla.
    """
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception:
        return {"message": "Cannot connect to the database. Try again later."}
    
    cur.execute(f"SELECT * FROM messages WHERE clid={id}")
    message = cur.fetchall()
    if not message:
        return {"message": "ID not found"}
    
    cur.close()
    conn.close()
    return message

@app.post("/data")
def post_message():
    """
    Inserta un nuevo registro en la base de datos.
    
    La petición debe incluir datos en formato JSON con los campos "clid" y "mess".

    Returns:
        dict: Mensaje de éxito o error según el resultado de la operación.
    """
    message = request.get_json()
    clid = message.get('clid')
    mess = message.get('mess')
    
    if not {'clid', 'mess'}.issubset(message.keys()):
        return {"message": "Invalid format. Must include only 'clid' and 'mess'"}
    
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO messages VALUES ({clid}, \"{mess}\", \"{container_id}\")")
        conn.commit()
    except mysql.connector.IntegrityError:
        return {"error": "Integrity error, duplicated ID"}
    finally:
        cur.close()
        conn.close()
    
    return {"message": "Message added successfully"}

@app.put("/data/<int:id>")
def update_message(id):
    """
    Actualiza un registro en la base de datos por su ID.
    
    La petición debe incluir un JSON con el campo "mess".

    Args:
        id (int): ID del registro a actualizar.

    Returns:
        dict: Mensaje de éxito o error según el resultado de la operación.
    """
    message = request.get_json()
    if "mess" not in message:
        return {"message": "Invalid format. Must include only 'mess'"}
    
    new_mess = message['mess']
    
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute(f"UPDATE messages SET mess='{new_mess}' WHERE clid={id}")
        conn.commit()
        if cur.rowcount == 0:
            return {"error": "No rows deleted, ID not found"}
        
    except mysql.connector.IntegrityError:
        return {"error": "Integrity error, ID not found"}
    finally:
        cur.close()
        conn.close()
    
    return {"message": "Data updated successfully"}

@app.delete("/data/<int:id>")
def delete_message(id):
    """
    Elimina un registro de la base de datos por su ID.
    
    Args:
        id (int): ID del registro a eliminar.

    Returns:
        dict: Mensaje de éxito o error según el resultado de la operación.
    """
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM messages WHERE clid={id}")
        conn.commit()
        if cur.rowcount == 0:
            return {"error": "No rows deleted, ID not found"}
        
    except mysql.connector.IntegrityError:
        return {"error": "Integrity error, ID not found"}
    finally:
        cur.close()
        conn.close()
    
    return {"message": "Data deleted successfully"}

@app.route('/metrics')
def metrics_endpoint():
    """
    Endpoint para exponer métricas de Prometheus.

    Returns:
        object: Métricas recopiladas por Prometheus.
    """
    return metrics

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
