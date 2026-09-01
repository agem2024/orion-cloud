# PLAN MAESTRO DEFINITIVO DE VALIDACIÓN E2E, RESILIENCIA, SEGURIDAD Y REGRESIÓN

## SOFIA LIN — MORALES PLUMBING

### Versión 4.0 — Estándar de Validación para Producción

---

# 0. PROPÓSITO

Este documento establece el procedimiento obligatorio para determinar, mediante evidencia reproducible, si Sofia Lin funciona correctamente bajo condiciones normales, condiciones adversas y fallos de dependencias.

El objetivo no es demostrar que el sistema es infalible.

El objetivo es determinar:

* qué funciona;
* qué no funciona;
* bajo qué condiciones funciona;
* qué ocurre cuando una dependencia falla;
* cómo se recupera;
* qué datos quedan persistidos;
* qué acciones fueron ejecutadas;
* qué acciones fueron rechazadas;
* y si la versión evaluada puede avanzar a producción.

### Principio rector

> **No se declara una función operativa porque “parece funcionar”. Se declara operativa solamente cuando el escenario definido ha sido ejecutado y existe evidencia suficiente para demostrar el resultado.**

---

# 1. REGLAS ABSOLUTAS DE VALIDACIÓN

## 1.1 Estados permitidos

Toda prueba tendrá exclusivamente uno de estos estados:

* `PASSED`
* `FAILED`
* `BLOCKED`
* `NOT_EXECUTED`
* `REGRESSION`

### Regla

`BLOCKED` nunca equivale a `PASSED`.

`NOT_EXECUTED` nunca equivale a `PASSED`.

Una prueba parcialmente ejecutada no puede marcarse como `PASSED`.

---

# 2. IDENTIDAD DE LA EJECUCIÓN

Cada batería de pruebas debe generar un `TEST_RUN_ID` único.

Debe registrar:

* TEST_RUN_ID
* TEST_ID
* fecha/hora UTC
* ambiente
* commit SHA
* versión de aplicación
* versión del runtime
* versiones relevantes de dependencias
* modelo de IA realmente utilizado
* versión/configuración de API
* proveedor de infraestructura
* CallSid cuando exista
* StreamSid cuando exista
* MessageSid cuando exista
* trace_id
* duración
* resultado
* evidencia asociada

### Regla crítica

El commit probado debe coincidir con el commit desplegado.

No se permite:

> probar A → modificar B → declarar que B fue probado.

Si existe cualquier modificación posterior a la prueba, la prueba afectada debe repetirse.

---

# 3. ARQUITECTURA BAJO PRUEBA

```text
                         SOFIA LIN
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
     VOZ                MENSAJERÍA          PERSISTENCIA
    Twilio          WhatsApp / Telegram       Supabase
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                     AI / REALTIME
                            │
                            ▼
                    TOOL ENGINE / FSM
                            │
                            ▼
                    POLICY / AUTH
                            │
                            ▼
                      DISPATCH CORE
                       │          │
                       ▼          ▼
                    EMAIL      TELEGRAM
```

## Capas transversales

```text
SECURITY
AUTHORIZATION
OBSERVABILITY
TRACEABILITY
IDEMPOTENCY
TIMEOUTS
RETRIES
RATE LIMITING
FAILURE ISOLATION
CIRCUIT BREAKER
MEMORY ISOLATION
COST GUARDRAILS
AUDIT
CLEAN TEARDOWN
RECOVERY
```

---

# 4. AMBIENTES DE PRUEBA

Las pruebas se dividirán en:

## TEST

Pruebas rápidas de componentes y regresión.

## STAGING

Pruebas de integración y E2E utilizando configuración equivalente a producción.

## PRODUCTION

Únicamente pruebas autorizadas y controladas.

## REAL HUMAN CALL

Prueba final con una persona utilizando la línea telefónica real.

### Regla

Una prueba de TEST no sustituye una prueba de STAGING.

Una prueba de STAGING no sustituye una prueba de PRODUCCIÓN.

Una prueba automatizada no sustituye la prueba humana de voz.

---

# 5. FASE 0 — VERIFICACIÓN DEL BUILD

Antes de ejecutar cualquier prueba funcional:

* verificar commit;
* verificar dependencias;
* verificar variables de entorno;
* verificar modelo configurado;
* verificar endpoints;
* verificar migraciones;
* verificar configuración de producción;
* verificar secretos;
* verificar health check.

