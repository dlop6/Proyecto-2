import pandas as pd

# Leer el archivo resultados.csv
file_path = 'resultados.csv'
columns = [
    "event_id", "nivel", "num_usuarios", "reservas_exitosas",
    "reservas_fallidas", "errores", "bloqueos", "tiempo_promedio"
]

# Cargar los datos en un DataFrame
df = pd.read_csv(file_path, header=None, names=columns)

# Crear un cuadro comparativo agrupado por 'nivel' y 'num_usuarios'
comparative_table = df.groupby(['nivel', 'num_usuarios']).mean(numeric_only=True)

# Mostrar el cuadro comparativo
print(comparative_table)

# Guardar el cuadro comparativo en un archivo Excel
output_path = 'cuadro_comparativo.xlsx'
comparative_table.to_excel(output_path)
print(f"Cuadro comparativo guardado en {output_path}")