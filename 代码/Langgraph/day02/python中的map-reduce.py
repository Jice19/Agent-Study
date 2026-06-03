# 输入数据（模拟分布式存储的分片）
input_data = [
    "hello world",
    "hello mapreduce",
    "hello world again",
    "mapreduce is fun",
    "hello world world"
]

# Map 阶段：将每个单词映射为键值对 (word, 1)
def map_function(text):
    words = text.split()  # 将句子分割成单词
    return [(word, 1) for word in words]


# 模拟 Map 阶段的输出
map_output = []
for text in input_data:
    map_output.extend(map_function(text))

print("Map 阶段输出:")
print(map_output)



# Shuffle 阶段：将相同键的键值对分组
from collections import defaultdict

def shuffle_function(map_output):
    shuffle_dict = defaultdict(list)
    for key, value in map_output:
        shuffle_dict[key].append(value)
    return shuffle_dict

shuffle_output = shuffle_function(map_output)

print("\nShuffle 阶段输出:")
for key, values in shuffle_output.items():
    print(f"{key}: {values}")


# Reduce 阶段：对每个键对应的值进行求和
def reduce_function(key, values):
    return (key, sum(values))  # 对值求和

# 模拟 Reduce 阶段的输出
reduce_output = [reduce_function(key, values) for key, values in shuffle_output.items()]

print("\nReduce 阶段输出:")
for key, count in reduce_output:
    print(f"{key}: {count}")