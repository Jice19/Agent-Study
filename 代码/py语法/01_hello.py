import os

# 获取环境变量，第二个参数为默认值（可选）
value = os.getenv("DASHSCOPE_API_KEY")
print(value)  