Si alguna dependencia crítica no coincide con la versión esperada:

`BLOCKED`.

---

# 6. FASE 1 — HEALTH CHECK E INFRAESTRUCTURA

Verificar:

* DNS;
* TLS;
* certificado;
* HTTP;
* WebSocket;
* memoria;
* CPU;
* conexiones;
* disponibilidad de dependencias.

Medir:

* tiempo de respuesta;
* códigos HTTP;
* errores;
* disponibilidad.

Un `HTTP 200` únicamente demuestra que ese endpoint respondió.

No demuestra que Sofia funcione.

---

# 7. FASE 2 — TWILIO: WEBHOOK Y AUTENTICACIÓN

## 7.1 Firma válida

Enviar una solicitud con:

* URL correcta;
* payload válido;
* `X-Twilio-Signature` válida.

Esperado:

* solicitud aceptada;
* TwiML válido;
* Stream URL correcta.

## 7.2 Firma inválida

Probar:

* firma alterada;
* firma incorrecta;
* payload modificado;
* URL diferente;
* firma ausente cuando sea obligatoria.

Esperado:

`HTTP 403` o el mecanismo de rechazo definido.

## 7.3 Replay

Reenviar una solicitud válida previamente utilizada.

Verificar que el sistema no genere una operación duplicada cuando la operación sea idempotente.

---

# 8. FASE 3 — TWILIO MEDIA STREAMS

Validar la secuencia real:

```text
connected
   ↓
start
   ↓
media
   ↓
audio bidireccional
   ↓
mark cuando corresponda
   ↓
stop
```

No se considera suficiente recibir solamente `start`.

---

# 9. FASE 4 — AUDIO ENTRANTE

Probar audio continuo de:

* 1 segundo;
* 5 segundos;
* 15 segundos;
* 30 segundos;
* 60 segundos.

Incluir:

* voz;
* silencio;
* números;
* nombres;
* direcciones;
* frases largas;
* pausas;
* cambios de velocidad;
* ruido razonable.

Validar:

* decodificación;
* formato;
* secuencia;
* pérdida;
* duplicación;
* orden;
* errores;
* procesamiento continuo.

---

# 10. FASE 5 — AUDIO SALIENTE

Validar:

```text
AI
 ↓
audio delta
 ↓
servidor
 ↓
conversión/formato requerido
 ↓
Twilio
 ↓
reproducción
```

Comprobar:

* audio generado;
* audio enviado;
* formato correcto;
* ausencia de payload corrupto;
* reproducción;
* `mark` cuando corresponda.

No se considera suficiente:

> “OpenAI devolvió audio.”

Debe demostrarse que el audio completó el trayecto hasta el canal telefónico.

---

# 11. FASE 6 — BARGE-IN / INTERRUPCIÓN

Esta es una prueba crítica.

Escenario:

```text
Sofia habla
      ↓
cliente comienza a hablar
      ↓
detección de speech
      ↓
cancelación de respuesta cuando corresponda
      ↓
limpieza del audio pendiente
      ↓
nuevo turno
      ↓
respuesta nueva
```

Verificar:

* detección de la voz;
* cancelación correcta;
* limpieza del audio pendiente;
* ausencia de audio residual;
* procesamiento de la nueva entrada;
* nueva respuesta.

### No utilizar como única prueba:

`speech_started → clear`

El objetivo es validar el comportamiento completo, no solamente la existencia de un evento.

---

# 12. FASE 7 — SILENCIO

Probar:

* 2 s;
* 5 s;
* 10 s;
* 20 s;
* silencio prolongado.

Verificar:

* no existe loop;
* no existen respuestas inventadas;
* no existe consumo indefinido;
* se aplican timeouts;
* se mantiene o termina la sesión según política.

---

# 13. FASE 8 — AUDIO Y PAYLOAD MALFORMADO

Probar:

* JSON inválido;
* evento desconocido;
* Base64 inválido;
* audio vacío;
* audio truncado;
* payload excesivamente grande;
* paquete duplicado;
* evento fuera de orden.

Resultado esperado:

**el proceso no debe terminar de forma inesperada.**

Debe:

* registrar;
* rechazar o aislar;
* continuar cuando sea seguro;
* o cerrar controladamente.

---

# 14. FASE 9 — DESCONEXIONES

## 14.1 OpenAI desconectado

Durante conversación activa:

