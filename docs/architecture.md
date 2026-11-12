# Arquitectura del orquestador

## Responsabilidades

`Supervisor` recibe un resumen del estado y devuelve `RouteDecision`, un contrato Pydantic cuyo
`next_agent` solo admite nodos existentes. La decision conserva una justificacion y una instruccion
especifica para el especialista.

`ResearchAgent` consulta una base documental local mediante `search_incident_knowledge`. Su salida
mantiene cada hallazgo separado, con metricas e identificador de fuente.

`AnalysisAgent` agrega las metricas recuperadas e invoca `calculate_incident_priority`. La formula
pondera tasa de errores, latencia p95, usuarios afectados y duracion. El modelo explica los factores
y propone una mitigacion, pero no altera el resultado numerico de la herramienta.

`validate_result` aplica controles reproducibles sobre cobertura, trazabilidad y rango. La aprobacion
queda en `task_completed`; cualquier observacion queda en `validation_feedback`.

`Synthesizer` solo se ejecuta tras la aprobacion y recibe el pedido original, la evidencia y el
analisis. No recibe metadata interna ni todo el historial de mensajes.

## Decisiones de control

El modelo propone la ruta, y una guarda verifica sus prerrequisitos:

1. Sin evidencia, el destino es `researcher`.
2. Con evidencia y sin analisis, el destino es `analyst`.
3. Con ambos resultados y sin aprobacion, el destino es `validator`.
4. Con aprobacion, el destino es `synthesizer`.

El modelo conserva la capacidad de elegir refinamientos cuando existe feedback. Las guardas evitan
saltos invalidos y el contador `supervisor_steps` detiene una ejecucion que exceda ocho decisiones.

## Aislamiento de contexto

Los especialistas no reciben el historial completo. El investigador recibe la solicitud, su
instruccion y el resultado de su herramienta. El analista recibe la instruccion, las metricas, el
calculo y las fuentes. El supervisor observa solo un resumen de completitud y validacion.
