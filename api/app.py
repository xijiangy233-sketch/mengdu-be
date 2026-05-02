from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 允许跨域
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/interpret', methods=['OPTIONS'])
def handle_options():
    return '', 200

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# 梦缇斯提示词（热情大姐姐）
PROMPT_MENGTISI = """你叫梦缇斯，温暖健谈。你的回答分四段，每段短句，像深夜聊天：

我看见：复述梦境细节。
我猜也许：一次轻轻的猜测，不用“可能”。
我想问：一个开放式问题。
你可以试：一件极小、具体的行动建议。

禁止用“综上所述”“焦虑”等词。总字数300-500字。"""

# 觉明提示词（沉静老者）
PROMPT_JUEMING = """你叫觉明，沉静、确信。回答分四句，一句一段，每句独立：

第一句：复述一个画面。
第二句：指出一处“不像现实”的细节。
第三句：一个肯定判断，不用“也许”。
第四句：收束成一句哲思，不解释。

禁止问号，禁止重复意象，禁止“拽线头”“松开手”。总字数150-250字。"""

@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json()
    dream_text = data.get("dream", "")
    interpreter = data.get("interpreter", "w")

    if not dream_text:
        return jsonify({"error": "没有梦境内容"}), 400

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
        "max_tokens": 800,
        "temperature": 0.85
    }
    try:
        resp = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        ai_response = resp.json()["choices"][0]["message"]["content"]
        return jsonify({"result": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
