# 📌 Proyecto 2 - Simulador de Reservas Concurrentes

**Sistema de simulación de reservas para eventos con manejo de concurrencia en PostgreSQL**

## 📋 Descripción

Este proyecto implementa un sistema de reservas de asientos para eventos que maneja operaciones concurrentes utilizando diferentes niveles de aislamiento de transacciones en PostgreSQL. El sistema permite simular múltiples usuarios intentando reservar asientos simultáneamente, midiendo el rendimiento y conflictos en distintos escenarios.

## 🚀 Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.8+
- psycopg2-binary (se instala automáticamente)
- PostgreSQL 13+

## 🛠 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/dlop6/Proyecto-2
cd proyecto-reservas-concurrentes
```

2. Iniciar los servicios con Docker Compose:
```bash
docker-compose up -d
```

3. Instalar dependencias de Python:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

El sistema viene preconfigurado con estos parámetros (editables en `docker-compose.yml` y `.env`):

- **PostgreSQL**:
  - Puerto: 5433
  - Usuario: `proyecto_user`
  - Contraseña: `proyecto_pass`
  - Base de datos: `reservas_db`

- **Simulación**:
  - Niveles de aislamiento probados: READ COMMITTED, REPEATABLE READ, SERIALIZABLE
  - Usuarios concurrentes: 5, 10, 20, 30

## 🖥 Uso del Programa

### Ejecutar todas las pruebas automáticamente
```bash
python simulation/simulador.py
```

### Ejecutar pruebas específicas
```python
from simulation.simulador import SimuladorReservas

simulador = SimuladorReservas()

# Prueba con 10 usuarios en REPEATABLE READ
simulador.ejecutar_prueba(num_usuarios=10, nivel_aislamiento="REPEATABLE READ", evento_id=1)

# Generar reporte final
simulador.generar_reporte()
```

### Parámetros personalizables
- `num_usuarios`: Cantidad de usuarios concurrentes (5, 10, 20, 30)
- `nivel_aislamiento`: "READ COMMITTED", "REPEATABLE READ" o "SERIALIZABLE"
- `evento_id`: ID del evento a simular (1-4 por defecto)

## 📊 Resultados

El programa genera:
1. Logs detallados en `simulacion.log`
2. Reporte final en consola con estadísticas
3. Tabla comparativa de resultados

Ejemplo de salida:
```
🔍 Resultados para SERIALIZABLE:
 - Reservas exitosas: 15
 - Reservas fallidas: 5 
 - Tasa de éxito: 75.00%
 - Tiempo promedio: 0.42 segundos
```

## 🧩 Estructura del Proyecto

```
.
├── docker-compose.yml
├── sql/
│   ├── 01_ddl.sql          # Esquema de la base de datos
│   └── 02_data.sql         # Datos iniciales
├── simulation/
│   ├── simulador.py        # Lógica de simulación
│   └── db_utils.py         # Utilidades de base de datos
└── tests/                  # Pruebas unitarias
```

## 🛑 Detener el Sistema

```bash
docker-compose down
```

## 📝 Notas Adicionales

- Los datos de prueba incluyen 4 eventos y 11 usuarios
- Para reiniciar completamente la base de datos:
  ```bash
  docker-compose down -v
  docker-compose up -d
  ```

