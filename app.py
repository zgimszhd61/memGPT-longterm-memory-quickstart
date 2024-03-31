# 导入所需的库
from openai import OpenAI
import tiktoken
import json
import os
os.environ["OPENAI_API_KEY"] = "sk-"

# 初始化OpenAI客户端
client = OpenAI()

# 定义一个助手提示，用于初始化对话
assistant_prompt = "你是一名编程助理。 在 Markdown 中返回您的响应（如有必要，可使用代码块），并响应所有用户请求。"

# 定义一个函数，用于将对话记忆中的消息内容拼接成一个字符串
def join_messages(memory: list[dict]):
    text = ""
    for m in memory:
        text += m.get("content")
    return text

# 定义一个函数，检查文本是否超过了模型的上下文限制
def check_under_context_limit(text: str, limit: int, model: str):
    enc = tiktoken.encoding_for_model(model)
    numtokens = len(enc.encode(text))
    if numtokens <= limit:
        return True
    else:
        return False

# 定义一个函数，用于跟随对话并生成回复
def follow_conversation(user_text: str, memory: list[dict], mem_size: int, model: str):
    # 确定记忆列表中要使用的消息数量
    ind = min(mem_size, len(memory))
    # 如果记忆为空，则初始化系统消息
    if ind == 0:
        memory = [{"role": "system", "content": assistant_prompt}]
    # 添加用户消息到记忆中
    memory.append({"role": "user", "content": user_text})
    # 确保记忆中的消息不超过模型的上下文限制
    while not check_under_context_limit(join_messages(memory), 128000, "gpt-3.5-turbo") and ind > 1:
        ind -= 1
    # 使用OpenAI客户端生成回复
    resp = client.chat.completions.create(
        model=model,
        messages = memory[-ind:]
    )
    # 获取生成的回复内容
    tr = resp.choices[0].message.content
    # 将助手的回复添加到记忆中
    memory.append({"role": "assistant", "content": tr})
    # 将回复内容追加写入到Markdown文件中
    open("respuestas.md", "a", encoding="utf-8").write(tr)
    # 打印回复内容
    print(tr)
    # 返回更新后的记忆列表
    return memory

# 从文件中读取提示
prompt = open("prompt.txt", "r").read()
# 初始化对话记忆列表
memory = []
# 主循环，用于接收用户输入并处理
while True:
    user_input = input(">> ").strip()
    if user_input == "Exit":
        break
    elif user_input == "Prompt":
        user_input = prompt
    # 调用函数处理对话并更新记忆，记住10轮对话.
    memory = follow_conversation(user_text=user_input, memory=memory, mem_size=10, model="gpt-4-1106-preview")

# 将对话记忆保存到JSON文件中
json.dump(memory, open("mem.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)