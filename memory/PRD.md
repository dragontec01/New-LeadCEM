# PRD — Modernización WhatCEM (Inicio Sprint 1)

## Problema original del usuario
- Analizar el sistema legado y proponer modernización integral.
- Potenciar funcionalidades con IA, mejores reportes/dashboards tipo BI.
- Iniciar Sprint 1 con enfoque en:
  - ruleta de asignación de vendedores para nuevos leads,
  - notificación por WhatsApp al vendedor,
  - integraciones de mensajería (Twilio y Gupshup),
  - base para campañas masivas WhatsApp y llamadas salientes IA con Twilio Voice.
- Solicitud actual: crear documentación y base de conocimiento funcional para configuraciones de usuario.

## Decisiones de arquitectura (alto nivel)
- Estrategia de modernización incremental sobre arquitectura modular por dominios.
- Separación funcional propuesta: distribución de leads, notificaciones, proveedores de mensajería, campañas y auditoría.
- Capa de abstracción de proveedores (Twilio/Gupshup) para fallback y portabilidad.
- Gobernanza por roles (Super Admin, Admin Empresa, Vendedor/Agente) y trazabilidad completa de eventos.

## Implementado en esta iteración
- Creado: `/app/WhatCEM_Powerchat/docs/01_documentacion_general_modernizacion_whatcem.md`
  - alcance de Sprint 1,
  - arquitectura funcional,
  - flujo operativo,
  - KPIs,
  - riesgos y mitigaciones,
  - definición de éxito y roadmap Sprint 2+.
- Creado: `/app/WhatCEM_Powerchat/docs/02_base_conocimiento_configuracion_usuarios.md`
  - guía de roles y permisos,
  - checklist de configuración de usuarios,
  - reglas de ruleta,
  - plantillas de notificación,
  - setup Twilio/Gupshup,
  - troubleshooting y buenas prácticas operativas.

## Backlog priorizado

### P0 (crítico, siguiente ejecución)
- Implementar motor de ruleta de asignación (round-robin + disponibilidad).
- Persistir historial de asignación y auditoría por lead.
- Implementar notificación WhatsApp al vendedor asignado con trazabilidad de estado.
- Crear módulo de configuración de integraciones Twilio/Gupshup (credenciales + test de conexión).

### P1 (alto valor)
- Fallback automático entre proveedores de mensajería.
- Dashboard operativo de asignaciones/notificaciones (SLA, entrega, fallos).
- Reglas avanzadas de asignación (ponderado por capacidad y por equipo).

### P2 (expansión)
- Campañas masivas WhatsApp con segmentación avanzada.
- Campañas de llamadas salientes IA (Twilio Voice + prompt + credenciales IA).
- Nodos IA de voz y asistente en constructor de flujos.
- Dashboards BI ejecutivos y comerciales con insights IA.

## Próximas tareas inmediatas
1. Definir esquema de datos para `assignment_rules`, `lead_assignments`, `notification_events`.
2. Crear endpoints base de ruleta y notificación.
3. Construir pantalla inicial de configuración de ruleta por empresa.
4. Integrar prueba real de envío con Twilio/Gupshup según credenciales disponibles.
