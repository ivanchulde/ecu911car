from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    'host': 'db',  # nombre del servicio en docker-compose
    'port': 5432,
    'dbname': 'VehiculosDB',
    'user': 'admin',
    'password': 'p.7891011'
}


def buscar_placa(placa_buscar):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                query = """
                SELECT id, nombres, cedula, institucion, cargo, placa, marca, modelo, tipo, color
                FROM vehiculosecu911
                WHERE UPPER(placa) = UPPER(%s)
                """
                cur.execute(query, (placa_buscar,))
                return cur.fetchone()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        placa = request.form["placa"]
        resultado = buscar_placa(placa)
    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
