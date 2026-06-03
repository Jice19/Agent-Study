# from typing_extensions import TypedDict
# from langgraph.graph import StateGraph
# from langgraph.graph import START, END
#
# class State(TypedDict):
#     value: str
#     action_result: str
#
#
# def router(state: State):
#     if state["value"] == "end":
#         return END
#     else:
#         return "action"
#
# def decision_node(state):
#     return {"value": "keep going!"}
#
#
# def action_node(state: State):
#     # Do your action here ...
#     return {"action_result": "what a great result!"}
#
#
# workflow = StateGraph(State)
# workflow.add_node("decision", decision_node)
# workflow.add_node("action", action_node)
# workflow.add_edge(START, "decision")
# workflow.add_conditional_edges("decision", router, ["action", END])
# workflow.add_edge("action", "decision")
# app = workflow.compile()
#
# from IPython.display import Image, display
# try:
#     display(Image(app.get_graph().draw_png(output_file_path='./img/示例10.png')))
# except:
#     pass
#
# from langgraph.errors import GraphRecursionError
#
# try:
#     app.invoke({"value": "hi!"})
# except GraphRecursionError:
#     print("Recursion Error")


######

from langgraph.constants import START, END
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.managed.is_last_step import RemainingSteps

class State(TypedDict):
    value: str
    action_result: str
    remaining_steps: RemainingSteps


def router(state: State):
    print(state)
    print(f"Remaining steps: {state['remaining_steps']}")  # 调试输出
    if state["remaining_steps"] <= 2:
        return END
    if state["value"] == "end":
        return END
    else:
        return "action"

def decision_node(state):
    return {"value": "keep going!"}

def action_node(state: State):
    # Do your action here ...
    return {"action_result": "what a great result!"}


workflow = StateGraph(State)
workflow.add_node("decision", decision_node)
workflow.add_node("action", action_node)
workflow.add_edge(START, "decision")
workflow.add_conditional_edges("decision", router, ["action", END])
workflow.add_edge("action", "decision")
app = workflow.compile()

from IPython.display import display, Image
try:
    display(Image(app.get_graph().draw_png(output_file_path='./img/示例10.1.png')))
except:
    pass

from langgraph.errors import GraphRecursionError
try:
    print(app.invoke({"value": "hi!"}))
except GraphRecursionError:
    print("Recursion Error")