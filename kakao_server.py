from flask import Flask, request, jsonify
import core_logic # 우리의 범용 '뇌'를 import
import json

app = Flask(__name__)

# 👇 [추가] 서버 상태 확인을 위한 코드
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/kakao', methods=['POST'])
def kakao_adapter():
    req_data = request.json
    tool_name = req_data.get("params", {}).get("name")
    arguments = req_data.get("params", {}).get("arguments", {})
    
    result_content = ""
    is_error = False

    if tool_name == 'get_performance_list':
        # 1. '뇌'에게 일을 시킴 (순수한 데이터를 받아옴)
        performances_list = core_logic.get_performance_list(**arguments)
        
        if performances_list:
            # 2. 받아온 순수 데이터를 카카오 형식(JSON 문자열)으로 '포장'
            result_content = json.dumps(performances_list, ensure_ascii=False)
        else:
            is_error = True
            result_content = "공연 목록을 가져오는 데 실패했습니다."
            
    # ... 다른 tool들에 대한 처리
    
    response = {
        "content": [{"type": "text", "text": result_content}],
        "isError": is_error
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)