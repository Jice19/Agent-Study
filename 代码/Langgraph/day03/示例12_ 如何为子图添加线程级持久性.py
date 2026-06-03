"""定义一个包含单个子图节点的简单图"""
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

class SubgraphState(TypedDict):
    foo: str  # note that this key is shared with the parent graph state
    bar: str

def subgraph_node_1(state: SubgraphState):
    return {"bar": "bar"}

def subgraph_node_2(state: SubgraphState):
    # note that this node is using a state key ('bar') that is only available in the subgraph
    # and is sending update on the shared state key ('foo')
    return {"foo": state["foo"] + state["bar"]}


subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()




class State(TypedDict):
    foo: str

def node_1(state: State):
    return {"foo": "hi! " + state["foo"]}


builder = StateGraph(State)
builder.add_node("node_1", node_1)
# note that we're adding the compiled subgraph as a node to the parent graph
builder.add_node("node_2", subgraph)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")


# 使用内存检查点器（ MemorySaver ）编译该图
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


from IPython.display import Image, display
try:
    display(Image(graph.get_graph().draw_png(output_file_path='./img/示例12.png')))
except:
    pass


# 验证持久性是否生效
config = {"configurable": {"thread_id": "1"}}
for _, chunk in graph.stream({"foo": "foo"}, config, subgraphs=True):
    print(_,chunk)



# 通过使用与调用图相同的配置来查看父图状态。
print(graph.get_state(config).values)   # {'foo': 'hi! foobar'}
print('###')

# 检查父图的状态历史，找到在从node_2（包含子图的节点）返回结果之前的状态快照：
state_with_subgraph = [s for s in graph.get_state_history(config) if s.next == ("node_2",)][0]
print(state_with_subgraph)
print('####')

# 检索子图状态的配置
subgraph_config = state_with_subgraph.tasks[0].state
print(subgraph_config)
print('#####')
print(graph.get_state(subgraph_config).values)


