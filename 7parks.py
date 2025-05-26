import requests
import csv
import schedule
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# Zona horaria de Nueva York para coherencia con horarios del parque
zona_est = ZoneInfo("America/New_York")

# Configuración de cada parque: URL y horario de monitorización (hora inicio y fin)
PARKS = [
    {
        "name": "AnimalKingdom",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 8,
        "end_hour": 18,
        "running": True
    },
    {
        "name": "EPCOT",
        "url": "https://api.themeparks.wiki/v1/entity/e957da41-3552-4cf6-b636-5babc5cbc4e5/live",
        "start_hour": 9,
        "end_hour": 21,
        "running": True
    },
    {
        "name": "HollywoodStudios",
        "url": "https://api.themeparks.wiki/v1/entity/e957da41-3552-4cf6-b636-5babc5cbc4e5/live",
        "start_hour": 9,
        "end_hour": 21,
        "running": True
    },
    {
        "name": "MagicKingdom",
        "url": "https://api.themeparks.wiki/v1/entity/e957da41-3552-4cf6-b636-5babc5cbc4e5/live",
        "start_hour": 9,
        "end_hour": 22,
        "running": True
    },
    {
        "name": "UniversalStudios",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 9,
        "end_hour": 21,
        "running": True
    },
    {
        "name": "IslandAdventure",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 9,
        "end_hour": 22,
        "running": True
    },
    {
        "name": "EpicUniverse",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 9,
        "end_hour": 22,
        "running": True
    }
]

def en_horario(start_hour, end_hour, now):
    hora = now.hour
    if start_hour < end_hour:
        return start_hour <= hora < end_hour
    else:
        # Cruza medianoche
        return hora >= start_hour or hora < end_hour

def obtener_tiempos(parque):
    url = parque["url"]
    nombre_parque = parque["name"]

    # Fecha con formato YYYY-MM-DD con zona horaria EST (Nueva York)
    now = datetime.now(tz=zona_est)
    fecha_str = now.strftime("%Y-%m-%d")
    csv_file = f"{nombre_parque}_{fecha_str}.csv"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error al obtener datos de {nombre_parque}: {e}")
        return

    timestamp = now.strftime("%Y-%m-%d %H:%M")

    nuevas_filas = []

    for ride in data.get("liveData", []):
        if ride.get("entityType") != "ATTRACTION":
            continue
        if ride.get("status") != "OPERATING":
            continue
        name = ride.get("name", "Sin nombre")
        queue = ride.get("queue", {})
        standby = queue.get("STANDBY")
        wait = standby.get("waitTime") if standby else None
        nuevas_filas.append([timestamp, ride.get("entityType", ""), name, wait if wait is not None else "Sin datos"])

    if not nuevas_filas:
        print(f"No hay datos válidos para {nombre_parque} a las {timestamp}")
        return

    # Crear archivo y cabecera si no existe
    try:
        with open(csv_file, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["FechaHora", "Tipo", "Nombre", "Espera"])
    except FileExistsError:
        pass

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(nuevas_filas)

    print(f"✅ {len(nuevas_filas)} registros guardados para {nombre_parque} a las {timestamp}")

def main():
    resumen_generado = {parque["name"]: False for parque in PARKS}
    finalizados = {parque["name"]: False for parque in PARKS}

    while True:
        now = datetime.now(tz=zona_est)

        for parque in PARKS:
            nombre = parque["name"]
            if finalizados[nombre]:
                continue

            if en_horario(parque["start_hour"], parque["end_hour"], now):
                resumen_generado[nombre] = False
                obtener_tiempos(parque)
            else:
                # Solo generar resumen si no se ha hecho y la hora está fuera de rango tras la jornada
                if not resumen_generado[nombre]:
                    print(f"\n📊 Resumen final para {nombre} ({now.strftime('%Y-%m-%d')})")
                    # Aquí podrías agregar función para leer CSV y hacer resumen, si quieres
                    resumen_generado[nombre] = True
                    finalizados[nombre] = True
                    print(f"🛑 Monitorización finalizada para {nombre}\n")

        # Si todos los parques han finalizado, termina el script
        if all(finalizados.values()):
            print("✅ Monitorización de todos los parques finalizada.")
            break

        time.sleep(900)  # Esperar 15 minutos

if __name__ == "__main__":
    main()
