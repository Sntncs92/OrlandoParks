import requests
import csv
from datetime import datetime
from zoneinfo import ZoneInfo
import os


# Configuración de cada parque: URL y horario de monitorización (hora inicio y fin)
PARKS = [
    {
        "name": "AnimalKingdom",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 8,
        "end_hour": 18,
        "running": True,
        "timezone": "America/New_York",
    },
    {
        "name": "EPCOT",
        "url": "https://api.themeparks.wiki/v1/entity/e957da41-3552-4cf6-b636-5babc5cbc4e5/live",
        "start_hour": 9,
        "end_hour": 21,
        "running": True,
        "timezone": "America/New_York",
    },
    {
        "name": "HollywoodStudios",
        "url": "https://api.themeparks.wiki/v1/entity/e957da41-3552-4cf6-b636-5babc5cbc4e5/live",
        "start_hour": 9,
        "end_hour": 21,
        "running": True,
        "timezone": "America/New_York",
    },
    {
        "name": "MagicKingdom",
        "url": "https://api.themeparks.wiki/v1/entity/e957da41-3552-4cf6-b636-5babc5cbc4e5/live",
        "start_hour": 9,
        "end_hour": 22,
        "running": True,
        "timezone": "America/New_York",
    },
    {
        "name": "UniversalStudios",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 9,
        "end_hour": 21,
        "running": True,
        "timezone": "America/New_York",
    },
    {
        "name": "IslandAdventure",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 9,
        "end_hour": 22,
        "running": True,
        "timezone": "America/New_York",
    },
    {
        "name": "EpicUniverse",
        "url": "https://api.themeparks.wiki/v1/entity/89db5d43-c434-4097-b71f-f6869f495a22/live",
        "start_hour": 9,
        "end_hour": 22,
        "running": True,
        "timezone": "America/New_York",
    }
]

def dentro_de_horario(start, end, now):
    h = now.hour
    if start < end:
        return start <= h < end
    else:
        return h >= start or h < end

def procesar_parque(park):
    tz = ZoneInfo(park["timezone"])
    now = datetime.now(tz)
    fecha_str = now.strftime("%Y-%m-%d")
    csv_file = f'{park["name"]}_{fecha_str}.csv'

    if dentro_de_horario(park["start_hour"], park["end_hour"], now):
        # Dentro del horario, obtener y guardar datos
        try:
            response = requests.get(park["url"])
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error al obtener datos de {park['name']}: {e}")
            return

        timestamp = now.strftime("%Y-%m-%d %H:%M")

        filas = []
        for ride in data.get("liveData", []):
            if ride.get("entityType") != "ATTRACTION":
                continue
            if ride.get("status") != "OPERATING":
                continue
            name = ride.get("name", "Sin nombre")
            wait = ride.get("queue", {}).get("STANDBY", {}).get("waitTime", "Sin datos")
            filas.append([timestamp, "ATTRACTION", name, wait])

        if filas:
            # Crear archivo con cabecera si no existe
            if not os.path.exists(csv_file):
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["FechaHora", "Tipo", "Nombre", "Espera"])

            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(filas)
            print(f"{park['name']}: Guardadas {len(filas)} filas a las {timestamp}")
        else:
            print(f"{park['name']}: No hay atracciones operativas en este momento.")

    else:
        # Fuera del horario, solo generar resumen si hay datos guardados
        if not os.path.exists(csv_file):
            print(f"{park['name']}: No hay datos aún hoy, no se genera resumen.")
            return

        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # saltar cabecera
                datos = list(reader)
        except Exception as e:
            print(f"Error leyendo CSV de {park['name']}: {e}")
            return

        if len(datos) == 0:
            print(f"{park['name']}: Archivo CSV vacío, no se genera resumen.")
            return

        atracciones = [row for row in datos if row[1] == "ATTRACTION"]
        esperas = [int(row[3]) for row in atracciones if row[3].isdigit()]

        print(f"\n{park['name']} - Resumen del día {fecha_str}")
        print("-----------------------------------")
        print(f"Total registros: {len(datos)}")
        print(f"Atracciones registradas: {len(atracciones)}")
        if esperas:
            print(f"Espera media (min): {sum(esperas) / len(esperas):.2f}")
        else:
            print("Sin datos de espera válidos")
        print("-----------------------------------\n")

def main():
    for park in parks:
        procesar_parque(park)

if __name__ == "__main__":
    main()
