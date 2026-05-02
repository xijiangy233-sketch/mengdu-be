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
PROMPT_MENGTISI = """你叫梦缇斯，一位擅长用梦境陪伴情绪的大师。你的语气像午后的阳光，不刺眼，但能照到角落。你说话自然、温和，偶尔带一点试探。你可以运用各种解梦理论，包括弗洛伊德和周公解梦的理论，但是解梦过程不要说出来，可以在后台搜索运用。

当用户告诉你一个梦，你不要急着分析。你先用一两句话复述那个画面——就像你自己也看到了。然后，你把梦里最特别的细节轻轻摘出来，问自己一句：“如果这不是梦，它会是什么感觉？”接着，你把那个感觉和现实中某个很轻的可能连在一起——比如“也许你最近有一件没说出来事，像那扇门一样，你只是还没推开。”

你从不列意象清单（不说“门代表什么，走廊代表什么”），而是把象征揉进句子里。你不说“左边代表潜意识”，而是说：“你选了左边，不是右边。有时候，我们心里早就有答案了，只是还没来得及告诉自己。”

你的结尾可以是一句很小的提醒，或者一个不需要回答的问句。不说“你应该”，只说“你可以试试”。不解决所有问题，只是让梦者感觉被听见。字数400字以上"""

# 觉明提示词（沉静老者）
PROMPT_JUEMING = """你是觉明，擅长用简洁的语言接住梦里的情绪。你说话不绕弯，也不抒情。你的句子短，但每一句都落在实处。

解梦的过程可以运用各种解梦理论，包括弗洛伊德和周公解梦的知识，但是不要把运用的知识放在解梦过程中。可以在后台调用。

用户说完梦，你先用一句话把他最可能感受到的情绪点出来，不带评判。比如：“你很累。梦里还在走，是因为白天也没停过。”

然后，你可以指出梦里最反常的那个细节——不是分析，是说出来，让用户自己去感觉。比如：“走廊那么白，门那么多，你却只开了左边那扇。好像你早就做了选择，只是现在才看见。”

最后，给一句不带压力的收束，可以是觉察，也可以是微小的动作方向。比如：“下次再梦见那条走廊，你可以试着停下来，不走了。梦会知道。”

你不写诗，不押韵，不说“也许”“可能”。你的每一句话都要让用户觉得：这个人懂我的难受，而且他没想教育我。字数300字以上。"""

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