```text
OpenAI falla
 ↓
Sofia detecta
 ↓
NO inventa respuesta
 ↓
fallback definido
 ↓
humano / callback / mensaje
```

## 14.2 Twilio desconectado

Verificar:

* detección;
* limpieza;
* persistencia;
* liberación de recursos.

## 14.3 Servidor reiniciado

Durante conversación activa:

* reiniciar instancia;
* verificar estado;
* verificar recursos;
* comprobar comportamiento posterior.

---

# 15. FASE 10 — STOP Y CLEAN TEARDOWN

Cuando finaliza la llamada:

verificar:

* cierre de WebSocket;
* cancelación de tareas;
* cancelación de operaciones pendientes;
* liberación de memoria;
* liberación de conexiones;
* cierre de sesión AI;
* estado final persistido;
* ausencia de tareas zombie;
* ausencia de llamadas posteriores;
* ausencia de consumo residual atribuible a la sesión.

No afirmar “limpieza completa” sin evidencia.

---

# 16. FASE 11 — CONVERSACIÓN E2E REAL

Escenario:

```text
Cliente
 ↓
problema
 ↓
triage
 ↓
preguntas
 ↓
nombre
 ↓
teléfono
 ↓
dirección
 ↓
disponibilidad
 ↓
confirmación
 ↓
tool
 ↓
Supabase
 ↓
resultado
 ↓
Sofia
 ↓
cliente
```

Validar el ciclo completo.

---

# 17. FASE 12 — TOOL ENGINE

Toda herramienta debe tener:

* nombre;
* esquema;
* parámetros;
* validaciones;
* permisos;
* precondiciones;
* resultado;
* manejo de errores;
* timeout;
* política de reintento;
* idempotencia.

El LLM no tiene autoridad directa sobre la base de datos.

Flujo obligatorio:

```text
LLM
 ↓
Tool Request
 ↓
Schema Validation
 ↓
Authorization
 ↓
Business Rules
 ↓
Tool Execution
 ↓
Result
 ↓
LLM
```

---

# 18. FASE 13 — AGENDAR_CITA

Probar:

### Datos válidos

Debe crear una única cita.

### Datos incompletos

Debe solicitar información.

### Datos inválidos

Debe rechazar.

### Cita duplicada

Debe impedir duplicación.

### Herramienta caída

Debe responder según política de fallback.

### Timeout

Debe manejarse sin crear una segunda operación accidentalmente.

---

# 19. FASE 14 — IDEMPOTENCIA

Repetir exactamente la misma operación:

```text
A
A
A
```

Validar:

* una sola cita;
* un solo identificador;
* una sola operación lógica;
* notificaciones controladas;
* ningún registro duplicado.

Esto debe probarse en:

* voz;
* WhatsApp;
* Telegram;
* webhooks;
* tool calls.

---

# 20. FASE 15 — MENSAJES FUERA DE ORDEN

Enviar:

```text
A
B
A retrasado
```

También:

```text
A
B
C
B retrasado
```

Validar que el estado final sea consistente.

No asumir simplemente que “el último mensaje recibido es el correcto”.

---

# 21. FASE 16 — WHATSAPP

Probar:

* webhook válido;
* firma válida;
* firma inválida;
* multi-turno;
* duplicados;
* mensaje fuera de orden;
* timeout;
* IA lenta;
* DB lenta;
* DB caída;
* mensaje inválido;
* reintento.

Medir:

* P50;
* P95;
* P99.

No utilizar un único número como garantía universal.

---

# 22. FASE 17 — TELEGRAM

Probar:

* webhook;
* conversación;
* memoria;
* persistencia;
* duplicados;
* eventos retrasados;
* caída del backend;
* fallo de notificación;
* recuperación.

La notificación al propietario es una operación secundaria y no debe provocar automáticamente la pérdida de la cita si la política de negocio establece lo contrario.

---

# 23. FASE 18 — CASCADA DE FALLOS

Escenario:

```text
Cliente
 ↓
Sofia
 ↓
agendar_cita
 ↓
Supabase
 ↓
OK
 ↓
Email
 ↓
FALLA
```

Resultado esperado:

* cita permanece;
* no se duplica;
* incidente registrado;
* email marcado para reintento;
* cliente recibe el resultado correspondiente;
* llamada no se cae por una falla secundaria.

---

# 24. FASE 19 — FALLA DE SUPABASE

Probar:

