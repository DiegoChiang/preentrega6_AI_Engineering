"""Grafo ReAct de un solo agente con retorno desde herramientas."""

from typing import Any

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from incident_agent.tools import TOOLS

SYSTEM_PROMPT = """Eres un agente único de diagnóstico de incidentes.
Decide autónomamente si necesitas consultar evidencia técnica antes de responder.

Reglas de investigación:
- Usa search_technical_knowledge para confirmar umbrales, procedimientos y hechos operativos.
- Ejecuta como máximo una llamada de herramienta en cada turno del modelo.
- Cada llamada debe investigar exactamente un componente técnico.
- Si una herramienta devuelve incomplete o un error, corrige la consulta y vuelve a intentarlo.
- Si la solicitud involucra varios componentes, consulta cada uno por separado antes de concluir.
- No respondas con datos técnicos que no estén respaldados por los resultados disponibles.
- La respuesta final debe citar los identificadores de las fuentes consultadas.
"""


class AgentState(MessagesState):
    """Historial acumulativo administrado por el reducer de MessagesState."""


def _tool_error(error: Exception) -> str:
    return (
        f"La herramienta falló con {type(error).__name__}: {error}. "
        "Revisa los argumentos y vuelve a intentarlo con una consulta más específica."
    )


def create_agent_graph(model: Any, checkpointer: Any) -> Any:
    """Compila el ciclo modelo → herramientas → modelo con persistencia."""

    model_with_tools = model.bind_tools(TOOLS, parallel_tool_calls=False)

    async def call_model(state: AgentState) -> dict[str, list[Any]]:
        response = await model_with_tools.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(TOOLS, handle_tool_errors=_tool_error))
    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model",
        tools_condition,
        {"tools": "tools", "__end__": END},
    )
    builder.add_edge("tools", "model")
    return builder.compile(checkpointer=checkpointer)
