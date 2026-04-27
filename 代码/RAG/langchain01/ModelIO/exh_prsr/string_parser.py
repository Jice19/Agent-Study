from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# 1.创建模型客户端
model = ChatTongyi()
#2.构建提示词，访问模型
prompt = PromptTemplate(template="你是一个翻译助手，请讲以下内容翻译成{language}:{text}")
#3.解析大模型的返回
parser = StrOutputParser()

# print(str)
# 链的调用   在langchain中  "|" 是一个链的调用符
chain = prompt | model | parser
result = chain.invoke({"language": "中文", "text": "I am a programmer"})
print(result)
