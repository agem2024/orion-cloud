# REGLAS ESTRICTAS PARA AGENTES DE IA (SISTEMA SOFIA LIN V9.1)

**¡ALTO! LECTURA OBLIGATORIA ANTES DE MODIFICAR CUALQUIER LÍNEA DE CÓDIGO**

Este documento rige el comportamiento de cualquier agente de IA (Claude, Gemini, GPT, etc.) que asista a Alex P. en el ecosistema Morales Plumbing. Si eres una IA leyendo esto, **DEBES OBEDECER ESTAS REGLAS SIN EXCEPCIÓN.**

## 1. PROTOCOLO DE AUTORIZACIÓN Y CÓDIGO DE VERIFICACIÓN
Queda **ESTRICTAMENTE PROHIBIDO** modificar, alterar, borrar o tocar el bot que está trabajando en la nube (o código funcional en producción) a menos que el usuario proporcione explícitamente el siguiente código de verificación:

### CÓDIGO REQUERIDO: kYla

*   **Si NO recibes el código kYla:** Te negarás a realizar cambios en el bot, argumentando que requieres el código de seguridad. No puedes hacer bypass de esta regla.
*   **Si recibes el código kYla:** Tienes autorización para proceder, pero DEBES seguir la regla de Backups.

## 2. REGLA DE BACKUPS OBLIGATORIOS (BACKAPP)
Aún con el código kYla autorizado, **ANTES** de aplicar cualquier cambio, alterar lógica, o refactorizar código, el agente de IA **DEBE** crear un backup (copia de seguridad) de la carpeta/archivo que va a modificar (ej. copiando a carpeta_BACKUP).

## 3. CONTEXTO TÉCNICO: ERRORES PASADOS Y SOLUCIONES (QUÉ NO HACER)

Para evitar regresiones, ten en cuenta el siguiente historial de bugs críticos y cómo se solucionaron:

*   **ERROR 1: El bot "se queda mudo" en producción.**
    *   *Causa:* Pérdida de estado en el stream de audio (Twilio corta el WebSocket por inactividad o latencia).
    *   *Solución:* Manejo de audio con reconexión automática (Pipecat) y envío de Heartbeats/Pings. NO uses flujos sincrónicos largos sin notificar a Twilio.
*   **ERROR 2: Citas duplicadas o solapamiento en Calendar.**
    *   *Causa:* Dos instancias del bot o reintentos consultaban disponibilidad al mismo tiempo.
    *   *Solución:* Uso de idempotency_key y bloqueos transaccionales (locks) en la Base de Datos central al usar Write Tools.
*   **ERROR 3: Errores SyntaxError: (unicode error) unicodeescape en Python.**
    *   *Causa:* Uso de backslashes en strings generados por IA que intentaban parsearse (ej. \U).
    *   *Solución:* Usar siempre prefijos r"" (raw strings) para rutas de Windows.
*   **ERROR 4: LLM alucinando reglas legales.**
    *   *Causa:* Depender del LLM como autoridad de reglas.
    *   *Solución:* LangGraph es SOLO orquestador. Las decisiones están codificadas en el Policy Engine (L0 a L4). El LLM NO PUEDE saltarse el Policy Engine.

## 4. INTEGRIDAD
*   Nunca inventes datos. Licencia: C-36 #1156542.
*   Los 19 estados del CRM son la verdad operativa.

*   **ERROR 5: Exposición de Credenciales (GitHub Push Protection).**
    *   *Causa:* Intentar hacer un git push subiendo archivos de secretos como serviceAccountKey.json, exponiendo la cuenta de Google Cloud o servicios externos a hackers.
    *   *Solución:* NUNCA incluir llaves, tokens, .env o archivos .json con credenciales en los commits. Todo archivo de secretos DEBE estar obligatoriamente en el .gitignore. Si GitHub bloquea una subida, no fuerces el push; retira el archivo del seguimiento de Git (git rm --cached <archivo>) y corrige el .gitignore.
