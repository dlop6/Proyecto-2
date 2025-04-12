import psycopg2
from psycopg2 import pool, sql
from contextlib import contextmanager


class DButils:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            host="localhost",
            database="reservas_db",
            user="proyecto_user",
            password="proyecto_pass",
            port="5433"
        )

    @staticmethod
    def test_connection():
        try:
            db = DButils()
            with db.get_cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM eventos")
                print(f"Conexión exitosa. Eventos en DB: {cur.fetchone()[0]}")
        except Exception as e:
            print(f"Error de conexión: {str(e).splitlines()[0]}")
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
                sql.SQL("INSERT INTO eventos (name, date, location) VALUES (%s, %s, %s) RETURNING id_evento"),
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
                    "INSERT INTO reservas (id_usuario, id_asiento) VALUES (%s, %s) RETURNING id_reserva",
                    (usuario_id, asiento_id)
                )
                return cur.fetchone()[0]
            except psycopg2.IntegrityError as e:
                if "duplicate key" in str(e):
                    print("Error: El asiento ya está reservado.")
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
                    cur.execute(
                        "SELECT id_asiento FROM asientos WHERE id_evento = %s AND numero_asiento = %s FOR UPDATE NOWAIT",
                        (evento_id, numero_asiento)
                    )
                    asiento = cur.fetchone()
                    if not asiento:
                        return False

                    cur.execute(
                        "INSERT INTO reservas (id_usuario, id_asiento) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (usuario_id, asiento[0])
                    )
                    conn.commit()
                    return cur.rowcount > 0

            except psycopg2.OperationalError as e:
                if "could not obtain lock" in str(e):
                    return False
                raise


if __name__ == "__main__":
    DButils.test_connection()
