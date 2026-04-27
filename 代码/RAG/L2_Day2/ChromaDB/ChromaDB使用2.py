# chromaDB使用.py
import chromadb
import json
from dotenv import load_dotenv
import os
from openai import OpenAI

# ====================== 【在这里填写你的阿里云 API Key】======================
ALI_TONGYI_API_KEY = ""  # 替换成你的真实key
# ============================================================================

ALI_TONGYI_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ALI_TONGYI_EMBEDDING_V3 = "text-embedding-v3"

# 加载JSON数据
with open('../Data/train.json', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f.readlines()]

instructions = [d['instruction'] for d in data]
outputs = [d['output'] for d in data]

print("数据条数：", len(instructions))


# 向量数据库连接器
class MyVectorDBConnector:
    def __init__(self, collection_name):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        # 直接在这里创建客户端，不再依赖外部文件
        self.client = OpenAI(
            api_key=ALI_TONGYI_API_KEY,
            base_url=ALI_TONGYI_URL
        )

    # 文本向量化
    def get_embeddings(self, texts, model=ALI_TONGYI_EMBEDDING_V3):
        data = self.client.embeddings.create(input=texts, model=model).data
        return [x.embedding for x in data]

    # 批量向量化
    def get_embeddings_batch(self, texts, model=ALI_TONGYI_EMBEDDING_V3, batch_size=5):
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_text = texts[i:i + batch_size]
            embeddings = self.get_embeddings(batch_text, model)
            all_embeddings.extend(embeddings)
        return all_embeddings

    # 添加文档
    def add_documents(self, instructions, outputs):
        embeddings = self.get_embeddings_batch(instructions)
        self.collection.add(
            embeddings=embeddings,
            documents=outputs,
            ids=[f"id_{i}" for i in range(len(outputs))]
        )
        print(f"✅ 已存入 {self.collection.count()} 条向量数据")

    # 检索
    def search(self, query, n_results=2):
        query_embedding = self.get_embeddings([query])
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "distances"]
        )
        return results


# ====================== 执行 ======================
if __name__ == "__main__":
    vector_db = MyVectorDBConnector("medical_qa")
    vector_db.add_documents(instructions, outputs)

    user_query = "得了白癜风怎么办？"
    results = vector_db.search(user_query, 1)

    print("\n查询结果：")
    for doc in results['documents'][0]:
        print("→", doc)
        print("-"*50)