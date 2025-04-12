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
    - Pool de conexiones robusto
    - Manejo detallado de errores
    - Soporte para transacciones concurrentes
    - Métodos de diagnóstico
    """
    
    def __init__(self):
        self.connection_pool = self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Crea un pool de conexiones con reintentos"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host="localhost",
                    database="reservas_db",
                    user="proyecto_user",
                    password="proyecto_pass",
                    port="5433"
                )
                logger.info(" Pool de conexiones creado exitosamente")
                return pool
            except OperationalError as e:
                if attempt == max_retries - 1:
                    logger.error(" No se pudo crear el pool de conexiones después de %d intentos", max_retries)
                    raise
                logger.warning("Intento %d de conexión fallido. Reintentando en %d segundos...", 
                              attempt + 1, retry_delay)
                time.sleep(retry_delay)
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener conexión del pool con manejo de errores"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        except Exception as e:
            logger.error("Error al obtener conexión: %s", e)
            raise
        finally:
            if conn:
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
                logger.error("Error en transacción: %s", e)
                raise
            finally:
                cursor.close()

    # Métodos para diagnóstico
    def check_database_health(self):
        """Verifica el estado de la base de datos y tablas esenciales"""
        checks = {
            'eventos': False,
            'asientos': False,
            'usuarios': False,
            'reservas': False
        }
        
        try:
            with self.get_cursor() as cur:
                # Verificar tablas
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name IN ('eventos', 'asientos', 'usuarios', 'reservas')
                """)
                existing_tables = {row[0] for row in cur.fetchall()}
                
                for table in checks:
                    if table in existing_tables:
                        checks[table] = True
                
                # Verificar datos básicos
                cur.execute("SELECT COUNT(*) FROM eventos")
                checks['eventos_count'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM asientos")
                checks['asientos_count'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM usuarios")
                checks['usuarios_count'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM reservas")
                checks['reservas_count'] = cur.fetchone()[0]
                
            return checks
        except Exception as e:
            logger.error("Error en check_database_health: %s", e)
            return checks

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
                logger.error("Error al crear evento: %s", e)
                raise
    
    def get_eventos(self):
        """Obtiene todos los eventos con información detallada"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_evento, name, date, location 
                FROM eventos 
                ORDER BY id_evento
            """)
            return cur.fetchall()
    
    def get_evento_by_id(self, evento_id):
        """Obtiene un evento específico por ID con verificación"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_evento, name, date, location 
                FROM eventos 
                WHERE id_evento = %s
            """, (evento_id,))
            result = cur.fetchone()
            if not result:
                logger.warning("Evento con ID %s no encontrado", evento_id)
            return result
    
    # Operaciones para asientos
    def get_total_asientos_evento(self, evento_id):
        """Obtiene todos los asientos de un evento"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_asiento, numero_asiento 
                FROM asientos 
                WHERE id_evento = %s
                ORDER BY numero_asiento
            """, (evento_id,))
            return cur.fetchall()
    
    def get_asientos_ocupados(self, evento_id):
        """Obtiene asientos ocupados para un evento específico"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT a.id_asiento, a.numero_asiento 
                FROM asientos a
                JOIN reservas r ON a.id_asiento = r.id_asiento
                WHERE a.id_evento = %s
                ORDER BY a.numero_asiento
            """, (evento_id,))
            return cur.fetchall()
    
    def get_asientos_disponibles(self, evento_id):
        """Versión mejorada con diagnóstico incorporado"""
        try:
            with self.get_cursor() as cur:
                # Primero verificar si el evento existe
                cur.execute("SELECT 1 FROM eventos WHERE id_evento = %s", (evento_id,))
                if not cur.fetchone():
                    logger.error(f"Evento {evento_id} no existe en get_asientos_disponibles")
                    return []
                
                # Consulta principal con diagnóstico
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
                
                resultados = cur.fetchall()
                logger.debug(f"Encontrados {len(resultados)} asientos disponibles para evento {evento_id}")
                return resultados
                
        except Exception as e:
            logger.error(f"Error en get_asientos_disponibles: {str(e)}")
            return []
    
    # Operaciones para reservas
    def create_reserva(self, id_usuario, id_asiento):
        """Crea una reserva básica con manejo de errores"""
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
                    logger.warning("Asiento %s ya reservado", id_asiento)
                elif "foreign key" in str(e):
                    logger.error("Usuario %s o asiento %s no existe", id_usuario, id_asiento)
                raise
            except pg_errors.DatabaseError as e:
                logger.error("Error al crear reserva: %s", e)
                raise
    
    def cancel_reserva(self, reserva_id):
        """Cancela una reserva existente con verificación"""
        with self.get_cursor() as cur:
            cur.execute("""
                DELETE FROM reservas 
                WHERE id_reserva = %s
                RETURNING id_reserva
            """, (reserva_id,))
            result = cur.fetchone()
            if not result:
                logger.warning("Reserva %s no encontrada", reserva_id)
                return False
            return True
    
    def limpiar_reservas_evento(self, evento_id):
        """Elimina todas las reservas de un evento con verificación"""
        with self.get_cursor() as cur:
            try:
                # Primero verificar si el evento existe
                cur.execute("SELECT 1 FROM eventos WHERE id_evento = %s", (evento_id,))
                if not cur.fetchone():
                    logger.error("Evento %s no existe", evento_id)
                    return False
                
                # Eliminar reservas
                cur.execute("""
                    DELETE FROM reservas
                    WHERE id_asiento IN (
                        SELECT id_asiento FROM asientos WHERE id_evento = %s
                    )
                """, (evento_id,))
                logger.info("Eliminadas %d reservas para evento %s", cur.rowcount, evento_id)
                return True
            except Exception as e:
                logger.error("Error al limpiar reservas para evento %s: %s", evento_id, e)
                return False
    
    def reservar_asiento_concurrente(self, usuario_id, evento_id, numero_asiento=None, nivel_aislamiento=None):
        """
        Versión mejorada del método de reserva concurrente con:
        - Reintentos automáticos
        - Mejor manejo de errores
        - Diagnóstico detallado
        """
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            with self.get_connection() as conn:
                try:
                    if nivel_aislamiento:
                        conn.set_isolation_level(nivel_aislamiento)
                    
                    with conn.cursor() as cur:
                        # Verificar que el usuario existe
                        cur.execute("SELECT 1 FROM usuarios WHERE id_usuario = %s", (usuario_id,))
                        if not cur.fetchone():
                            logger.error("Usuario %s no existe", usuario_id)
                            return False
                        
                        # Selección de asiento
                        if numero_asiento is None:
                            # Asiento aleatorio disponible
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
                                logger.debug("No hay asientos disponibles para evento %s", evento_id)
                                return False
                            id_asiento = asiento[0]
                        else:
                            # Asiento específico
                            cur.execute("""
                                SELECT id_asiento 
                                FROM asientos 
                                WHERE id_evento = %s 
                                AND numero_asiento = %s
                                FOR UPDATE NOWAIT
                            """, (evento_id, numero_asiento))
                            asiento = cur.fetchone()
                            if not asiento:
                                logger.warning("Asiento %s no existe para evento %s", numero_asiento, evento_id)
                                return False
                            id_asiento = asiento[0]
                        
                        # Intentar reserva
                        cur.execute("""
                            INSERT INTO reservas (id_usuario, id_asiento) 
                            VALUES (%s, %s) 
                            ON CONFLICT DO NOTHING
                        """, (usuario_id, id_asiento))
                        conn.commit()
                        
                        if cur.rowcount > 0:
                            logger.debug("Reserva exitosa para usuario %s en asiento %s", usuario_id, id_asiento)
                            return True
                        else:
                            logger.debug("Reserva fallida (asiento %s ya ocupado)", id_asiento)
                            return False
                
                except pg_errors.SerializationError:
                    logger.debug("Intento %d: Error de serialización", attempt + 1)
                    if attempt == max_retries - 1:
                        logger.debug("Maximos reintentos alcanzados para usuario %s", usuario_id)
                        return False
                    time.sleep(retry_delay)
                    continue
                    
                except pg_errors.OperationalError as e:
                    if "could not obtain lock" in str(e):
                        logger.debug("Intento %d: No se pudo obtener bloqueo", attempt + 1)
                        if attempt == max_retries - 1:
                            logger.debug("Maximos reintentos alcanzados para usuario %s", usuario_id)
                            return False
                        time.sleep(retry_delay)
                        continue
                    logger.error("Error operacional: %s", e)
                    conn.rollback()
                    raise
                    
                except pg_errors.DatabaseError as e:
                    logger.error("Error de base de datos: %s", e)
                    conn.rollback()
                    raise
        
        return False

    @staticmethod
    def test_connection():
        """Prueba completa de conexión y estructura"""
        try:
            db = DButils()
            
            # Verificar conexión básica
            with db.get_cursor() as cur:
                cur.execute("SELECT 1")
                if cur.fetchone()[0] != 1:
                    raise OperationalError("Prueba básica de conexión fallida")
            
            # Verificar estructura de la base de datos
            health = db.check_database_health()
            if not all(health[t] for t in ['eventos', 'asientos', 'usuarios', 'reservas']):
                missing = [t for t in health if not health[t]]
                raise OperationalError(f"Tablas faltantes: {missing}")
            
            logger.info(" Conexión y estructura verificadas exitosamente")
            logger.info("Estadísticas de la base de datos:")
            logger.info(" - Eventos: %d", health.get('eventos_count', 0))
            logger.info(" - Asientos: %d", health.get('asientos_count', 0))
            logger.info(" - Usuarios: %d", health.get('usuarios_count', 0))
            logger.info(" - Reservas: %d", health.get('reservas_count', 0))
            
            return True
        except Exception as e:
            logger.error(" Error en test_connection: %s", e)
            return False

if __name__ == "__main__":
    DButils.test_connection()