"""
Servicio de recordatorios automáticos de citas.

Ejecutar en paralelo con la app Streamlit:
    python recordatorios.py

Comprueba cada 5 minutos si hay citas próximas y envía:
  - Email recordatorio 24h antes
  - Email recordatorio 2h antes
  - WhatsApp recordatorio 24h antes  (requiere TWILIO_ENABLED=true en .env)
  - WhatsApp recordatorio 2h antes   (requiere TWILIO_ENABLED=true en .env)
"""

import os
import csv
import time
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CITAS = os.path.join(BASE_DIR, "..", "citas_programadas.csv")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# ──────────────────────────────────────────────────────────────────────────────
# WhatsApp via Twilio
# Activar cuando el cliente tenga número: poner TWILIO_ENABLED=true en .env
# y rellenar TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y TWILIO_WHATSAPP_FROM.
# ──────────────────────────────────────────────────────────────────────────────
TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

CABECERAS_CSV = [
    "nombre", "email", "telefono", "fecha_hora",
    "recordatorio_24h_enviado", "recordatorio_2h_enviado",
]


def _asegurar_csv():
    if not os.path.exists(RUTA_CITAS):
        with open(RUTA_CITAS, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CABECERAS_CSV).writeheader()


def _leer_citas():
    _asegurar_csv()
    with open(RUTA_CITAS, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _guardar_citas(citas):
    with open(RUTA_CITAS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CABECERAS_CSV)
        writer.writeheader()
        writer.writerows(citas)


# ──────────────────────────────────────────────────────────────────────────────
# Email
# ──────────────────────────────────────────────────────────────────────────────

def _enviar_email(email, nombre, fecha_hora, horas_antes):
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print(f"[Email] Credenciales no configuradas. No se envió a {email}.")
        return

    if horas_antes == 2:
        asunto = "Tu cita es en 2 horas — Clínica de Fisioterapia"
        detalle = "¡Nos vemos en un momento! Si necesitas algo, llámanos."
    else:
        asunto = "Recordatorio: tu cita es mañana — Clínica de Fisioterapia"
        detalle = "Es mañana a la misma hora. ¡Te esperamos!"

    cuerpo = f"""Hola {nombre},

Te recordamos tu cita en nuestra clínica de fisioterapia:

  📅 Fecha: {fecha_hora.strftime('%d/%m/%Y')}
  🕐 Hora:  {fecha_hora.strftime('%H:%M')}

{detalle}

Si necesitas cancelar o cambiar la cita, responde a este email con antelación suficiente.

Un saludo,
Clínica de Fisioterapia
"""

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = email
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, email, msg.as_string())


# ──────────────────────────────────────────────────────────────────────────────
# WhatsApp
# ──────────────────────────────────────────────────────────────────────────────

def _enviar_whatsapp(telefono, nombre, fecha_hora, horas_antes):
    """
    Envía recordatorio por WhatsApp via Twilio.

    Para activar:
      1. pip install twilio
      2. En .env: TWILIO_ENABLED=true
      3. En .env: rellenar TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
      4. En .env: TWILIO_WHATSAPP_FROM=whatsapp:+TUNUM ERO_TWILIO
    """
    if not TWILIO_ENABLED:
        print(
            f"[WhatsApp] Pendiente de activar (TWILIO_ENABLED=false). "
            f"Se habría enviado recordatorio {horas_antes}h a {telefono}."
        )
        return

    try:
        from twilio.rest import Client  # noqa: import dentro de guard
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        if horas_antes == 2:
            texto = (
                f"Hola {nombre} 👋 Te recordamos tu cita de fisioterapia "
                f"hoy a las {fecha_hora.strftime('%H:%M')}. ¡Nos vemos en 2 horas!"
            )
        else:
            texto = (
                f"Hola {nombre} 👋 Te recordamos tu cita de fisioterapia "
                f"mañana {fecha_hora.strftime('%d/%m/%Y')} a las {fecha_hora.strftime('%H:%M')}. "
                f"¡Te esperamos!"
            )

        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{telefono}",
            body=texto,
        )
        print(f"[WhatsApp] Recordatorio {horas_antes}h enviado a {telefono}.")
    except ImportError:
        print("[WhatsApp] Librería 'twilio' no instalada. Ejecuta: pip install twilio")
    except Exception as e:
        print(f"[WhatsApp] Error al enviar a {telefono}: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Bucle principal
# ──────────────────────────────────────────────────────────────────────────────

def comprobar_y_enviar():
    citas = _leer_citas()
    if not citas:
        return

    ahora = datetime.now()
    modificado = False

    for cita in citas:
        try:
            fecha_hora = datetime.fromisoformat(cita["fecha_hora"])
        except (ValueError, KeyError):
            continue

        tiempo_restante = fecha_hora - ahora

        # Recordatorio 24h — ventana entre 25h y 23h antes para no perder la ventana
        if (
            cita.get("recordatorio_24h_enviado") != "si"
            and timedelta(hours=23) <= tiempo_restante <= timedelta(hours=25)
        ):
            try:
                _enviar_email(cita["email"], cita["nombre"], fecha_hora, 24)
                if cita.get("telefono"):
                    _enviar_whatsapp(cita["telefono"], cita["nombre"], fecha_hora, 24)
                cita["recordatorio_24h_enviado"] = "si"
                modificado = True
                print(f"[Recordatorio 24h] Enviado → {cita['email']} ({cita['nombre']})")
            except Exception as e:
                print(f"[Error 24h] {cita['email']}: {e}")

        # Recordatorio 2h — ventana entre 2h15 y 1h45 antes
        if (
            cita.get("recordatorio_2h_enviado") != "si"
            and timedelta(hours=1, minutes=45) <= tiempo_restante <= timedelta(hours=2, minutes=15)
        ):
            try:
                _enviar_email(cita["email"], cita["nombre"], fecha_hora, 2)
                if cita.get("telefono"):
                    _enviar_whatsapp(cita["telefono"], cita["nombre"], fecha_hora, 2)
                cita["recordatorio_2h_enviado"] = "si"
                modificado = True
                print(f"[Recordatorio 2h]  Enviado → {cita['email']} ({cita['nombre']})")
            except Exception as e:
                print(f"[Error 2h] {cita['email']}: {e}")

    if modificado:
        _guardar_citas(citas)


if __name__ == "__main__":
    print("=" * 60)
    print("  Servicio de recordatorios — Clínica de Fisioterapia")
    print("  Comprobando citas cada 5 minutos...")
    print(f"  WhatsApp: {'ACTIVADO' if TWILIO_ENABLED else 'desactivado (TWILIO_ENABLED=false)'}")
    print("=" * 60)

    while True:
        try:
            comprobar_y_enviar()
        except Exception as e:
            print(f"[Error general] {e}")
        time.sleep(300)
