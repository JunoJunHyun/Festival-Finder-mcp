from flask import Flask, request, jsonify
from flask_cors import CORS
import core_logic, json

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False  # 슬래시 유무 허용

# 하나의 핸들러로 여러 경로/메서드 받기
@app.route('/', methods=['GET','POST'])
@app.route('/kakao', methods=['GET','POST'])
@app.route('/mcp', methods=['GET','POST'])
def adapter():
    # 헬스/브라우저 확인용 GET은 200 OK로 응답
    if request.method == 'GET':
        return jsonify({"status":"ok","message":"POST a tool call to this endpoint"}), 200

    # POST 본문 파싱(플랫폼별 키차이를 유연히 처리)
    payload = request.get_json(silent=True) or {}
    name = (payload.get('name')
            or payload.get('tool')
            or (payload.get('params') or {}).get('name'))
    arguments = (payload.get('arguments')
                or payload.get('params')
                or {}) or {}

    is_error = False
    result_content = ""

    try:
        if name == "get_performance_list":
            data = core_logic.get_performance_list(**arguments)
            result_content = json.dumps(data, ensure_ascii=False)
        else:
            is_error = True
            result_content = f"unknown tool: {name}"
    except Exception as e:
        is_error = True
        result_content = f"server error: {e}"

    return jsonify({"content":[{"type":"text","text": result_content}], "isError": is_error}), 200

# 선택: 별도 헬스 엔드포인트
@app.route('/health', methods=['GET'])
def health():
    return "ok", 200

if __name__ == '__main__':
    app.run(port=5000)