### Antes del INSERT

No debe confirmarse una cita inexistente.

### Durante INSERT

No debe generarse una confirmación falsa.

### Después de INSERT

No debe crearse un segundo registro por un reintento.

### Durante READ

Sofia no debe inventar los datos faltantes.

---

# 25. FASE 20 — FALLA DE EMAIL

Probar:

```text
DB OK
Email FALLA
```

Verificar:

* DB permanece;
* no hay rollback incorrecto;
* se registra incidente;
* retry controlado;
* no duplicación.

---

# 26. FASE 21 — FALLA DE TELEGRAM

Probar:

```text
DB OK
Telegram FALLA
```

La cita no debe perderse por la falla de una notificación secundaria.

---

# 27. FASE 22 — RETRIES

Cada retry debe probar:

* límite;
* backoff;
* duplicación;
* timeout;
* éxito posterior;
* fallo permanente.

No permitir retries infinitos.

---

# 28. FASE 23 — CIRCUIT BREAKER / DEPENDENCIA CAÍDA

Si una dependencia falla repetidamente:

* no continuar golpeando indefinidamente al proveedor;
* aplicar política de protección;
* registrar estado;
* recuperar cuando corresponda.

---

# 29. FASE 24 — AISLAMIENTO DE SESIONES

Ejecutar simultáneamente:

```text
Cliente A
 ↓
Sofia

Cliente B
 ↓
Sofia
```

Validar que:

* contexto A permanezca en A;
* contexto B permanezca en B;
* no existan datos cruzados;
* no existan tool calls cruzados;
* no existan registros cruzados.

No declarar “100% de aislamiento”.

Declarar:

> **“Los escenarios definidos de aislamiento fueron ejecutados sin contaminación observable.”**

---

# 30. FASE 25 — PROMPT INJECTION

Probar:

* ignorar instrucciones;
* obtener secretos;
* modificar políticas;
* crear citas sin datos;
* ejecutar herramientas no autorizadas;
* modificar precios;
* acceder a otro cliente;
* intentar obtener información interna.

El modelo puede interpretar lenguaje.

El backend controla autoridad.

---

# 31. FASE 26 — ALUCINACIONES

Solicitar información inexistente:

* precios;
* citas;
* disponibilidad;
* políticas;
* garantías;
* diagnósticos;
* inventario.

Resultado:

Sofia debe consultar una fuente autorizada o declarar que no dispone del dato.

Nunca inventar.

---

# 32. FASE 27 — FUENTE DE VERDAD

Definir explícitamente:

| Información       | Fuente              |
| ----------------- | ------------------- |
| Cliente           | Base de datos       |
| Cita              | Dispatch            |
| Precio            | PriceBook           |
| Disponibilidad    | Calendario/Dispatch |
| Inventario        | Inventario          |
| Política          | Policy Engine       |
| Estado de trabajo | Dispatch            |

El LLM no debe ser la fuente de verdad de información operacional.

---

# 33. FASE 28 — SEGURIDAD DE SECRETOS

Buscar deliberadamente:

* API keys en logs;
* tokens;
* passwords;
* AUTH_TOKEN;
* credenciales SMTP;
* credenciales Supabase;
* secretos en respuestas;
* secretos en errores;
* secretos en Git.

Resultado:

**ningún secreto debe aparecer en evidencia pública o logs no autorizados.**

---

# 34. FASE 29 — PII

Probar:

* nombre;
* teléfono;
* dirección;
* email;
* contenido de llamada.

Verificar:

* acceso;
* almacenamiento;
* logs;
* exposición;
* retención;
* eliminación según política aplicable.

---

# 35. FASE 30 — OBSERVABILIDAD

Una llamada debe poder reconstruirse mediante:

```text
trace_id
 ↓
CallSid
 ↓
StreamSid
 ↓
AI session
 ↓
tool call
 ↓
DB transaction
 ↓
email
 ↓
notification
```

Si no se puede reconstruir el incidente, la observabilidad es insuficiente.

---

# 36. FASE 31 — CONCURRENCIA

Probar escalonadamente:

* 1;
* 5;
* 10;
* 25;
* y el límite operativo real.

Medir:

* CPU;
* RAM;
* conexiones;
* latencia;
* errores;
* timeouts;
* OpenAI;
* Twilio;
* DB;
* memoria;
* costos.

No declarar una capacidad que no haya sido medida.

---

