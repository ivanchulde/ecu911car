from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2

app = Flask(__name__)
app.secret_key = "clave_secreta_aqui"  # importante para sesiones

DB_CONFIG = {
    'host': 'db',
    'port': 5432,
    'dbname': 'VehiculosDB',
    'user': 'admin',
    'password': 'p.7891011'
}

# Función de búsqueda
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

# Página de login
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")

        if not usuario or not clave:
            error = "Ingrese usuario y contraseña"
        elif usuario == "admin" and clave == "1234":
            session["usuario"] = usuario
            return redirect(url_for("index"))
        else:
            error = "Usuario o contraseña incorrectos"
    
    return render_template("login.html", error=error)

# Página de búsqueda (solo accesible si se ha hecho login)
@app.route("/index", methods=["GET", "POST"])
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))

    resultado = None
    if request.method == "POST":
        placa = request.form["placa"]
        resultado = buscar_placa(placa)
    return render_template("index.html", resultado=resultado)

# Logout
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
