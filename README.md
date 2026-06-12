# Automatización Clínica IA

Sistema inteligente de gestión de pacientes para clínicas de fisioterapia desarrollado con Python, Streamlit e Inteligencia Artificial.

## Descripción

Este proyecto simula un asistente virtual capaz de atender consultas de pacientes, registrar leads automáticamente, gestionar citas y enviar confirmaciones por correo electrónico.

El objetivo es reducir tareas administrativas y mejorar la atención al paciente mediante automatización e inteligencia artificial.

---

## Funcionalidades

### Asistente conversacional con IA

* Recepción de consultas de pacientes.
* Clasificación automática de mensajes.
* Respuestas generadas mediante Claude AI.

### Gestión de Leads

* Registro automático de contactos.
* Almacenamiento en CSV.
* Sincronización con Google Sheets.
* Actualización de estados:

  * Nuevo
  * Contactado
  * Cita agendada
  * Cancelado

### Agenda Inteligente

* Reserva automática de citas.
* Creación de eventos en Google Calendar.
* Gestión de horarios.

### Confirmación por Email

* Envío automático de correos de confirmación.
* Información de fecha y hora de la cita.
* Mensajes personalizables.

### Panel de Administración

* Visualización de leads.
* Estadísticas básicas.
* Filtros por tipo de consulta.
* Descarga de datos en CSV.
* Eliminación y actualización de registros.

---

## Tecnologías Utilizadas

* Python
* Streamlit
* Claude AI (Anthropic)
* Google Calendar API
* Google Sheets API
* Gmail SMTP
* Pandas
* CSV
* GitHub

---

## Arquitectura del Sistema

Paciente

↓

Aplicación Streamlit

↓

Claude AI

↓

Registro de Lead

↓

Google Sheets

↓

Google Calendar

↓

Correo de Confirmación

---

## Ejemplo de Flujo

1. El paciente escribe una consulta.
2. La IA responde automáticamente.
3. El lead se almacena.
4. El paciente solicita una cita.
5. Se selecciona fecha y hora.
6. El sistema crea el evento en Google Calendar.
7. Se envía un correo de confirmación.
8. El estado del lead cambia a "Cita agendada".

---

## Posibles Mejoras Futuras

* Integración con WhatsApp Business.
* Recordatorios automáticos por WhatsApp.
* Integración con CRM.
* Base de datos SQL.
* Dashboard avanzado con métricas.
* Gestión de múltiples profesionales.
* Historial clínico básico.

---

## Autor

Natalia Rodríguez Martínez

Proyecto desarrollado como parte de la formación en Inteligencia Artificial, Big Data y Python, aplicando automatización de procesos reales para clínicas de fisioterapia.
