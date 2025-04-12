import psycopg2
from psycopg2 import OperationalError, pool, sql, errors as pg_errors
from contextlib import contextmanager
import logging
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DButils:
    """
    Clase mejorada para manejo de base de datos con:
    - Pool de conexiones
    - Manejo robusto de errores
    - Soporte para transacciones concurrentes
    """
    
    def __init__(self):
        self.connection_pool = self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Crea un pool de conexiones con reintentos"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host="localhost",
                    database="reservas_db",
                    user="proyecto_user",
                    password="proyecto_pass",
                    port="5433"
                )
            except OperationalError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Intento {attempt + 1} de conexión fallido. Reintentando...")
                time.sleep(retry_delay)
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener conexión del pool"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit=True):
        """Context manager para manejo seguro de cursores"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error en transacción: {e}")
                raise
            finally:
                cursor.close()
    
    # Operaciones CRUD para eventos
    def crear_evento(self, name, date, location):
        """Crea un nuevo evento en la base de datos"""
        with self.get_cursor() as cur:
            try:
                cur.execute(
                    sql.SQL("""
                        INSERT INTO eventos (name, date, location) 
                        VALUES (%s, %s, %s) 
                        RETURNING id_evento
                    """), 
                    (name, date, location)
                )
                return cur.fetchone()[0]
            except pg_errors.UniqueViolation:
                logger.error("Evento ya existe")
                raise
            except pg_errors.DatabaseError as e:
                logger.error(f"Error al crear evento: {e}")
                raise
    
    def get_eventos(self):
        """Obtiene todos los eventos"""
        with self.get_cursor() as cur:
            cur.execute("SELECT id_evento, name, date, location FROM eventos")
            return cur.fetchall()
    
    def get_evento_by_id(self, evento_id):
        """Obtiene un evento específico por ID"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_evento, name, date, location 
                FROM eventos 
                WHERE id_evento = %s
            """, (evento_id,))
            return cur.fetchone()
    
    # Operaciones para asientos
    def get_asientos_disponibles(self, evento_id):
        """Obtiene asientos disponibles para un evento"""
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
    
    # Operaciones para reservas
    def create_reserva(self, id_usuario, id_asiento):
        """Crea una reserva básica"""
        with self.get_cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO reservas (id_usuario, id_asiento) 
                    VALUES (%s, %s) 
                    RETURNING id_reserva
                """, (id_usuario, id_asiento))
                return cur.fetchone()[0]
            except pg_errors.IntegrityError as e:
                if "duplicate key" in str(e):
                    logger.warning("Asiento ya reservado")
                elif "foreign key" in str(e):
                    logger.error("Usuario o asiento no existe")
                raise
            except pg_errors.DatabaseError as e:
                logger.error(f"Error al crear reserva: {e}")
                raise
    
    def cancel_reserva(self, reserva_id):
        """Cancela una reserva existente"""
        with self.get_cursor() as cur:
            cur.execute("DELETE FROM reservas WHERE id_reserva = %s", (reserva_id,))
            return cur.rowcount > 0
    
    def reservar_asiento_concurrente(self, usuario_id, evento_id, numero_asiento=None, nivel_aislamiento=None):
        """
        Intenta reservar un asiento de forma concurrente
        con manejo de niveles de aislamiento y bloqueos
        """
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            with self.get_connection() as conn:
                try:
                    if nivel_aislamiento:
                        conn.set_isolation_level(nivel_aislamiento)
                    
                    with conn.cursor() as cur:
                        # Si no se especifica asiento, elegir uno aleatorio disponible
                        if numero_asiento is None:
                            cur.execute("""
                                SELECT id_asiento 
                                FROM asientos 
                                WHERE id_evento = %s 
                                AND id_asiento NOT IN (
                                    SELECT id_asiento FROM reservas
                                )
                                ORDER BY RANDOM() 
                                LIMIT 1
                                FOR UPDATE SKIP LOCKED
                            """, (evento_id,))
                            asiento = cur.fetchone()
                            if not asiento:
                                return False
                            id_asiento = asiento[0]
                        else:
                            # Bloquear el asiento específico
                            cur.execute("""
                                SELECT id_asiento 
                                FROM asientos 
                                WHERE id_evento = %s 
                                AND numero_asiento = %s 
                                FOR UPDATE NOWAIT
                            """, (evento_id, numero_asiento))
                            asiento = cur.fetchone()
                            if not asiento:
                                return False
                            id_asiento = asiento[0]
                        
                        # Verificar que el usuario existe
                        cur.execute("SELECT 1 FROM usuarios WHERE id_usuario = %s", (usuario_id,))
                        if not cur.fetchone():
                            logger.error(f"Usuario {usuario_id} no existe")
                            return False
                        
                        # Intentar reserva
                        cur.execute("""
                            INSERT INTO reservas (id_usuario, id_asiento) 
                            VALUES (%s, %s) 
                            ON CONFLICT DO NOTHING
                        """, (usuario_id, id_asiento))
                        conn.commit()
                        return cur.rowcount > 0
                        
                except pg_errors.OperationalError as e:
                    if "could not obtain lock" in str(e):
                        if attempt == max_retries - 1:
                            logger.debug(f"No se pudo obtener bloqueo para usuario {usuario_id}")
                            return False
                        time.sleep(retry_delay)
                        continue
                    logger.error(f"Error operacional: {e}")
                    raise
                except pg_errors.SerializationError:
                    if attempt == max_retries - 1:
                        logger.debug(f"Serialización fallida para usuario {usuario_id}")
                        return False
                    time.sleep(retry_delay)
                    continue
                except pg_errors.DatabaseError as e:
                    logger.error(f"Error de base de datos: {e}")
                    conn.rollback()
                    raise
        
        return False

    @staticmethod
    def test_connection():
        """Verifica la conexión y estructura básica"""
        try:
            db = DButils()
            with db.get_cursor() as cur:
                # Verificar tablas esenciales
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'eventos'
                    )
                """)
                if not cur.fetchone()[0]:
                    raise OperationalError("Tabla 'eventos' no existe")
                
                logger.info("✅ Conexión y estructura básica verificadas")
                return True
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

if __name__ == "__main__":
    DButils.test_connection()