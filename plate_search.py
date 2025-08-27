import psycopg2

# Configuración de conexión a la base de datos PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'VehiculosDB', #nombre de la base de datos
    'user': 'admin',
    'password': 'p.7891011'
}

def main():
    placa_buscar = input("Ingrese la placa a buscar: ")
    resultado = buscar_placa(placa_buscar)
    
    if isinstance(resultado, tuple):
        # Desempaquetar resultados
        id, nombres, cedula, institucion, cargo, placa, marca, modelo, tipo, color = resultado

        print(f"\n🔎 Resultados encontrados:")
        print(f"ID: {id}")
        print(f"Nombres: {nombres}")
        print(f"Cédula: {cedula}")
        print(f"Institución: {institucion}")
        print(f"Cargo: {cargo}")
        print(f"Placa: {placa}")
        print(f"Marca: {marca}")
        print(f"Modelo: {modelo}")
        print(f"Tipo: {tipo}")
        print(f"Color: {color}")
    else:
        print(f"❌ {resultado}")

def buscar_placa(placa_buscar):
    try:
        # Conexión a la base de datos
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Conexión exitosa")
        # Consulta SQL para buscar por placa (ignora mayúsculas/minúsculas)
        query = """
        SELECT id, nombres, cedula, institucion, cargo, placa, marca, modelo, tipo, color
        FROM vehiculosecu911
        WHERE UPPER(placa) = UPPER(%s)
        """
        cur.execute(query, (placa_buscar,))
        resultado = cur.fetchone()

        # Cerrar conexiones
        cur.close()
        conn.close()

        if resultado:
            return resultado
        else:
            return f"No se encontró la placa {placa_buscar}."

    except Exception as e:
        return f"Error al buscar la placa: {str(e)}"

if __name__ == "__main__":
    main()