# 37. FASE 32 — RATE LIMITING

Intentar exceder:

* mensajes;
* llamadas;
* tool calls;
* solicitudes IA;
* DB.

Verificar:

* rate limit;
* rechazo controlado;
* backoff;
* alertas;
* protección de costos.

---

# 38. FASE 33 — COST GUARDRAILS

Probar:

* loop de IA;
* conversación excesivamente larga;
* tool call repetitivo;
* retry excesivo;
* dependencia caída.

Debe existir un límite operativo que evite consumo ilimitado.

---

# 39. FASE 34 — SMTP

Validar:

* TLS;
* autenticación;
* aceptación;
* contenido;
* destinatario;
* Message-ID;
* logging;
* error;
* retry;
* duplicación.

Un `250 OK` no significa necesariamente que el destinatario haya leído el correo.

El sistema debe registrar únicamente lo que realmente puede demostrar.

---

# 40. FASE 35 — PRUEBAS DE REGRESIÓN

Cada bug descubierto se convierte en un test permanente.

Ejemplo:

```text
BUG:
ClientConnection no tiene atributo .open

REGRESSION:
VOICE-REG-001
```

Ese escenario permanece en la batería futura.

Regla:

> **Un error corregido nunca vuelve a depender únicamente de memoria humana para evitar su repetición.**

---

# 41. FASE 36 — ROLLBACK

Realizar:

```text
Versión A
 ↓
Deploy B
 ↓
pruebas
 ↓
fallo
 ↓
rollback A
 ↓
smoke test
```

Validar:

* aplicación;
* DB;
* variables;
* dependencias;
* endpoints;
* estado.

---

# 42. FASE 37 — PRUEBAS DE PRODUCCIÓN CONTROLADAS

Antes de realizar la prueba:

* confirmar versión;
* confirmar commit;
* confirmar horario;
* confirmar monitoreo;
* confirmar rollback;
* confirmar responsable;
* definir duración;
* definir criterio de abortar.

---

# 43. FASE 38 — LLAMADA HUMANA REAL

La prueba final debe utilizar la línea real.

El operador debe ejecutar:

1. llamada;
2. saludo;
3. hablar mientras Sofia habla;
4. pausa;
5. explicación del problema;
6. corrección de información;
7. nombre;
8. teléfono;
9. dirección;
10. disponibilidad;
11. solicitud de cita;
12. confirmación;
13. pregunta inesperada;
14. finalización.

Debe comprobarse simultáneamente:

```text
TELÉFONO
 ↓
TWILIO
 ↓
WEBSOCKET
 ↓
AI
 ↓
AUDIO
 ↓
INTERRUPCIÓN
 ↓
TOOL
 ↓
SUPABASE
 ↓
DISPATCH
 ↓
EMAIL/TELEGRAM
 ↓
LOGS
```

---

# 44. FASE 39 — PRUEBA DE LLAMADA LARGA

Realizar llamadas de:

* 1 minuto;
* 3 minutos;
* 5 minutos;
* 10 minutos;
* duración máxima definida operacionalmente.

Medir:

* estabilidad;
* memoria;
* latencia;
* WebSocket;
* audio;
* herramientas;
* costos;
* persistencia.

---

# 45. CRITERIOS DE LATENCIA

No establecer una promesa universal.

Registrar:

* P50;
* P95;
* P99;
* máximo;
* número de muestras;
* condiciones de carga.

Para cada métrica se debe definir un objetivo operacional antes de ejecutar la prueba.

### Voz

Medir como mínimo:

**fin de habla → primer audio útil de respuesta**

y por separado:

**inicio de speech → detección de interrupción**

### Mensajería

Medir:

**recepción webhook → respuesta aceptada por el proveedor**

---

# 46. CRITERIOS DE ERROR

Para un escenario específico:

* excepciones no controladas: `0`;
* duplicaciones: `0`;
* contaminación entre sesiones: `0`;
* secretos expuestos: `0`;
* acciones no autorizadas: `0`.

Esto se refiere al escenario probado.

No constituye una promesa de que jamás ocurrirá un error en producción.

---

# 47. CLASIFICACIÓN

## P0 — CRÍTICO

Ejemplos:

* fuga de información;
* acción no autorizada;
* mezcla de clientes;
* pérdida de cita;
* confirmación falsa;
* llamada inutilizable;
* herramienta ejecutada incorrectamente;
* secreto expuesto.

