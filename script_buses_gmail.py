from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText

# Paso 1: Obtener HTML
url = "https://www.emtmalaga.es/emt-mobile/horario.html?codLinea=70"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

# Paso 2: Extraer horarios
def obtener_horarios(soup, sentido):
    div = soup.find("div", {"class": "listado-horarios", "id": f"horarios-{sentido}"})
    return [span.text.strip() for span in div.select("div.horas-salida span")]

ida = obtener_horarios(soup, "ida")
vuelta = obtener_horarios(soup, "vuelta")

# Paso 3: Filtrar los que quedan hoy
def proximos_buses(lista_horas):
    ahora = datetime.now().time()
    return [h for h in lista_horas if datetime.strptime(h, "%H:%M").time() > ahora]

print("Próximos buses IDA:", proximos_buses(ida))
print("Próximos buses VUELTA:", proximos_buses(vuelta))

# Paso 4: Guardar y comparar
def guardar(nombre_archivo, ida, vuelta):
    with open(nombre_archivo, "w") as f:
        f.write("\n".join(["IDA:"] + ida + ["VUELTA:"] + vuelta))


def enviar_gmail(actuales, nuevo):
    if nuevo is not True:
        remitente = ""
        destinatario = ""

        asunto = "Cambio en horario de bus"
        cuerpo = f"El horario de buses actual es: \n {actuales}"

        mensaje = MIMEText(cuerpo, "plain", "utf-8")
        mensaje["Subject"] = asunto
        mensaje["From"] = remitente
        mensaje["To"] = destinatario
    else:
        remitente = ""
        destinatario = ""

        asunto = "Bienvenido al servicio de notificaciones"
        cuerpo = "Solo está la línea E actualmente, sin embargo, se va a ampliar en un futuro"

        mensaje = MIMEText(cuerpo, "plain", "utf-8")
        mensaje["Subject"] = asunto
        mensaje["From"] = remitente
        mensaje["To"] = destinatario

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, "")
            servidor.sendmail(remitente, destinatario, mensaje.as_string())




def comparar_con_anterior(actual_ida, actual_vuelta):
    try:
        with open("horarios_anteriores.txt", "r") as f:
            anteriores = f.read().splitlines()
        actuales = ["IDA:"] + actual_ida + ["VUELTA:"] + actual_vuelta
        if actuales != anteriores:
            print("Los horarios han cambiado.")
            nuevo = False    
        else:
            print("Los horarios no han cambiado.")
    except FileNotFoundError:
        print("No se encontró un archivo anterior. Se guardará por primera vez.")
        nuevo = True

    guardar("horarios_anteriores.txt", actual_ida, actual_vuelta)
    with open("horarios_anteriores.txt", "r") as f:
            anteriores = f.read().splitlines()
            actuales = ["IDA:"] + actual_ida + ["VUELTA:"] + actual_vuelta
    enviar_gmail(actuales, nuevo)

while True:
    comparar_con_anterior(ida, vuelta)
    time.sleep(7200)
