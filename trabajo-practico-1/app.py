from flask import Flask, request
import mysql.connector
from prometheus_flask_exporter import PrometheusMetrics

# mariadb config
config = {
    'host': 'mariadb',
    'port': 3306,
    'user': 'wolfxyz',
    'password': 'wolfxyz',
    'database': 'ipmd',
}

# Leemos el id del contenedor. Esta en el archivo /etc/hostname
try:
    with open('/etc/hostname', 'r') as f:
        container_id = f.read().strip()
except Exception as e:
    container_id = ""

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.get("/")
def hello():
    return f'{{"Message": "Hello from {container_id}. Proyecto de ipmd de yeray2"}}'

@app.get("/data")
def get_database():
    """
    El servidor devuelve el contenido completo de la BD, en formato JSON
    """
    # Hacemos la conexion con la base de datos
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception as e:
        return '{"message": "Can not connect to the database. Maybe wait for a few seconds..."}'

    # Execute a SQL statement and fetch de data
    cur.execute("SELECT * FROM messages")
    messages = cur.fetchall()

    # Close the connection
    cur.close()
    conn.close()

    return messages

@app.get("/data/<int:id>")
def get_id(id):
    """
    El servidor devuelve el registro de la BD identificado por int, en formato JSON
    """
    # Hacemos la conexion con la base de datos
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception as e:
        return '{"message": "Can not connect to the database. Maybe wait for a few seconds..."}'

    # Execute a SQL statement and fetch de data
    cur.execute(f"SELECT * FROM messages WHERE clid={id}")
    message = cur.fetchall()

    # Close the connection
    cur.close()
    conn.close()

    return message

@app.post("/data")
def post_message():
    """
    El servidor inserta un registro en la BD. La petición debe incluir datos en JSON con el contenido del registro, enriquecido con el nombre del servidor. 
    El campo "clid" es clave y debe ser único. El servidor devolverá un mensaje de éxito/error
    """
    # Capturamos la variable que recibimos por POST
    message = request.get_json()
    clid = message['clid']
    mess = message['mess']
    
    # Comprobamos que el mensaje tenga las keys que nos interesa
    must_have_keys = {"clid", "mess"}
    recived_keys = set(message.keys())
    if not recived_keys.issubset(must_have_keys):
        return {"message": "Message has an invalid format. Must have only clid and mess"}

    # Comprobamos que el id sea un numero
    try:
        int(message['clid'])
    except Exception as e:
        return {"message": "clid is not a valid id. Only integer numbers"}

    # Hacemos la conexion con la base de datos
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception as e:
        return '{"message": "Can not connect to the database. Maybe wait for a few seconds..."}'

    # Ejecutamos la consulta SQL
    try:
        cur.execute(f"INSERT INTO messages VALUES ({clid}, \"{mess}\", \"{container_id}\")")
    except mysql.connector.IntegrityError as e:
        return {"error": "Integrity error, duplicated id"}

    # Realizamos los cambios
    conn.commit()

    # Cerramos la conexion
    cur.close()
    conn.close()

    return {"message": "Message added succesfully"}

@app.put("/data/<int:id>")
def update_message(id):
    """
    El servidor modifica el registro con "clid" = int en la BD. La petición debe incluir datos en JSON con el nuevo contenido del campo "mess".
    El servidor devolverá un mensaje de éxito/error.
    """
    # Comprobamos que solo haya una key y que sea de nombre mess
    message = request.get_json()
    if "mess" not in message.keys() and message.keys() == 1:
        return {"message": "Message has an invalid format. Must have only mess"}

    new_mess = message['mess']

    # Hacemos la conexion con la base de datos
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception as e:
        return '{"message": "Can not connect to the database. Maybe wait for a few seconds..."}'

    # Ejecutamos la consulta SQL
    try:
        cur.execute(f"UPDATE messages SET mess='{new_mess}' WHERE clid='{id}'")
    except mysql.connector.IntegrityError as e:
        return {"error": "Integrity error, id not found"}

    # Realizamos los cambios
    conn.commit()

    # Cerramos la conexion
    cur.close()
    conn.close()

    return {"message": "Data updated successfully"}

@app.delete("/data/<int:id>")
def delete_message(id):
    """
    El servidor elimina el registro con "clid" = int en la BD. El servidor devolverá un mensaje de éxito/error.
    """
    # Hacemos la conexion con la base de datos
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
    except Exception as e:
        return '{"message": "Can not connect to the database. Maybe wait for a few seconds..."}'

    # Ejecutamos la consulta SQL
    try:
        cur.execute(f"DELETE FROM messages WHERE clid={id}")
    except mysql.connector.IntegrityError as e:
        return {"error": "Integrity error, id not found"}

    # Realizamos los cambios
    conn.commit()

    # Cerramos la conexion
    cur.close()
    conn.close()

    return {"message": "Data deleted successfully"}

@app.route('/metrics')
def metrics_endpoint():
    return metrics

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
