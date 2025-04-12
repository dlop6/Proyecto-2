import threading
import time
from psycopg2 import extensions
from db_utils import DButils
import random

NUM_USUARIOS = 10
EVENTO_ID = 3
NIVEL_AISLAMIENTO = extensions.ISOLATION_LEVEL_SERIALIZABLE

resultados = {
    "exitosas": 0,
    "fallidas": 0,
    "tiempos": []
}

lock = threading.Lock()

def simular_reserva(usuario_id):
    db = DButils()
    asiento = random.randint(1, 10)

    inicio = time.perf_counter()
    try:
        exito = db.reservar_asiento_concurrente(
            usuario_id=usuario_id,
            evento_id=EVENTO_ID,
            numero_asiento=asiento,
            nivel_aislamiento=NIVEL_AISLAMIENTO
        )
    except Exception as e:
        print(f"[Error Usuario {usuario_id}] {str(e).splitlines()[0]}")
        exito = False
    fin = time.perf_counter()

    tiempo = (fin - inicio) * 1000

    with lock:
        if exito:
            resultados["exitosas"] += 1
        else:
            resultados["fallidas"] += 1
        resultados["tiempos"].append(tiempo)

def ejecutar_simulacion():
    hilos = []
    for i in range(NUM_USUARIOS):
        hilo = threading.Thread(target=simular_reserva, args=(i + 1,))
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    print("\n🧾 Resultados de la Simulación:")
    print(f"Usuarios Concurrentes: {NUM_USUARIOS}")
    print(f"Nivel de Aislamiento: {NIVEL_AISLAMIENTO}")
    print(f"Reservas Exitosas: {resultados['exitosas']}")
    print(f"Reservas Fallidas: {resultados['fallidas']}")
    if resultados["tiempos"]:
        print(f"Tiempo Promedio: {sum(resultados['tiempos']) / len(resultados['tiempos']):.2f} ms")
    else:
        print("No se registraron tiempos de reserva (todas fallaron).")

if __name__ == "__main__":
    ejecutar_simulacion()
