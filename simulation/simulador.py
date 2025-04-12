import threading
import time
import random
from datetime import datetime
from db_utils import DButils
import logging
from psycopg2 import errors as pg_errors

# Configuración mejorada de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulacion.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimuladorReservas:
    def __init__(self):
        self.db = DButils()
        self.reset_resultados()
        self.evento_actual = None
    
    def reset_resultados(self):
        """Reinicia las estadísticas para nuevas pruebas"""
        self.resultados = {
            'READ COMMITTED': {'exitos': 0, 'fallos': 0, 'tiempos': [], 'conflictos': 0},
            'REPEATABLE READ': {'exitos': 0, 'fallos': 0, 'tiempos': [], 'conflictos': 0},
            'SERIALIZABLE': {'exitos': 0, 'fallos': 0, 'tiempos': [], 'conflictos': 0}
        }

    def preparar_entorno_pruebas(self, evento_id):
        """Versión con diagnóstico extendido"""
        try:
            # Verificar conexión primero
            self.db.test_connection()
            
            # Verificar evento
            self.evento_actual = self.db.get_evento_by_id(evento_id)
            if not self.evento_actual:
                logger.error(f"Evento {evento_id} no encontrado en la base de datos")
                return False
            
            logger.info(f"\nPreparando pruebas para evento: {self.evento_actual[1]} (ID: {self.evento_actual[0]})")
            
            # Diagnóstico avanzado de asientos
            total_asientos = self.db.get_total_asientos_evento(evento_id)
            logger.info(f"Asientos totales registrados: {len(total_asientos)}")
            
            # Limpiar reservas
            if not self.db.limpiar_reservas_evento(evento_id):
                logger.error("Fallo al limpiar reservas")
                return False
            
            # Verificar disponibilidad después de limpiar
            asientos_disp = self.db.get_asientos_disponibles(evento_id)
            logger.info(f"Asientos disponibles después de limpieza: {len(asientos_disp)}")
            
            if not asientos_disp:
                # Diagnóstico adicional
                asientos_ocupados = self.db.get_asientos_ocupados(evento_id)
                logger.error(f"Estado de asientos para evento {evento_id}:")
                logger.error(f" - Totales: {len(total_asientos)}")
                logger.error(f" - Ocupados: {len(asientos_ocupados)}")
                logger.error(f" - Disponibles: 0 (INCONSISTENCIA)")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error en preparar_entorno_pruebas: {str(e)}")
            return False

    def _simular_usuario(self, nivel_aislamiento, evento_id, usuario_id, asiento_especifico=None):
        """Lógica de reserva para un usuario individual con manejo mejorado de errores"""
        try:
            inicio = time.time()
            
            # Asegurar que el usuario_id esté en el rango válido
            usuario_id = (usuario_id % 30) + 1  # Ciclar entre 1 y 30 (nuestros usuarios de prueba)
            
            # Obtener asientos disponibles
            asientos_disponibles = self.db.get_asientos_disponibles(evento_id)
            if not asientos_disponibles:
                logger.debug(f"No hay asientos disponibles para evento {evento_id}")
                self.resultados[nivel_aislamiento]['fallos'] += 1
                return
            
            # Elegir estrategia de reserva
            if asiento_especifico is not None:
                asiento_target = asiento_especifico
            else:
                # 60% de probabilidad de competir por un asiento popular, 40% aleatorio
                if random.random() < 0.6 and len(asientos_disponibles) > 5:
                    # Competir por uno de los primeros 5 asientos (los más populares)
                    asiento_target = random.choice([a[1] for a in asientos_disponibles if a[1] <= 5])
                else:
                    # Elegir aleatorio entre disponibles
                    asiento_target = random.choice([a[1] for a in asientos_disponibles])

            # Intentar reserva
            exito = self.db.reservar_asiento_concurrente(
                usuario_id=usuario_id,
                evento_id=evento_id,
                numero_asiento=asiento_target,
                nivel_aislamiento=nivel_aislamiento
            )

            tiempo = time.time() - inicio
            self.resultados[nivel_aislamiento]['tiempos'].append(tiempo)
            
            if exito:
                self.resultados[nivel_aislamiento]['exitos'] += 1
                logger.info(f"Usuario {usuario_id} reservó asiento {asiento_target} con {nivel_aislamiento}")
            else:
                self.resultados[nivel_aislamiento]['fallos'] += 1
                logger.debug(f"Usuario {usuario_id} no pudo reservar asiento {asiento_target}")

        except pg_errors.SerializationError:
            self.resultados[nivel_aislamiento]['conflictos'] += 1
            logger.debug(f"Conflicto de serialización para usuario {usuario_id}")
        except pg_errors.OperationalError as e:
            if "could not obtain lock" in str(e):
                self.resultados[nivel_aislamiento]['conflictos'] += 1
                logger.debug(f"Bloqueo no obtenido para usuario {usuario_id}")
            else:
                logger.error(f"Error operacional: {e}")
                self.resultados[nivel_aislamiento]['fallos'] += 1
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            self.resultados[nivel_aislamiento]['fallos'] += 1

    def ejecutar_prueba(self, num_usuarios, nivel_aislamiento, evento_id=1, asiento_competitivo=None):
        """Ejecuta una prueba completa con preparación y reporte"""
        if not self.preparar_entorno_pruebas(evento_id):
            return
            
        logger.info(f"\n{'='*50}")
        logger.info(f"Iniciando prueba con {num_usuarios} usuarios ({nivel_aislamiento})")
        logger.info(f"Evento: {self.evento_actual[1]} (ID: {self.evento_actual[0]})")
        logger.info(f"Estrategia: {'Asiento específico' if asiento_competitivo else 'Aleatorio'}")
        logger.info('='*50)
        
        # Ejecutar usuarios concurrentes
        hilos = []
        for i in range(num_usuarios):
            hilo = threading.Thread(
                target=self._simular_usuario,
                args=(nivel_aislamiento, evento_id, i+1, asiento_competitivo)
            )
            hilos.append(hilo)
            hilo.start()
            time.sleep(0.05 * random.random())  # Pequeño delay aleatorio entre usuarios

        # Esperar a que todos terminen
        for hilo in hilos:
            hilo.join()

        # Mostrar resultados
        self._mostrar_resultados(nivel_aislamiento, evento_id)

    def _mostrar_resultados(self, nivel_aislamiento, evento_id):
        """Genera un reporte detallado de los resultados"""
        datos = self.resultados[nivel_aislamiento]
        exitos = datos['exitos']
        fallos = datos['fallos']
        conflictos = datos['conflictos']
        total = exitos + fallos
        
        # Obtener estado final de asientos
        asientos_disp_final = len(self.db.get_asientos_disponibles(evento_id))
        asientos_totales = len(self.db.get_total_asientos_evento(evento_id))
        
        logger.info(f"\nResultados para {nivel_aislamiento}:")
        logger.info(f" - Usuarios simulados: {total}")
        logger.info(f" - Reservas exitosas: {exitos} ({exitos/total*100:.1f}%)")
        logger.info(f" - Fallos: {fallos} ({fallos/total*100:.1f}%)")
        logger.info(f" - Conflictos detectados: {conflictos}")
        
        if datos['tiempos']:
            avg_time = sum(datos['tiempos'])/len(datos['tiempos'])
            min_time = min(datos['tiempos'])
            max_time = max(datos['tiempos'])
            logger.info(f" - Tiempo promedio: {avg_time:.4f}s (min: {min_time:.4f}s, max: {max_time:.4f}s)")
        
        logger.info(f" - Asientos disponibles finales: {asientos_disp_final}/{asientos_totales}")
        logger.info('='*50)

    
