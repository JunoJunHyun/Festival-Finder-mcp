from flask import Flask, request, jsonify
import core_logic

app = Flask(__name__)

@app.route('/api/performances', methods=['GET'])
def web_adapter():
    # 웹사이트에서는 GET 요청으로 파라미터를 받음
    args = request.args
    
    # 1. 똑같은 '뇌'에게 일을 시킴
    performances_list = core_logic.get_performance_list(
        stdate=args.get('stdate'),
        eddate=args.get('eddate'),
        signgucode=args.get('signgucode')
    )
    
    # 2. 이번엔 카카오 형식이 아닌, 일반적인 JSON 형식으로 '포장'
    return jsonify({
        "status": "success",
        "data": performances_list
    })

if __name__ == '__main__':
    app.run(port=5001)