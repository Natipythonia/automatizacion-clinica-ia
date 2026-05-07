from datetime import datetime
from anthropic import Anthropic
import os
from dotenv import load_dotenv
load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

mensaje = input("Escribe el mensaje del paciente: ")
nombre = input("Escribe tu nombre: ")

mensaje_lower = mensaje.lower()
fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

if "cita" in mensaje_lower:
    prompt = f"""
Eres el asistente de una clínica de fisioterapia.

El paciente quiere pedir una cita.

Responde de forma breve, amable y profesional.
Invita a reservar una valoración y anima a concretar disponibilidad.

Paciente: {nombre}
Mensaje: {mensaje}

Respuesta:
"""
elif "dolor" in mensaje_lower:
    prompt = f"""
Eres el asistente de una clínica de fisioterapia.

El paciente comenta dolor o molestias físicas.

Responde de forma profesional, cercana y útil.
No diagnostiques de forma concluyente.
Sugiere valoración presencial si procede.
Puedes dar consejos generales prudentes, sin sustituir atención profesional.

Paciente: {nombre}
Mensaje: {mensaje}

Respuesta:
"""
else:
    prompt = f"""
Eres el asistente de una clínica de fisioterapia.

El paciente hace una consulta general.

Responde de forma breve, amable y profesional.
Ofrece ayuda e invita a explicar mejor su caso o a pedir cita si lo desea.

Paciente: {nombre}
Mensaje: {mensaje}

Respuesta:
"""

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

respuesta = response.content[0].text

print("\nRespuesta automática:")
print(respuesta)

if "cita" in mensaje_lower:
    archivo_nombre = "citas.txt"
elif "dolor" in mensaje_lower:
    archivo_nombre = "dolor.txt"
else:
    archivo_nombre = "otros.txt"

with open(archivo_nombre, "a", encoding="utf-8") as archivo:
    archivo.write(f"[{fecha}] {nombre}: {mensaje}\n")
    archivo.write(f"Respuesta IA: {respuesta}\n")
    archivo.write("-" * 50 + "\n")