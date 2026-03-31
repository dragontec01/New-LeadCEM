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
- Backend Sprint 1 (base funcional):
  - Nuevo schema: `/app/WhatCEM_Powerchat/shared/db/schema/lead_assignment.ts`
    - `lead_assignment_rules`
    - `lead_assignment_state`
    - `lead_assignment_events`
  - Nuevo migration SQL: `/app/WhatCEM_Powerchat/migrations/109-add-lead-assignment-and-gupshup.sql`
  - Nuevo canal soportado en schema: `whatsapp_gupshup` en `shared/db/schema/assigns.ts`
  - Nuevo servicio: `/app/WhatCEM_Powerchat/server/services/channels/whatsapp-gupshup.ts`
  - Nuevo router: `/app/WhatCEM_Powerchat/server/routes/lead-assignment.ts`
    - `GET /api/lead-assignment/rules`
    - `POST /api/lead-assignment/rules`
    - `GET /api/lead-assignment/events`
    - `POST /api/lead-assignment/conversations/:id/assign-next`
    - `POST /api/lead-assignment/notifications/test`
  - Integración del router en `server/routes.ts`.
- Frontend Sprint 1 (operación inicial):
  - Nueva página: `/app/WhatCEM_Powerchat/client/src/pages/lead-assignment.tsx`
    - Configuración de reglas de ruleta
    - Prueba de notificación
    - Ejecución manual de asignación por conversationId
    - Tabla de eventos recientes
  - Nueva ruta de app: `/settings/lead-assignment` en `client/src/App.tsx`.
  - Nuevo acceso en sidebar: `Lead Router IA` en `client/src/components/layout/Sidebar.tsx`.
  - Nuevo formulario de integración: `/app/WhatCEM_Powerchat/client/src/components/settings/GupshupWhatsAppForm.tsx`.
  - Integración en Settings para canal `WhatsApp Gupshup` (card + modal + channel info).
  - Mejora de testabilidad: `data-testid` agregados en tarjetas “Add New Channel”, incluyendo Gupshup.
  - Limpieza técnica: removida duplicación de `initializeGoogleTranslateCompatibility()` en `client/src/App.tsx`.

## Resultado de testing y estado
- Se ejecutó testing agent y reportó **bloqueo de entorno**: la URL pública configurada en `/app/frontend/.env` apunta a otra app placeholder y no al despliegue de WhatCEM.
- Consecuencia: endpoints nuevos (`/api/lead-assignment/*`) y UI nueva no se pudieron validar e2e sobre esa URL.
- Se actualizó `/app/memory/test_credentials.md` con credenciales proporcionadas por el usuario para futuras pruebas autenticadas.

## Backlog priorizado

### P0 (crítico, siguiente ejecución)
- Conectar UI admin para configuración de reglas de ruleta y test de notificaciones.
- Crear CRUD de conexiones `whatsapp_gupshup` y `whatsapp_twilio` desde panel de canales.
- Ejecutar migración 109 en ambiente de staging/producción.
- Validar extremo a extremo: asignación automática + notificación WhatsApp en datos reales.

### P0 operativo inmediato (desbloqueo QA)
- Corregir mapeo de URL de pruebas para que apunte al despliegue real de WhatCEM.
- Re-ejecutar testing e2e de Sprint 1 sobre entorno correcto (backend + frontend).

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
