import psycopg2
from psycopg2 import OperationalError

try:
    connection = psycopg2.connect(
        dbname='neondb',
        user='neondb_owner',
        password='npg_CBTd8VzrRA6o',
        host='ep-ancient-glade-a8gdjaab.eastus2.azure.neon.tech',
        port='5432',
        sslmode='require'
    )

    print("✅ Conexión exitosa a la base de datos PostgreSQL (Neon)")

except OperationalError as e:
    print(f"❌ Error al conectar: {e}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Conexión cerrada")



# postgresql://neondb_owner:npg_CBTd8VzrRA6o@ep-ancient-glade-a8gdjaab-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
