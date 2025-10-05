from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS 라이브러리 import
import core_logic, json

app = Flask(__name__)
CORS(app)  # <-- app에 CORS 설정을 적용합니다. 이 한 줄이 핵심입니다!
app.url_map.strict_slashes = False  # 슬래시 유무 허용

# 하나의 핸들러로 여러 경로/메서드 받기
@app.route('/', methods=['GET', 'POST'])
@app.route('/kakao', methods=['GET','POST'])
@app.route('/mcp', methods=['GET','POST'])
def adapter():
    # 헬스/브라우저 확인용 GET은 200 OK로 응답
    if request.method == 'GET':
        return jsonify({"status":"ok","message":"POST a tool call to this endpoint"}), 200

    # POST 요청 처리
    req_data = request.get_json(silent=True) # 더 안전한 방법으로 JSON 데이터를 읽습니다.
    if not req_data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    tool_name = req_data.get("params", {}).get("name")
    arguments = req_data.get("params", {}).get("arguments", {})
    
    result_content = ""
    is_error = False

    if tool_name == 'get_performance_list':
        performances_list = core_logic.get_performance_list(**arguments)
        if performances_list:
            result_content = json.dumps(performances_list, ensure_ascii=False)
        else:
            is_error = True
            result_content = "공연 목록을 가져오는 데 실패했습니다."
            
    response = {
        "content": [{"type": "text", "text": result_content}],
        "isError": is_error
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)