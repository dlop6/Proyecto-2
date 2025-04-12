# Simulador de Reservas Concurrentes

## Descripción
Este proyecto simula un sistema de reservas concurrentes para eventos, demostrando el manejo de transacciones en bases de datos con diferentes niveles de aislamiento. El sistema permite probar cómo se comportan múltiples usuarios intentando reservar los mismos asientos simultáneamente.

## Requisitos previos
- Docker y Docker Compose instalados
- Python 3.8+
- Dependencias de Python (instaladas con `pip install -r requirements.txt`)

## Configuración inicial

1. **Iniciar la base de datos PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

2. **Verificar la conexión**:
   ```bash
   python db_utils.py
   ```
   Si hay errores, revisa que el contenedor esté corriendo con `docker ps`.

## Cómo usar el simulador

Ejecuta el programa principal:
```bash
python simulador.py
```

El sistema mostrará un menú interactivo con las siguientes opciones:

1. **Seleccionar evento**: Se muestran todos los eventos disponibles en la base de datos
2. **Elegir nivel de aislamiento**:
   - READ COMMITTED
   - REPEATABLE READ
   - SERIALIZABLE
3. **Especificar número de usuarios concurrentes** (entre 5 y 30)

## Funcionamiento del sistema

El simulador realiza las siguientes acciones:

1. Crea múltiples hilos (uno por usuario)
2. Cada hilo intenta reservar un asiento aleatorio
3. Registra los resultados de cada operación
4. Genera un reporte con:
   - Número de reservas exitosas/fallidas
   - Errores encontrados
   - Tiempos de ejecución
   - Conflictos de bloqueo

## Estructura del código

### Archivos principales

- `simulador.py`: Contiene la lógica de simulación y el menú interactivo
- `db_utils.py`: Maneja todas las operaciones con la base de datos

### Métodos clave

En `simulador.py`:
- `simular_reserva()`: Intenta reservar un asiento para un usuario
- `ejecutar_simulacion()`: Coordina la ejecución concurrente

En `db_utils.py`:
- `reservar_asiento_concurrente()`: Implementa la reserva con bloqueos
- `get_asientos_disponibles()`: Consulta asientos libres

## Configuración de la base de datos

El sistema espera una base de datos PostgreSQL con:
- Tablas: eventos, asientos, reservas, usuarios
- Usuario: proyecto_user
- Contraseña: proyecto_pass
- Puerto: 5433

Estos parámetros pueden modificarse en el constructor de `DButils`.

## Interpretación de resultados

Los resultados se guardan en `results/resultados.csv` con el formato:
```
event_id,nivel,num_usuarios,reservas_exitosas,reservas_fallidas,errores,bloqueos,tiempo_promedio
```

## Solución de problemas

Si encuentras errores:
1. Verifica que PostgreSQL esté corriendo
2. Ejecuta `docker-compose down -v && docker-compose up -d` para reiniciar
3. Revisa los logs con `docker-compose logs`

## Ejemplo de uso

```
$ python simulador.py

Simulador de Reservas Concurrentes
Eventos disponibles:
1. Concierto UVG - 2025-05-15 (Auditorio UVG)
2. Conferencia de Tecnología - 2025-06-20 (Salón de Conferencias)

Seleccione el ID del evento: 1

Niveles de aislamiento disponibles:
1. READ COMMITTED
2. REPEATABLE READ
3. SERIALIZABLE

Seleccione nivel de aislamiento (1-3): 2

Número de usuarios concurrentes (5-30): 15

Iniciando simulación con 15 usuarios...
[Resultados detallados...]
```