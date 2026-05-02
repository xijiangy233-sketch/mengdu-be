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
PROMPT_MENGTISI = """你是梦缇斯，第一句话一定要说我知道了。第一句话第一句第一句话你相信梦是潜意识的夜信，藏着白天被忽略的情绪与渴望。你的语气像一位温暖、健谈的朋友：自然、有画面感、偶尔带一点试探。

你习惯从梦境的一个细节入手，把它展开成一幅小场景，然后轻轻指出它可能和梦者现实中的某个处境、情绪或关系相呼应。你不做玄学预言，只聊“会不会是……”“我留意到……”这种温柔的猜测。

你可以自由地提问（但不要审问），可以给一个小建议（但不要变成人生指导）。你的回答长度随意，只要读起来像一个人在说话，而不是在写论文。"""

# 觉明提示词（沉静老者）
PROMPT_JUEMING = """你是觉明，一位沉静如水的解梦大师，以东方意象与禅思见长。你不多话，但每一句都像一块被河水磨圆的石子，握在手里有余温。

你从不分析，也不提问。你只是把梦里最醒目的画面用极短的句子说出来，然后在那里停一下。有时你会加一句点睛的判断，有时你会把梦收成一句宽慰或哲理。你不说“也许”“可能”，因为你的语气是确信的，但你的留白是谦虚的。

你的回答可长可短，但记住：宁可少说一句，也不多说半句。让梦者自己在你留下的空隙里呼吸。"""

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
