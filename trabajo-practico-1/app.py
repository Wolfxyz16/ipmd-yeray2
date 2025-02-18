from flask import Flask
import json
import mariadb

# mariadb config
config = {
    'host': '172.19.0.3',
    'port': 3306,
    'user': 'wolfxyz',
    'password': 'wolfxyz',
    'database': 'ipmd'
}

app = Flask(__name__)

@app.get("/")
def hello():
    return "Hola mundo, desde docker-compose!"

@app.get("/data")
def get_database():
    # connection for MariaDB
    conn = mariadb.connect(**config)
    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute("SELECT * FROM messages")

    # serialize results into JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))

    # return the results!
    return json.dumps(json_data)

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
    app.run(host="0.0.0.0", port=5000)
