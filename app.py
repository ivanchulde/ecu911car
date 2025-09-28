from flask import Flask, render_template, request, redirect, session, url_for, Response
import psycopg2
from threading import Thread
from ultralytics import YOLO
import cv2
import pytesseract
import time


app = Flask(__name__)
app.secret_key = "clave_secreta_aqui"  # importante para sesiones

DB_CONFIG = {
    'host': 'db',
    'port': 5432,
    'dbname': 'VehiculosDB',
    'user': 'admin',
    'password': 'p.7891011'
}

#----------------------------------------FUNCIONES--------------------------------------------------------------

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
    
# Función para registrar ingreso
def registrar_ingreso(id_persona, nombres, cedula, placa):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                query = """
                INSERT INTO registro_ingresos (id_persona, nombres, cedula, placa)
                VALUES (%s, %s, %s, %s)
                """
                cur.execute(query, (id_persona, nombres, cedula, placa))
                conn.commit()
    except Exception as e:
        print(f"⚠️ Error al registrar ingreso: {str(e)}")

# Función para obtener registros de ingresos
def buscar_registro(filtro):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        query = """
        SELECT nombres, cedula, placa, fecha_hora
        FROM registro_ingresos
        WHERE UPPER(nombres) LIKE UPPER(%s)
           OR UPPER(cedula) LIKE UPPER(%s)
           OR UPPER(placa) LIKE UPPER(%s)
        ORDER BY fecha_hora DESC
        """
        filtro_param = f"%{filtro}%"
        cur.execute(query, (filtro_param, filtro_param, filtro_param))
        resultados = cur.fetchall()

        # Formatear la fecha a "YYYY-MM-DD HH:MM:SS"
        registros_formateados = []
        for r in resultados:
            nombres, cedula, placa, fecha_hora = r
            fecha_str = fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if fecha_hora else ""
            registros_formateados.append((nombres, cedula, placa, fecha_str))

        cur.close()
        conn.close()

        return registros_formateados

    except Exception as e:
        print(f"⚠️ Error al buscar registros: {str(e)}")
        return []

# ------------------------------------CAMARA OPEN CV---------------------------------------------------
model = YOLO("yolov8n.pt")  # Modelo preentrenado o custom para placas
frame_actual = None
ultima_placa = ""

# Generador de frames para Flask (solo video)
def gen_frames():
    global frame_actual
    CAMERA_URL = "rtsp://admin:Sisecu911@192.168.2.3:554/stream1"
    cap = cv2.VideoCapture(CAMERA_URL)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame_actual = cv2.resize(frame, (320, 180))  # miniatura
        ret, buffer = cv2.imencode('.jpg', frame_actual)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()


#----------------------------------------PAGINAS--------------------------------------------------------------
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

# Página de búsqueda y registro manual (solo accesible si se ha hecho login)
@app.route("/index", methods=["GET", "POST"])
def index():
    global ultima_placa
    if "usuario" not in session:
        return redirect(url_for("login"))

    resultado = None
    mensaje_buscar = None
    mensaje_manual = None

    if request.method == "POST":
        # Saber qué formulario se envió
        tipo_form = request.form.get("form_tipo")

        if tipo_form == "buscar":
            # 🔎 Búsqueda de placa
            placa = request.form.get("placa")
            resultado = buscar_placa(placa)

            if isinstance(resultado, tuple):
                # Desempaquetar datos
                id_persona, nombres, cedula, institucion, cargo, placa, marca, modelo, tipo, color = resultado
                
                # Registrar ingreso
                registrar_ingreso(id_persona, nombres, cedula, placa)

                mensaje_buscar = f"✅ Ingreso registrado para {nombres} - Placa {placa}"
            else:
                mensaje_buscar = f"❌ {resultado}"

        elif tipo_form == "manual":
            # ✍️ Registro manual
            nombres = request.form.get("nombres")
            cedula = request.form.get("cedula")
            placa = request.form.get("placa_manual")
            # Aquí llamamos a la misma función, sin repetir la conexión
            # Para registro manual no hay id_persona, podemos pasar None
            registrar_ingreso(None, nombres, cedula, placa)
            mensaje_manual = f"✅ Ingreso manual registrado para {nombres} - Placa {placa}"
            

    return render_template(
        "index2.html",
        resultado=resultado,
        mensaje_buscar=mensaje_buscar,
        mensaje_manual=mensaje_manual,
        ultima_placa=ultima_placa
    )

#PAGINA Registros de Ingreso
@app.route("/registro-ingresos", methods=["GET", "POST"])
def registro_ingresos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    filtro = ""
    if request.method == "POST":
        filtro = request.form.get("filtro", "").strip()

    registros = buscar_registro(filtro)

    return render_template("registroIngresos.html", registros=registros, filtro=filtro)

# Video feed route
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Logout
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
