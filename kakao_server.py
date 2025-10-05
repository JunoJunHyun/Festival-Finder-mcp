# kakao_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import core_logic

APP_NAME = "festival-finder-mcp"
APP_VER  = "0.1.0"

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False  # /kakao와 /kakao/ 모두 허용

# 공통 핸들러: MCP(JSON-RPC) + 단순 HTTP 양쪽 다 받기
@app.route('/', methods=['GET','POST'])
@app.route('/kakao', methods=['GET','POST'])
@app.route('/mcp', methods=['GET','POST'])
def adapter():
    if request.method == 'GET':
        # 스캐너/브라우저/헬스체크용
        return jsonify({"status":"ok","message":"POST MCP JSON-RPC or simple tool call"}), 200

    payload = request.get_json(silent=True) or {}

    # ========== 1) MCP JSON-RPC 브리지 ==========
    if payload.get("jsonrpc") == "2.0" and "method" in payload:
        rpc_id = payload.get("id")
        method = payload.get("method")
        params = payload.get("params") or {}

        # a) initialize (핸드셰이크)
        if method == "initialize":
            result = {
                "protocolVersion": params.get("protocolVersion","2025-06-18"),
                "capabilities": {
                    "tools": {"list": True, "call": True}
                },
                "serverInfo": {"name": APP_NAME, "version": APP_VER}
            }
            return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result}), 200

        # b) tools/list (툴 목록/스키마)
        if method in ("tools/list","tools.list","listTools"):
            result = {
                "tools": [
                    {
                        "name": "get_performance_list",
                        "description": "기간/지역별 공연 목록 조회(KOPIS)",
                        "inputSchema": {
                            "type":"object",
                            "properties":{
                                "stdate":{"type":"string","description":"시작일 YYYYMMDD"},
                                "eddate":{"type":"string","description":"종료일 YYYYMMDD"},
                                "signgucode":{"type":"string","description":"지역코드(예: '11'=서울)","nullable":True}
                            },
                            "required":["stdate","eddate"],
                            "additionalProperties": False
                        }
                    }
                ],
                "nextCursor": None
            }
            return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result}), 200

        # c) tools/call (툴 실행)
        if method in ("tools/call","tools.call","callTool"):
            name = params.get("name") or params.get("tool")
            args = params.get("arguments") or params.get("args") or {}
            try:
                if name == "get_performance_list":
                    data = core_logic.get_performance_list(**args)
                    text = json.dumps(data, ensure_ascii=False)
                    result = {"content":[{"type":"text","text":text}], "isError": False}
                else:
                    result = {"content":[{"type":"text","text":f"unknown tool: {name}"}], "isError": True}
            except Exception as e:
                result = {"content":[{"type":"text","text":f"server error: {e}"}], "isError": True}
            return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result}), 200

        # d) 알 수 없는 MCP 메서드
        return jsonify({"jsonrpc":"2.0","id":rpc_id,"error":{"code":-32601,"message":f"Unknown method: {method}"}}), 200

    # ========== 2) 단순 HTTP 포맷(백워드 호환) ==========
    name = (payload.get('name')
            or payload.get('tool')
            or (payload.get('params') or {}).get('name'))
    args = (payload.get('arguments')
            or payload.get('params')
            or {}) or {}

    is_error = False
    text = ""
    try:
        if name == "get_performance_list":
            data = core_logic.get_performance_list(**args)
            text = json.dumps(data, ensure_ascii=False)
        else:
            is_error = True
            text = f"unknown tool: {name}"
    except Exception as e:
        is_error = True
        text = f"server error: {e}"

    return jsonify({"content":[{"type":"text","text":text}],"isError":is_error}), 200


@app.route('/health', methods=['GET'])
def health():
    return "ok", 200

if __name__ == '__main__':
    app.run(port=5000)
