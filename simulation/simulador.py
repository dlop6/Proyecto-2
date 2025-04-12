import threading
import random
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_REPEATABLE_READ, ISOLATION_LEVEL_SERIALIZABLE
from db_utils import DButils  # Asumiendo que tu archivo se llama db_utils.py

class SimuladorReservas:
    def __init__(self):
        self.db = DButils()
        self.resultados = {
            "exitosas": 0,
            "fallidas": 0,
            "errores": 0,
            "bloqueos": 0
        }
        self.lock = threading.Lock()

    def simular_reserva(self, user_id, event_id, nivel_aislamiento=None):
        try:
            # Seleccionar un asiento disponible aleatorio
            asientos_disponibles = self.db.get_asientos_disponibles(event_id)
            
            if not asientos_disponibles:
                with self.lock:
                    self.resultados["fallidas"] += 1
                print(f"Usuario {user_id} - No hay asientos disponibles")
                return False
                
            asiento_id, numero_asiento = random.choice(asientos_disponibles)
            
            # Intentar reserva con el método concurrente
            exito = self.db.reservar_asiento_concurrente(
                user_id, 
                event_id, 
                numero_asiento,
                nivel_aislamiento
            )
            
            with self.lock:
                if exito:
                    self.resultados["exitosas"] += 1
                    print(f"Usuario {user_id} - Reserva exitosa para asiento {numero_asiento}")
                else:
                    self.resultados["fallidas"] += 1
                    print(f"Usuario {user_id} - No pudo reservar asiento {numero_asiento}")
            
            return exito
            
        except psycopg2.OperationalError as e:
            if "could not obtain lock" in str(e):
                with self.lock:
                    self.resultados["bloqueos"] += 1
                print(f"Usuario {user_id} - Asiento bloqueado, reintentando...")
                return self.simular_reserva(user_id, event_id, nivel_aislamiento)
            else:
                with self.lock:
                    self.resultados["errores"] += 1
                print(f" Usuario {user_id} - Error: {str(e)}")
                return False
        except Exception as e:
            with self.lock:
                self.resultados["errores"] += 1
            print(f" Usuario {user_id} - Error inesperado: {str(e)}")
            return False

    def ejecutar_simulacion(self, num_usuarios, event_id, nivel_aislamiento=None):
        threads = []
        self.resultados = {"exitosas": 0, "fallidas": 0, "errores": 0, "bloqueos": 0}
        
        inicio = time.time()
        
        print(f"\nIniciando simulación con {num_usuarios} usuarios...")
        print(f"🔧 Nivel de aislamiento: {nivel_aislamiento or 'Por defecto'}")
        
        for i in range(num_usuarios):
            t = threading.Thread(
                target=self.simular_reserva,
                args=(i+1, event_id, nivel_aislamiento)
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        tiempo_total = time.time() - inicio
        tiempo_promedio = (tiempo_total * 1000) / num_usuarios
        
        print("\nResultados:")
        print(f"Reservas exitosas: {self.resultados['exitosas']}")
        print(f"Reservas fallidas: {self.resultados['fallidas']}")
        print(f"Errores: {self.resultados['errores']}")
        print(f"Bloqueos: {self.resultados['bloqueos']}")
        print(f"Tiempo total: {tiempo_total:.2f} segundos")
        print(f"Tiempo promedio por usuario: {tiempo_promedio:.2f} ms")
        
        return {
            "reservas_exitosas": self.resultados["exitosas"],
            "reservas_fallidas": self.resultados["fallidas"],
            "errores": self.resultados["errores"],
            "bloqueos": self.resultados["bloqueos"],
            "tiempo_total": tiempo_total,
            "tiempo_promedio": tiempo_promedio
        }

# Configuración de niveles de aislamiento
NIVELES_AISLAMIENTO = {
    "READ COMMITTED": ISOLATION_LEVEL_READ_COMMITTED,
    "REPEATABLE READ": ISOLATION_LEVEL_REPEATABLE_READ,
    "SERIALIZABLE": ISOLATION_LEVEL_SERIALIZABLE
}

def menu_principal():
    print("\nSimulador de Reservas Concurrentes")
    print("Basado en el sistema de gestión de base de datos DButils")
    
    db = DButils()
    eventos = db.get_eventos()
    
    print("\nEventos disponibles:")
    for evento in eventos:
        print(f"{evento[0]}. {evento[1]} - {evento[2]} ({evento[3]})")
    
    event_id = int(input("\nSeleccione el ID del evento: "))
    
    print("\nNiveles de aislamiento disponibles:")
    for i, nivel in enumerate(NIVELES_AISLAMIENTO.keys(), 1):
        print(f"{i}. {nivel}")
    
    opcion = input("\nSeleccione nivel de aislamiento (1-3, Enter para predeterminado): ")
    if opcion.isdigit() and 0 < int(opcion) <= 3:
        nivel = list(NIVELES_AISLAMIENTO.keys())[int(opcion)-1]
        nivel_aislamiento = NIVELES_AISLAMIENTO[nivel]
    else:
        nivel = "Por defecto"
        nivel_aislamiento = None
    
    num_usuarios = int(input("\nNúmero de usuarios concurrentes (5-30): ") or "10")
    num_usuarios = max(5, min(30, num_usuarios))
    
    print(f"\nConfiguración final:")
    print(f"Evento: {event_id}")
    print(f"Nivel de aislamiento: {nivel}")
    print(f"Usuarios concurrentes: {num_usuarios}")
    
    input("\nPresione Enter para comenzar la simulación...")
    
    simulador = SimuladorReservas()
    resultados = simulador.ejecutar_simulacion(
        num_usuarios, 
        event_id,
        nivel_aislamiento
    )
    
    # Guardar resultados en un archivo
    with open("resultados.csv", "a") as f:
        f.write(f"{event_id},{nivel},{num_usuarios},{resultados['reservas_exitosas']},{resultados['reservas_fallidas']},{resultados['errores']},{resultados['bloqueos']},{resultados['tiempo_promedio']:.2f}\n")
    
    print("\nSimulación completada. Resultados guardados en 'resultados_simulacion.csv'")

if __name__ == "__main__":
    menu_principal()