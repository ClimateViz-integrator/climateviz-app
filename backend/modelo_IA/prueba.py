import psycopg2
from psycopg2 import OperationalError

try:
    connection = psycopg2.connect(
        dbname='climateviz_db',
        user='climateviz_db_user',
        password='tXT9hh8JSgW67Rm8dsaGPf7hMHdck9yv',
        host='dpg-d111ueumcj7s739p29q0-a.oregon-postgres.render.com',
        port='5432',
    )

    print("✅ Conexión exitosa a la base de datos PostgreSQL (Neon)")

except OperationalError as e:
    print(f"❌ Error al conectar: {e}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Conexión cerrada")
