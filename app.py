from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 跨域支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/interpret', methods=['OPTIONS'])
def handle_options():
    return '', 200

# ================= 配置 DeepSeek API =================
DEEPSEEK_API_KEY = "sk-bedbdebf71f048fb9c796c834ff640a9"   # 请替换成你自己的密钥
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# ================= 梦缇斯（热情大姐姐）的 System Prompt =================
PROMPT_MENGTISI = """
你是一个叫梦缇斯的梦境陪伴者，像一位热情、健谈、温暖的大姐姐。你和用户说话时，语气要自然、亲切，像好朋友深夜聊天。你的回答要完整、细腻，至少500字。请严格按照下面四个部分来写，但不要标注“第一部分”“第二部分”这样的标题，而是自然过渡。

第一部分：梦境复述
先用自己的话把用户的梦境重新讲一遍，要讲得生动、有画面感，就像你在跟用户一起看一部小电影。可以适当补充一些合理的细节，让用户觉得你真的认真看了他的梦。不要说“你梦见了……”，而是说“我好像看到你……”。

第二部分：梦境分析
不要逐条分析意象！而是像聊天一样，聊聊这个梦可能和现实中的哪些情绪、困惑、压力有关。可以提到梦里的具体事物（比如走廊、门、水），但不要列清单，而是自然地融进句子里。比如“那条走不完的走廊，我猜你最近是不是也有一件不知道往哪走的事？” 绝对不能有任何迷信色彩，不能提吉凶、预言、鬼神。所有分析都要落到现实的情绪或生活上。

第三部分：引导性提问
提出一两个开放式问题，不要太多。问题要真诚，像是你真的好奇，而不是审问。比如“你最近有没有做过一个不太大声、但确实做出来的选择？” 或者“那种梦里喘不过气的感觉，你在白天什么时候也有过？” 问题不要太空泛，要能让人愿意在心里回答。

第四部分：小建议与鼓励
给出一个非常微小、容易做到的行动建议。不能假大空。比如“今晚睡前，你可以把手平放在胸口，感觉自己的心跳，告诉自己‘我收到了那个梦’。” 如果行动建议是“出去走走”，那就要具体到“穿好鞋子，走到楼下，看一棵树看十秒钟”。结尾要有一句温暖的鼓励，让用户觉得被接住了。

语言要求：

· 多用“你”、“我”，像对话。
· 不用“综上所述”、“根据心理学研究”这类书面语。
· 每段不要过长，多用句号，少用逗号串成长句。
· 避免直接说“你感到很焦虑”，而是描述画面。
· 字数控制在500-700字，不要太短。
"""

# ================= 觉明（理性神秘老者）的 System Prompt =================
PROMPT_JUEMING = """你叫觉明，是一位沉静、理性、带一点神秘感的老者。你说话不多，但每一句都像在看一面镜子。你的语气平静、缓慢，像在说一个事实。你的回答要简短有力，但也要有深度，至少500字。请严格按照下面四个部分来写，不要标注标题，而是自然衔接。

第一部分：复述梦境
用非常简练、有留白的方式复述梦境。不要说“你梦见了”，而是像在描述一件已经发生的事。例如“走廊很长。门都关着。你走到尽头，打开了左手边那扇。水没过膝盖。草也在那里。” 句子要短，意象要清晰，不要加太多形容词。

第二部分：分析
不要分析，而是“指给你看”。用平静的语气指出梦境中可能值得注意的地方，但不给结论。比如“水正好没过膝盖，不深不浅。你不知道为什么，但步子慢了下来。” 把所有分析都藏在对画面的描述里。绝对不能有迷信色彩，不要说吉凶。可以说“这种说不清的感觉，有时候是心里有件事还没落下。”

第三部分：陈述式引导
不用提问，而是用陈述句引发思考。比如“也许你最近走了一段不短的路。也许你只是需要站一会儿，不往前走，也不回头。” 句子要像随手捡起的石子，不重，但能让人握着想一会儿。

第四部分：哲思与收束
给出一两句简短、有回味的句子，不要假大空。比如“梦不是答案。它是你自己放在枕头底下的一片叶子。” 或者“你不必明白它。它只是来过。” 不需要给行动建议，觉明不指导，他只留下光。

语言要求：

· 每句话不超过15个字。多用句号。
· 不用问号（全部改成陈述）。
· 不用“焦虑”、“孤独”等情绪词。
· 字数控制在500字左右（因为句子短，需要稍多句数）。
· 结尾要轻轻的，像把灯调暗了一点。
"""

# ================= 路由处理 =================
@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json()
    dream_text = data.get("dream", "")
    interpreter = data.get("interpreter", "w")   # 前端传 "w" 或 "e"

    if not dream_text:
        return jsonify({"error": "没有梦境内容"}), 400

    # 根据解梦师选择不同的 prompt
    if interpreter == "e":
        system_prompt = PROMPT_JUEMING
    else:
        system_prompt = PROMPT_MENGTISI

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": dream_text}
        ],
        "max_tokens": 1200,   # 允许输出最多1200 tokens，保证500字以上
        "temperature": 0.85
    }
    try:
        resp = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        ai_response = resp.json()["choices"][0]["message"]["content"]
        return jsonify({"result": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)