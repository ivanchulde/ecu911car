import psycopg2
from datetime import datetime

# Configuración de conexión a la base de datos PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'VehiculosDB',  # nombre de la base de datos
    'user': 'admin',
    'password': 'p.7891011'
}

def main():
    """placa_buscar = input("Ingrese la placa a buscar: ")
    resultado = buscar_placa(placa_buscar)
    
    if isinstance(resultado, tuple):
        # Desempaquetar resultados
        id_persona, nombres, cedula, institucion, cargo, placa, marca, modelo, tipo, color = resultado

        print(f"\n🔎 Resultados encontrados:")
        print(f"ID: {id_persona}")
        print(f"Nombres: {nombres}")
        print(f"Cédula: {cedula}")
        print(f"Institución: {institucion}")
        print(f"Cargo: {cargo}")
        print(f"Placa: {placa}")
        print(f"Marca: {marca}")
        print(f"Modelo: {modelo}")
        print(f"Tipo: {tipo}")
        print(f"Color: {color}")

        # Registrar ingreso en otra tabla
        registrar_ingreso(id_persona, nombres, cedula, placa)

    else:
        print(f"❌ {resultado}")

    #Ingreso Manual
    placa_manual = input("\nIngrese la placa manualmente para registrar ingreso: ")
    nombres_manual = input("Ingrese los nombres completos: ") 
    cedula_manual = input("Ingrese la cédula: ")
    registrar_ingreso(0, nombres_manual, cedula_manual, placa_manual)  # ID 0 para ingreso manual """

    #Busqueda de registros de ingresos
    filtro = input("Ingrese un filtro por nombre, cédula o placa (enter para todos): ").strip()
    registros = buscar_registro(filtro)

    if registros:
        print("\n🔎 Registros encontrados:")
        for r in registros:
            id_reg, nombres, cedula, placa, fecha = r
            print(f"\nID: {id_reg}")
            print(f"Nombres: {nombres}")
            print(f"Cédula: {cedula}")
            print(f"Placa: {placa}")
            print(f"Fecha Ingreso: {fecha}")
    else:
        print("❌ No se encontraron registros.")

def buscar_placa(placa_buscar):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        query = """
        SELECT id, nombres, cedula, institucion, cargo, placa, marca, modelo, tipo, color
        FROM vehiculosecu911
        WHERE UPPER(placa) = UPPER(%s)
        """
        cur.execute(query, (placa_buscar,))
        resultado = cur.fetchone()

        cur.close()
        conn.close()

        if resultado:
            return resultado
        else:
            return f"No se encontró la placa {placa_buscar}."

    except Exception as e:
        return f"Error al buscar la placa: {str(e)}"

def registrar_ingreso(id_persona, nombres, cedula, placa):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        query = """
        INSERT INTO registro_ingresos (id_persona, nombres, cedula, placa)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (id_persona, nombres.upper(), cedula.upper(), placa.upper()))

        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Ingreso registrado para {nombres} - Placa {placa}.")

    except Exception as e:
        print(f"⚠️ Error al registrar ingreso: {str(e)}")

def buscar_registro(filtro):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        query = """
        SELECT id, nombres, cedula, placa, fecha_hora
        FROM registro_ingresos
        WHERE UPPER(nombres) LIKE UPPER(%s)
           OR UPPER(cedula) LIKE UPPER(%s)
           OR UPPER(placa) LIKE UPPER(%s)
        ORDER BY fecha_hora DESC
        """
        # usamos % para que funcione LIKE
        filtro_param = f"%{filtro}%"
        cur.execute(query, (filtro_param, filtro_param, filtro_param))
        resultados = cur.fetchall()

        cur.close()
        conn.close()

        return resultados

    except Exception as e:
        print(f"⚠️ Error al buscar registros: {str(e)}")
        return []



if __name__ == "__main__":
    main()
