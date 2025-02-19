from flask import Flask
import mysql.connector
import json

# mariadb config
config = {
    # 'host': 'mariadb',
    'host': '172.18.0.3',
    'port': 3306,
    'user': 'wolfxyz',
    'password': 'wolfxyz',
    'database': 'ipmd',
}

app = Flask(__name__)

@app.get("/")
def hello():
    return '{""Message": "Proyecto de ipmd de yeray2"}'

@app.get("/data")
def get_database():
    """
    El servidor devuelve el contenido completo de la BD, en formato JSON
    """
    # Connection for MariaDB
    conn = mysql.connector.connect(**config)
    # Create a connection cursor
    cur = conn.cursor()
    # Execute a SQL statement and fetch de data
    cur.execute("SELECT * FROM messages")
    messages = cur.fetchall()
    # Close the connection
    cur.close()
    conn.close()
    # return the results!
    return str(json.dump(messages))

@app.get("/data/<int:id>")
def get_id(id):
    """
    El servidor devuelve el registro de la BD identificado por int, en formato JSON
    """
    # Connection for MariaDB
    conn = mysql.connector.connect(**config)
    # Create a connection cursor
    cur = conn.cursor()
    # Execute a SQL statement and fetch de data
    cur.execute(f"SELECT * FROM messages WHERE clid={id}")
    message = cur.fetchall()
    # Close the connection
    cur.close()
    conn.close()
    # return the results!
    return str(json.dump(messages))

@app.post("/data/<int:id>")
def post_message(id):
    """
    El servidor inserta un registro en la BD. La petición debe incluir datos en JSON con el contenido del registro, enriquecido con el nombre del servidor. 
    El campo "clid" es clave y debe ser único. El servidor devolverá un mensaje de éxito/error
    """
    return f'<p>Posting {id} post...</p>'

@app.put("/data/<int:id>")
def update_message(id):
    """
    El servidor modifica el registro con "clid" = int en la BD. La petición debe incluir datos en JSON con el nuevo contenido del campo "mess".
    El servidor devolverá un mensaje de éxito/error.
    """
    return f'<p>Updating {id} post...</p>'

@app.delete("/data/<int:id>")
def delete_message(id):
    """
    El servidor elimina el registro con "clid" = int en la BD. El servidor devolverá un mensaje de éxito/error.
    """
    return f'<p>Deleting {id} post...</p>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