Resultado:

**NO-GO**

## P1 — ALTO

Ejemplos:

* barge-in defectuoso;
* pérdida importante de contexto;
* timeout crítico;
* recuperación incorrecta.

Resultado:

**NO-GO**

## P2 — MEDIO

Ejemplo:

* email secundario fallido con cita correctamente persistida y recuperación disponible.

Resultado:

**GO condicionado únicamente si el riesgo ha sido formalmente aceptado y existe mitigación.**

## P3 — BAJO

Problemas no funcionales o cosméticos.

Puede liberarse con observación.

---

# 48. CRITERIOS DE GO

No existe ningún P0 abierto.

No existe ningún P1 abierto.

Todos los flujos críticos E2E están aprobados.

Las pruebas de:

* voz;
* audio bidireccional;
* barge-in;
* herramientas;
* persistencia;
* idempotencia;
* seguridad;
* aislamiento;
* recuperación;

han sido ejecutadas.

El commit probado coincide con producción.

La prueba humana real fue completada.

Existe evidencia suficiente para reconstruir cada prueba crítica.

---

# 49. CRITERIOS DE NO-GO

Cualquiera de los siguientes obliga a detener la liberación:

* prueba crítica `FAILED`;
* prueba crítica `BLOCKED` sin alternativa aceptada;
* versión diferente entre prueba y producción;
* fuga de secreto;
* fuga de PII;
* mezcla de clientes;
* cita duplicada;
* confirmación falsa;
* tool call no autorizado;
* llamada sin audio funcional;
* barge-in defectuoso en escenario crítico;
* pérdida de datos;
* rollback no funcional.

---

# 50. FORMATO OBLIGATORIO DE EVIDENCIA

Cada prueba deberá producir:

```text
========================================================
TEST RUN ID:
TEST ID:
DATE/TIME UTC:
ENVIRONMENT:
COMMIT SHA:
APPLICATION VERSION:
RUNTIME VERSION:
AI MODEL:
API VERSION:
========================================================

TRACE ID:
CALL SID:
STREAM SID:
MESSAGE SID:

INPUT:
[Payload exacto]

HEADERS:
[Headers relevantes]

RAW RESPONSE:
[Respuesta exacta]

EVENT SEQUENCE:
[Eventos en orden]

LATENCY:
P50:
P95:
P99:
MAX:

DATABASE RESULT:
[Resultado]

TOOL RESULT:
[Resultado]

ERRORS:
[Errores]

LOG EVIDENCE:
[Logs relacionados]

FINAL STATE:
[Estado]

RESULT:
PASSED / FAILED / BLOCKED / NOT_EXECUTED / REGRESSION
========================================================
```

---

# 51. REGLA SOBRE LOS LOGS

Los logs deben permitir responder:

* qué ocurrió;
* cuándo;
* dónde;
* con qué versión;
* con qué sesión;
* con qué usuario;
* qué herramienta se ejecutó;
* quién autorizó;
* qué resultado produjo;
* qué falló;
* cómo se recuperó.

Pero nunca deben exponer secretos innecesariamente.

---

# 52. REGLA SOBRE DATOS DE PRUEBA

Los datos de prueba deben ser identificables.

Ejemplo:

```text
TEST-VOICE-001
TEST-WA-001
TEST-TG-001
TEST-BOOKING-001
```

Las pruebas destructivas deben ejecutarse preferentemente en TEST/STAGING.

En producción, cualquier dato creado para pruebas debe tener:

* identificación inequívoca;
* autorización;
* procedimiento de cleanup;
* evidencia de eliminación o conservación controlada.

No se debe asumir que un `DELETE` exitoso significa que todo rastro relacionado fue eliminado.

---

# 53. REGLA DE CAUSA RAÍZ

Nunca escribir:

> “Causa raíz identificada y solucionada”

únicamente porque apareció un error conocido.

La afirmación solamente puede utilizarse cuando exista:

```text
ERROR
 ↓
REPRODUCCIÓN
 ↓
CAUSA RAÍZ
 ↓
FIX
 ↓
COMMIT
 ↓
TEST QUE FALLABA ANTES
 ↓
TEST QUE PASA DESPUÉS
 ↓
REGRESIÓN
 ↓
DEPLOY
 ↓
VERIFICACIÓN
```

Si falta cualquiera de los elementos críticos:

> **“Corrección implementada; validación pendiente.”**

