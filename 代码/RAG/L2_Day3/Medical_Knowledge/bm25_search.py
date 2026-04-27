import json
import jieba
import numpy as np
from rank_bm25 import BM25Okapi


# ================= 带分数打印的版本 =================

class SimpleTopNBM25:
    def __init__(self, data_path, chunk_word_size=20):
        print("正在初始化...")
        self.chunk_word_size = chunk_word_size

        # 1. 加载数据
        self.raw_data = self._load_data(data_path)

        # 2. 分词与分块
        self.corpus_chunks, self.corpus_metadata = self._prepare_corpus()

        # 3. 初始化 BM25
        print("正在构建索引...")
        self.tokenized_corpus = [jieba.lcut(chunk) for chunk in self.corpus_chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print("完成！\n")

    def _load_data(self, data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f.readlines()]

    def _split_by_words(self, text):
        """基于 jieba.lcut 切词"""
        words = jieba.lcut(text)
        if len(words) <= self.chunk_word_size:
            return ["".join(words)]

        chunks = []
        # 改为滑动窗口，避免语义被切断
        step = max(1, self.chunk_word_size // 2)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_word_size]
            chunks.append("".join(chunk_words))
        return chunks

    def _prepare_corpus(self):
        chunks = []
        metadata = []
        for idx, entry in enumerate(self.raw_data):
            full_text = f"问题：{entry['instruction']}\n答案：{entry['output']}"
            text_chunks = self._split_by_words(full_text)
            for chunk in text_chunks:
                chunks.append(chunk)
                metadata.append(entry)
        return chunks, metadata

    def search(self, query, top_k):
        # 1. 问题分词
        tokenized_query = jieba.lcut(query)
        print(f"查询: {query}\n分词: {tokenized_query}\n")

        # 2. 【关键】获取所有分数并手动排序
        # 获取所有分块的分数
        scores = self.bm25.get_scores(tokenized_query)

        # 按分数降序排序，获取索引
        # np.argsort()[::-1] 得到的是从大到小的索引数组
        sorted_indices = np.argsort(scores)[::-1]

        # 3. 去重并收集结果 (同时带上分数)
        seen = set()
        final_results = []

        print("-" * 30)
        print("检索过程 (按分数排序):")
        print("-" * 30)

        for idx in sorted_indices:
            score = scores[idx]
            item = self.corpus_metadata[idx]
            matched_chunk = self.corpus_chunks[idx]  # 拿到具体匹配到的文本片段

            # 打印过程日志
            print(f"[索引: {idx}] 分数: {score:.4f} | 匹配片段: {matched_chunk[:30]}...")

            # 去重逻辑
            if item['instruction'] not in seen:
                seen.add(item['instruction'])
                final_results.append({
                    "data": item,
                    "score": score,
                    "matched_chunk": matched_chunk
                })

            if len(final_results) >= top_k:
                break

        return final_results


# ================= 测试 =================

if __name__ == '__main__':
    retriever = SimpleTopNBM25('../Data/train.json')
    query = "喝酒之后怎么办"

    results = retriever.search(query, top_k=1)

    print("\n" + "=" * 15, "最终结果", "=" * 15)
    for i, res in enumerate(results, 1):
        print(f"\n[{i}] 匹配分数: {res['score']:.4f}")
        print(f"    问题: {res['data']['instruction']}")
        print(f"    答案: {res['data']['output']}")