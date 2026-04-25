# test.py
import os
from dotenv import load_dotenv

# 加载 .env 文件里的环境变量
load_dotenv()  

key = os.getenv("ALI_TONGYI_API_KEY")
print(key)  # 现在应该能正常打印你的 Key 了