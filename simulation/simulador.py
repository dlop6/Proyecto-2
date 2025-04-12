import threading
import time
import random
from datetime import datetime
from db_utils import DButils
import logging
from psycopg2 import OperationalError, errors as pg_errors

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulacion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimuladorReservas:
    def __init__(self):
        self.db = DButils()
        self.resultados = {
            'READ COMMITTED': {'exitos': 0, 'fallos': 0, 'tiempos': []},
            'REPEATABLE READ': {'exitos': 0, 'fallos': 0, 'tiempos': []},
            'SERIALIZABLE': {'exitos': 0, 'fallos': 0, 'tiempos': []}
        }

    def _simular_usuario(self, nivel_aislamiento, evento_id, usuario_id, asiento_especifico=None):
        """Lógica de reserva para un usuario individual"""
        try:
            inicio = time.time()
            
            # Asegurar que el usuario_id esté en el rango válido (1-11 según datos iniciales)
            usuario_id = (usuario_id % 11) + 1  # Esto cicla los IDs entre 1 y 11
            
            # Elegir asiento (competitivo o aleatorio)
            asientos_disponibles = self.db.get_asientos_disponibles(evento_id)
            if not asientos_disponibles:
                logger.warning(f"No hay asientos disponibles para el evento {evento_id}")
                return
                
            asiento_target = asiento_especifico or random.choice(
                [a[1] for a in asientos_disponibles]
            ) if random.random() > 0.5 else None  # 50% de probabilidad de competir

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
                logger.warning(f"Usuario {usuario_id} no pudo reservar con {nivel_aislamiento}")

        except pg_errors.ForeignKeyViolation as e:
            logger.error(f"Error de clave foránea para usuario {usuario_id}: {str(e).splitlines()[0]}")
            self.resultados[nivel_aislamiento]['fallos'] += 1
        except OperationalError as e:
            logger.error(f"Error operacional en usuario {usuario_id}: {str(e).splitlines()[0]}")
            self.resultados[nivel_aislamiento]['fallos'] += 1
        except Exception as e:
            logger.error(f"Error inesperado en usuario {usuario_id}: {str(e)}")
            self.resultados[nivel_aislamiento]['fallos'] += 1

    def ejecutar_prueba(self, num_usuarios, nivel_aislamiento, evento_id=1):
        """Ejecuta prueba con usuarios concurrentes"""
        # Verificar que el evento existe
        if not self.db.get_evento_by_id(evento_id):
            logger.error(f"El evento {evento_id} no existe!")
            return
            
        hilos = []
        logger.info(f"\n{'='*50}\nIniciando prueba con {num_usuarios} usuarios ({nivel_aislamiento}) para evento {evento_id}...")
        
        for i in range(num_usuarios):
            hilo = threading.Thread(
                target=self._simular_usuario,
                args=(nivel_aislamiento, evento_id, i+1, 10)  # Todos compiten por el asiento 10
            )
            hilos.append(hilo)
            hilo.start()
            time.sleep(0.1 * random.random())  # Espaciado aleatorio entre solicitudes

        for hilo in hilos:
            hilo.join()

        # Calcular estadísticas
        exitos = self.resultados[nivel_aislamiento]['exitos']
        fallos = self.resultados[nivel_aislamiento]['fallos']
        tiempos = self.resultados[nivel_aislamiento]['tiempos']
        
        tiempo_promedio = sum(tiempos)/len(tiempos) if tiempos else 0
        
        logger.info(f"\nResultados para {nivel_aislamiento}:")
        logger.info(f" - Reservas exitosas: {exitos}")
        logger.info(f" - Reservas fallidas: {fallos}")
        logger.info(f" - Tasa de éxito: {(exitos/(exitos+fallos))*100:.2f}%" if exitos+fallos > 0 else " - Tasa de éxito: 0%")
        logger.info(f" - Tiempo promedio: {tiempo_promedio:.4f} segundos")
        logger.info('='*50)

    def generar_reporte(self):
        """Genera un reporte consolidado de todas las pruebas"""
        logger.info("\n\nREPORTE FINAL DE SIMULACIÓN")
        logger.info("="*50)
        
        for nivel, datos in self.resultados.items():
            total = datos['exitos'] + datos['fallos']
            if total == 0:
                continue
                
            logger.info(f"\nNivel de Aislamiento: {nivel}")
            logger.info(f" - Total intentos: {total}")
            logger.info(f" - Éxitos: {datos['exitos']} ({(datos['exitos']/total)*100:.2f}%)")
            logger.info(f" - Fallos: {datos['fallos']} ({(datos['fallos']/total)*100:.2f}%)")
            
            if datos['tiempos']:
                avg_time = sum(datos['tiempos'])/len(datos['tiempos'])
                logger.info(f" - Tiempo promedio: {avg_time:.4f} segundos")
        
        logger.info("="*50)

if __name__ == "__main__":
    # Configuración de pruebas según requerimientos del proyecto
    simulador = SimuladorReservas()
    
    # Pruebas con diferentes niveles de aislamiento
    pruebas = [
        (5, "READ COMMITTED", 1),
        (10, "REPEATABLE READ", 1), 
        (20, "SERIALIZABLE", 1),
        (30, "SERIALIZABLE", 1)
    ]
    
    for num_usuarios, nivel, evento_id in pruebas:
        simulador.ejecutar_prueba(num_usuarios, nivel, evento_id)
        time.sleep(2)  # Intervalo entre pruebas
    
    # Generar reporte final
    simulador.generar_reporte()