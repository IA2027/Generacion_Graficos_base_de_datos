import pandas as pd
import random
from pathlib import Path



VENDEDORES = [
    "Ana López", "Carlos Pérez", "María Gómez", "Juan Rodríguez",
    "Lucía Fernández", "Diego Martínez", "Sofía Romero", "Pablo Torres"
]

PRODUCTOS = {
    "Drone Mini 4K": (350, 520),
    "Drone Explorer Pro": (780, 1150),
    "Drone FPV Racer": (620, 950),
    "Drone Agriculture X": (1400, 2100),
    "Drone Cinematic 6K": (1100, 1750),
    "Drone Beginner HD": (180, 290),
}

def generar_base_de_datos(cantidad=50, archivo="ventas_drones.csv"):
    random.seed()  # datos aleatorios en cada ejecución
    filas = []

    for _ in range(cantidad):
        vendedor = random.choice(VENDEDORES)
        producto = random.choice(list(PRODUCTOS.keys()))
        precio_min, precio_max = PRODUCTOS[producto]
        precio_unitario = random.randrange(precio_min, precio_max + 1, 10)
        unidades = random.randint(1, 4)
        total_venta = unidades * precio_unitario

        filas.append({
            "Vendedor": vendedor,
            "Producto": producto,
            "Unidades": unidades,
            "Precio_unitario_USD": precio_unitario,
            "Total_venta_USD": total_venta,
        })

    df = pd.DataFrame(filas)
    ruta = Path(__file__).resolve().parent / archivo
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"Base de datos creada: {ruta}")
    print(f"Registros generados: {len(df)}")
    print(df.head(10).to_string(index=False))
    return df

if __name__ == "__main__":
    generar_base_de_datos()