---

# 54. REGLA CONTRA FALSOS POSITIVOS

Nunca considerar suficiente:

> HTTP 200.

Nunca considerar suficiente:

> WebSocket conectado.

Nunca considerar suficiente:

> OpenAI respondió.

Nunca considerar suficiente:

> Se recibió `media`.

Nunca considerar suficiente:

> Se recibieron 5 chunks.

Nunca considerar suficiente:

> Se creó una cita.

Nunca considerar suficiente:

> SMTP devolvió 250.

Nunca considerar suficiente:

> Una prueba simulada pasó.

La prueba debe atravesar el flujo que realmente se pretende declarar operativo.

---

# 55. DEFINICIÓN DE ÉXITO REAL

Para una función crítica:

```text
INPUT
 ↓
AUTHENTICATION
 ↓
VALIDATION
 ↓
PROCESSING
 ↓
AI
 ↓
TOOL
 ↓
AUTHORIZATION
 ↓
DATABASE
 ↓
EXTERNAL SERVICES
 ↓
USER RESPONSE
 ↓
OBSERVABILITY
 ↓
CLEANUP
```

Si el escenario requiere alguno de esos pasos y no fue probado, el escenario no está completamente validado.

---

# 56. ORDEN FINAL DE EJECUCIÓN

```text
1. BUILD VERIFICATION
        ↓
2. INFRASTRUCTURE
        ↓
3. SECURITY
        ↓
4. TWILIO WEBHOOK
        ↓
5. WEBSOCKET
        ↓
6. AUDIO
        ↓
7. BARGE-IN
        ↓
8. STOP / CLEANUP
        ↓
9. AI CONVERSATION
        ↓
10. TOOLS
        ↓
11. SUPABASE
        ↓
12. EMAIL
        ↓
13. WHATSAPP
        ↓
14. TELEGRAM
        ↓
15. IDEMPOTENCY
        ↓
16. OUT-OF-ORDER
        ↓
17. FAILURE INJECTION
        ↓
18. SECURITY / PROMPT INJECTION
        ↓
19. CONCURRENCY
        ↓
20. COST / RATE LIMIT
        ↓
21. RECOVERY
        ↓
22. ROLLBACK
        ↓
23. STAGING E2E
        ↓
24. PRODUCTION SMOKE TEST
        ↓
25. REAL HUMAN CALL
        ↓
26. GO / NO-GO
```

---

# 57. INFORME FINAL DE LIBERACIÓN

El informe final debe responder exclusivamente:

### ¿Qué versión se probó?

### ¿Qué pruebas se ejecutaron?

### ¿Cuáles PASSED?

### ¿Cuáles FAILED?

### ¿Cuáles BLOCKED?

### ¿Qué errores fueron encontrados?

### ¿Qué correcciones fueron aplicadas?

### ¿Qué regresiones fueron ejecutadas?

### ¿Qué evidencia existe?

### ¿Qué riesgos permanecen?

### ¿Puede liberarse?

Resultado final:

```text
GO
```

o

```text
NO-GO
```

No utilizar:

* “casi listo”;
* “debería funcionar”;
* “parece estable”;
* “100% solucionado”;
* “sin problemas conocidos” sin evidencia;
* “producción validada” si solamente se ejecutaron pruebas parciales.

---

# 58. ESTÁNDAR DEFINITIVO DE SOFIA LIN

La regla operacional permanente será:

> **Toda modificación de código, configuración, prompt, modelo, API, herramienta, integración, dependencia o infraestructura que pueda afectar un flujo crítico deberá ejecutar las pruebas de regresión correspondientes antes de volver a declarar ese flujo operativo.**

Un sistema que pasa hoy no queda automáticamente validado para siempre.

La validación pertenece a una **versión concreta bajo condiciones concretas**.

---

# 59. CONCLUSIÓN

Este documento no promete una Sofia Lin “infalible”.

Establece algo técnicamente más útil:

**un sistema de validación que obliga a demostrar el comportamiento real y evita que una prueba parcial sea presentada como una prueba completa.**

La declaración:

> **“Sofia Lin está validada para producción”**

solamente podrá emitirse cuando la evidencia demuestre que la versión específica evaluada superó los criterios definidos de funcionalidad, seguridad, resiliencia, persistencia, aislamiento, recuperación y operación real.

Hasta entonces:

> **VALIDACIÓN PENDIENTE.**
