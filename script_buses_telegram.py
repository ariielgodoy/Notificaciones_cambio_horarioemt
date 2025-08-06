from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time

TOKEN = ""
CHAT_ID = "1461875624"
offset = 0

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print("Error al enviar mensaje por Telegram:", r.text)


def recibir_mensajes(offset):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return r.json()

def obtener_horarios(soup, sentido):
    div = soup.find("div", {"class": "listado-horarios", "id": f"horarios-{sentido}"})
    return [span.text.strip() for span in div.select("div.horas-salida span")]

def proximos_buses(lista_horas):
    ahora = datetime.now().time()
    return [h for h in lista_horas if datetime.strptime(h, "%H:%M").time() > ahora]

def guardar(nombre_archivo, ida, vuelta):
    with open(nombre_archivo, "w") as f:
        f.write("\n".join(["IDA:"] + ida + ["VUELTA:"] + vuelta))

def comparar_con_anterior(actual_ida, actual_vuelta):
    try:
        with open("horarios_anteriores.txt", "r") as f:
            anteriores = f.read().splitlines()
        actuales = ["IDA:"] + actual_ida + ["VUELTA:"] + actual_vuelta
        if actuales != anteriores:
            print("Los horarios han cambiado.")
            mensaje = "*Cambio en horario de bus*\n\nIDA:\n" + "\n".join(actual_ida) + "\n\nVUELTA:\n" + "\n".join(actual_vuelta)
        else:
            print("Los horarios no han cambiado.")
            return
    except FileNotFoundError:
        print("No se encontró un archivo anterior. Se guardará por primera vez.")
        mensaje = "Bienvenido al servicio de notificaciones. Solo está la línea E actualmente, se ampliará en un futuro."

    guardar("horarios_anteriores.txt", actual_ida, actual_vuelta)
    enviar_telegram(mensaje)

while True:

    #1. Mirar si hay mensajes nuevos dentro del bot /parar_trackeo /nueva_url_linea /empezar_trackeo
    mensaje = recibir_mensajes(offset)

    mensaje["result"][""]
    #2. Si esta activo empezar trackeo, poner un flag con timestamps y mierdas 
    # para que vaya comprobando cada 2 horas si cambia la linea

    #3. Mirar como puedo hostear el codigo para que no este en mi ordenador


    url = "https://www.emtmalaga.es/emt-mobile/horario.html?codLinea=70"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    ida = obtener_horarios(soup, "ida")
    vuelta = obtener_horarios(soup, "vuelta")
    comparar_con_anterior(ida, vuelta)
