import operator
import sqlite3
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, START
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage
from langgraph.pregel import RetryPolicy

RetryPolicy()

db = SQLDatabase.from_uri("sqlite:///:memory:")
# 创建表
db.run("CREATE TABLE Artist (ArtistId INTEGER PRIMARY KEY, Name NVARCHAR(120));")
# 表中添加数据
db.run("""
INSERT INTO Artist (Name) VALUES 
('Louis Armstrong'),
('Duke Ellington'),
('Ella Fitzgerald'),
('Charlie Parker'),
('Thelonious Monk'),
('Billie Holiday'),
('Dizzy Gillespie'),
('Herbie Hancock'),
('Sarah Vaughan'),
('Chet Baker'),
('Dave Brubeck'),
('Stan Getz'),
('Art Tatum'),
('Coleman Hawkins'),
('Lester Young');
""")

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(model_name="gpt-4o-mini")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def query_database(state):
    query_result = db.run(state['messages'][1].content)
    print('query_result', query_result)
    '''```sql\nSELECT * FROM Artist LIMIT 10;\n```
    正则表达式的形式
    '''
    # query_result = db.run("SELECT * FROM Artist LIMIT 5;")
    print('query_result:', query_result)
    return {"messages": [AIMessage(content=query_result)]}


def call_model(state):
    response = model.invoke(state["messages"])
    print('response:', response)
    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("query_database", query_database, retry=RetryPolicy(retry_on=sqlite3.OperationalError))
builder.add_node("model", call_model, retry=RetryPolicy(max_attempts=5))

builder.add_edge(START, "model")
builder.add_edge("model", "query_database")
builder.add_edge("query_database", END)
graph = builder.compile()

from IPython.display import display, Image

try:
    display(Image(graph.get_graph().draw_png(output_file_path='./img/示例9.png')))
except Exception:
    pass

result = graph.invoke({"messages": [HumanMessage(
    content="查询Artist表格中前十位艺术家，我的表名叫Artist，表结构信息只有ArtistId与Name两个字段，只返回SQL查询语句，不要返回其他内容，特别是TOP、```sql\n不要出现")]})
print('result：', result)
