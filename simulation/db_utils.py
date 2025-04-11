import psycopg2
from psycopg2 import OperationalError, pool, sql
from contextlib import contextmanager




class DButils:
    """
    Clase DButils
    Esta clase proporciona utilidades para interactuar con una base de datos PostgreSQL, 
    incluyendo manejo de conexiones, transacciones y operaciones específicas para un sistema de reservas.
    Métodos:
    ---------
    - __init__():
        Inicializa un pool de conexiones a la base de datos.
    - get_connection():
        Context manager para obtener una conexión del pool.
    - get_cursor():
        Context manager para obtener un cursor de la conexión, manejando automáticamente commit/rollback.
    - crear_evento(nombre, fecha, ubicacion):
        Crea un nuevo evento en la base de datos y retorna el ID del evento creado.
    - get_eventos():
        Retorna todos los eventos registrados en la base de datos.
    - get_evento_by_id(evento_id):
        Retorna los detalles de un evento específico por su ID.
    - get_asientos_disponibles(evento_id):
        Retorna los asientos disponibles para un evento específico.
    - create_reserva(usuario_id, asiento_id):
        Crea una reserva para un usuario y asiento específicos. Maneja errores de integridad.
    - cancel_reserva(reserva_id):
        Cancela una reserva específica por su ID. Retorna True si se eliminó correctamente.
    - reservar_asiento_concurrente(usuario_id, evento_id, numero_asiento, nivel_aislamiento=None):
        Intenta reservar un asiento de forma concurrente utilizando bloqueos y niveles de aislamiento.
        Retorna True si la reserva fue exitosa, False si el asiento ya estaba reservado.
    """
    
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            host="localhost",
            database="reservas_db",
            user="proyecto_user",
            password="proyecto_pass",
            port="5433"  # Cambiado a 5433 para coincidir con docker-compose
        )
    
    @staticmethod
    def test_connection():
        """Verifica que la conexión a la BD funcione y que las tablas básicas existan.
        Muestra errores útiles si falla."""
        try:
            db = DButils()
            with db.get_cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM eventos")
                print(f"✅ Conexión exitosa. Eventos en DB: {cur.fetchone()[0]}")
        except Exception as e:
            print(f"❌ Error de conexión: {str(e).splitlines()[0]}")
            print("\nPosibles soluciones:")
            print("1. Ejecuta: docker-compose down -v")
            print("2. Verifica que los contenedores estén corriendo: docker ps")
            print("3. Revisa el archivo .env si usas variables de entorno")
        
        
    @contextmanager
    def get_connection(self):
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except:
                conn.rollback()
                raise
            finally:
                cursor.close()
                
    def crear_evento(self, nombre, fecha, ubicacion):
        with self.get_cursor() as cur:
            cur.execute(
                sql.SQL("INSERT INTO eventos (nombre, fecha, ubicacion) VALUES (%s, %s, %s) RETURNING id_evento"),
                (nombre, fecha, ubicacion)
            )
            return cur.fetchone()[0]
    
    def get_eventos(self):
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM eventos")
            return cur.fetchall()
    
    def get_evento_by_id(self, evento_id):
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM eventos WHERE id_evento = %s", (evento_id,))
            return cur.fetchone()
        
    
    def get_asientos_disponibles(self, evento_id):
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT a.id_asiento, a.numero_asiento 
                FROM asientos a
                WHERE a.id_evento = %s 
                AND NOT EXISTS (
                    SELECT 1 FROM reservas r 
                    WHERE r.id_asiento = a.id_asiento
                )
                ORDER BY a.numero_asiento
            """, (evento_id,))
            return cur.fetchall()
    
    def create_reserva(self, usuario_id, asiento_id):
        with self.get_cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO reservas (usuario_id, asiento_id) VALUES (%s, %s) RETURNING id_reserva",
                    (usuario_id, asiento_id)
                )
                return cur.fetchone()[0]
            except psycopg2.IntegrityError as e:
                if "duplicate key" in str(e):
                    print("❌ Error: El asiento ya está reservado.")
                    raise e
                raise
    def cancel_reserva(self, reserva_id):
        with self.get_cursor() as cur:
            cur.execute("DELETE FROM reservas WHERE id_reserva = %s", (reserva_id,))
            
            return cur.rowcount > 0
            
    def reservar_asiento_concurrente(self, usuario_id, evento_id, numero_asiento, nivel_aislamiento=None):
        with self.get_connection() as conn:
            try:
                if nivel_aislamiento:
                    conn.set_isolation_level(nivel_aislamiento)
                
                with conn.cursor() as cur:
                    # Bloquea el asiento
                    cur.execute(
                        "SELECT id_asiento FROM asientos WHERE id_evento = %s AND numero_asiento = %s FOR UPDATE NOWAIT",
                        (evento_id, numero_asiento)
                    )
                    asiento = cur.fetchone()
                    if not asiento:
                        return False
                    
                    # Intenta reserva
                    cur.execute(
                        "INSERT INTO reservas (usuario_id, asiento_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (usuario_id, asiento[0])
                    )
                    conn.commit()
                    return cur.rowcount > 0
                    
            except psycopg2.OperationalError as e:
                if "could not obtain lock" in str(e):
                    return False  # Asiento ya bloqueado
                raise
            
          

if __name__ == "__main__":
    DButils.test_connection()