if __name__ == "__main__":
    # Verificar conexión y estructura primero
    if not DButils.test_connection():
        exit(1)
    
    # Configuración de pruebas
    simulador = SimuladorReservas()
    
    # Mostrar eventos disponibles
    logger.info("\nEventos disponibles en la base de datos:")
    for evento in simulador.db.get_eventos():
        logger.info(f"ID: {evento[0]} - {evento[1]} ({evento[2]})")
    
    # Definir pruebas (usuarios, nivel_aislamiento, evento_id, asiento_especifico)
    pruebas = [
        (20, "READ COMMITTED", 1, 10),    # 20 usuarios compitiendo por asiento 10
        (30, "READ COMMITTED", 1, None),   # 30 usuarios con selección aleatoria
        (25, "REPEATABLE READ", 2, 5),     # 25 usuarios compitiendo por asiento 5
        (40, "REPEATABLE READ", 2, None),  # 40 usuarios con selección aleatoria
        (35, "SERIALIZABLE", 3, 1),        # 35 usuarios compitiendo por asiento 1
        (50, "SERIALIZABLE", 3, None)      # 50 usuarios con selección aleatoria
    ]
    
    # Ejecutar pruebas
    for i, (num_usuarios, nivel, evento_id, asiento_esp) in enumerate(pruebas, 1):
        logger.info(f"\n{'#'*50}")
        logger.info(f" PRUEBA {i}/{len(pruebas)} - {nivel} - {num_usuarios} usuarios ")
        logger.info(f"{'#'*50}")
        
        simulador.ejecutar_prueba(num_usuarios, nivel, evento_id, asiento_esp)
        time.sleep(1)  # Pequeña pausa entre pruebas
    
    # Reporte final
    