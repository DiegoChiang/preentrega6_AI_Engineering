# Flujo de razonamiento

`AgentState` conserva una lista de mensajes con el reducer de `MessagesState`. Cada entrada del
usuario inicia en el nodo `model`.

1. El modelo analiza la solicitud y decide si cuenta con evidencia suficiente.
2. Si emite un `tool_call`, `tools_condition` dirige la ejecución a `ToolNode`.
3. La herramienta devuelve evidencia estructurada o el estado `incomplete`.
4. La arista de retorno entrega el resultado al modelo.
5. El modelo puede consultar otro componente, corregir una consulta o emitir la respuesta final.

`AsyncSqliteSaver` guarda un checkpoint después de cada superpaso. La combinación del archivo
SQLite y `thread_id` permite reanudar la conversación sin reenviar su historial completo.

La configuración `recursion_limit=10` detiene ejecuciones que no alcancen una respuesta final. Los
errores de herramienta se transforman en mensajes utilizables por el modelo para que pueda ajustar
los argumentos y realizar otro intento.
