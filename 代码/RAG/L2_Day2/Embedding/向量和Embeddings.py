# 向量 和 Embeddings.py
# 如何访问嵌入模型以及输出文本的向量表示

import os
from dotenv import load_dotenv
from openai import OpenAI  # 必加

# 加载环境变量
load_dotenv()

# ===================== 阿里云配置 =====================
ALI_TONGYI_API_KEY = os.getenv("ALI_TONGYI_API_KEY")  # 这里直接写字符串，不搞变量
ALI_TONGYI_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ALI_TONGYI_EMBEDDING_V3 = "text-embedding-v3"
# ======================================================

# 创建客户端
client_qwen = OpenAI(
    api_key=ALI_TONGYI_API_KEY,
    base_url=ALI_TONGYI_URL
)

# 嵌入模型
def get_embeddings(texts, model, dimensions=1024):
    data = client_qwen.embeddings.create(input=texts, model=model, dimensions=1024).data
    return [x.embedding for x in data]

# 测试文本
test_query = [
    "我爱你",
    "中国为了反对内外敌人，争取民族独立和人民自由幸福，在历次斗争中牺牲的人民英雄们永垂不朽！"
]

# 生成向量
vec = get_embeddings(test_query, model=ALI_TONGYI_EMBEDDING_V3, dimensions=64)

# 输出结果
print(vec[0])
print("第1句话的维度:", len(vec[0]))
print("第2句话的维度:", len(vec[1]))