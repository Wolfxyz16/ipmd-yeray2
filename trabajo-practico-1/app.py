from flask import Flask
import mysql.connector

# mariadb config
config = {
    # 'host': 'mariadb',
    'host': '172.18.0.3',
    'port': 3306,
    'user': 'wolfxyz',
    'password': 'wolfxyz',
    'database': 'ipmd',
}

"""
Ya se porque no se conecta, el servidor de mariadb tarda un poco en iniciar y a flask no le da tiempo a conectarse
si lo dejas ejecutando unos segundos veras que empieza a hacer conexiones correctas
"""
while True:
    try:
        # Establecer conexión
        conn = mysql.connector.connect(**config)
    
        if conn.is_connected():
            print("✅ Conexión exitosa a MariaDB")

            # Crear un cursor
            cursor = conn.cursor()

            # Ejecutar una consulta
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
        
            # Mostrar las tablas disponibles
            for table in tables:
                print(table)

            # Cerrar la conexión
            cursor.close()
            conn.close()
            print("✅ Conexión cerrada correctamente")

    except mysql.connector.Error as e:
        print(f"❌ Error al conectar a MariaDB: {e}")

app = Flask(__name__)

@app.get("/")
def hello():
    return "Hola mundo, desde docker-compose!"

@app.get("/data")
def get_database():
    # # connection for MariaDB
    # conn = mariadb.connect(**config)
    # # create a connection cursor
    # cur = conn.cursor()
    # # execute a SQL statement
    # cur.execute("SELECT * FROM messages")
    #
    # # serialize results into JSON
    # row_headers=[x[0] for x in cur.description]
    # rv = cur.fetchall()
    # json_data = []
    # for result in rv:
    #     json_data.append(dict(zip(row_headers,result)))
    #
    # # return the results!
    # return json.dumps(json_data)
    return "hola"

@app.get("/data/<int:id>")
def get_id(id):
    return f'<p>Getting {id} post...</p>'

@app.post("/data/<int:id>")
def post_message(id):
    return f'<p>Posting {id} post...</p>'

@app.put("/data/<int:id>")
def update_message(id):
    return f'<p>Updating {id} post...</p>'

@app.delete("/data/<int:id>")
def delete_message(id):
    return f'<p>Deleting {id} post...</p>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
