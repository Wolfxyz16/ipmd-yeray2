import mysql.connector
from pyhive import hive

hive_conn = None 
mariadb_conn = None

while hive_conn == None and mariadb_conn == None:
    # Conectar a Hive
    try:
        hive_conn = hive.Connection(host="hive-server", port=10000, database="ipmd")
        mariadb_conn = mysql.connector.connect(
            host="mariadb",
            user="wolfxyz",
            password="wolfxyz",
            database="ipmd"
        )
        cursor_hive = hive_conn.cursor()
        cursor_mariadb = mariadb_conn.cursor()


cursor_mariadb.execute("USE ipmd;")

# Crear tabla en MariaDB si no existe
cursor_mariadb.execute("""
    CREATE TABLE IF NOT EXISTS summary (
        country VARCHAR(255) PRIMARY KEY,
        user_count INT NOT NULL
    )
""")

# Insertar datos en MariaDB (evitando duplicados)
for row in cursor_hive.fetchall():
    cursor_mariadb.execute("""
        INSERT INTO summary (country, user_count)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE user_count = VALUES(user_count)
    """, row)

# Confirmar cambios
mariadb_conn.commit()
print("✅ Datos exportados de Hive a MariaDB correctamente.")

# Cerrar conexiones
cursor_hive.close()
cursor_mariadb.close()
hive_conn.close()
mariadb_conn.close()

# Salimos del script, success
exit(0)
