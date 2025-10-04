from flask import Flask, request, jsonify
import core_logic
import json

app = Flask(__name__)

# 기존의 상태 확인 코드는 이제 필요 없으므로 삭제하거나 그대로 두어도 괜찮습니다.
# @app.route('/', methods=['GET'])
# def health_check():
#    return jsonify({"status": "ok", "message": "Server is running"})

# 👇 [가장 중요] 경로를 '/kakao'에서 '/'로 변경하고, POST와 GET을 모두 허용
@app.route('/', methods=['GET', 'POST'])
def adapter():
    # GET 요청은 상태 확인용으로 사용
    if request.method == 'GET':
        return jsonify({"status": "ok", "message": "Server is ready for POST requests"})

    # POST 요청은 기존 로직 그대로 사용
    req_data = request.json
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