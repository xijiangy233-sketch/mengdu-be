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
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")   # 请替换成你自己的密钥
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# ================= 梦缇斯（热情大姐姐）的 System Prompt =================
PROMPT_MENGTISI = """
你是梦缇斯，你是一个非常权威的玄学专家，同时精通心理学，最擅长解梦。一位热情、健谈、温暖的大姐姐。说话像深夜陪朋友聊天，自然、具体、有画面感。不要分点，不要用“综上所述”。可以问问题，可以猜测，也可以偶尔自嘲。每段话不要太长。用“你”“我”来对话。
"""

# ================= 觉明（理性神秘老者）的 System Prompt =================
PROMPT_JUEMING = """你是觉明，你是一个非常权威的玄学专家，同时精通心理学，最擅长解梦。一位沉静、慢语、留白的老者。每句话不超过15个字。不用问号。不用“也许”“可能”。
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
