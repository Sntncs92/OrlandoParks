# Theme Parks Queue Monitor

Este proyecto contiene un script en Python para consultar periódicamente la API de Theme Parks Wiki y guardar los tiempos de espera en varios parques temáticos en archivos CSV separados.  

El script controla horarios específicos para cada parque y genera un resumen diario. Está diseñado para ejecutarse como un servicio programado (cron job) en Render.com o cualquier otro servicio que soporte tareas recurrentes.

---

## Características

- Consulta la API cada 15 minutos durante el horario de apertura de cada parque.
- Filtra solo atracciones en estado operativo.
- Guarda los datos en archivos CSV por parque y día.
- Genera un resumen con el número total de registros y el tiempo medio de espera.
- Soporta múltiples parques con diferentes horarios y URLs.
- Se puede desplegar en Render como un Cron Job para automatizar la ejecución sin necesidad de mantener un ordenador encendido.

---

## Requisitos

- Python 3.9+
- Paquetes Python:  
  - requests  
  - schedule  

Estos están incluidos en `requirements.txt`.

