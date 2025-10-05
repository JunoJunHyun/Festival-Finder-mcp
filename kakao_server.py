# kakao_server.py (Simplified and Corrected)
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import core_logic

APP_NAME = "festival-finder-mcp"
APP_VER  = "0.1.0"

app = Flask(__name__)
CORS(app)

# 서버 상태 확인 및 MCP 요청을 처리할 단일 엔드포인트
@app.route('/', methods=['GET','POST'])
def adapter():
    # GET 요청은 스캐너의 상태 확인(Health Check)용
    if request.method == 'GET':
        return jsonify({"status":"ok", "message":"Server is ready for MCP JSON-RPC POST requests."})

    # POST 요청은 MCP 프로토콜로만 처리
    payload = request.get_json(silent=True) or {}

    # MCP JSON-RPC 형식이 아니면 요청을 처리하지 않음
    if not (payload.get("jsonrpc") == "2.0" and "method" in payload):
        return jsonify({"jsonrpc":"2.0", "id": payload.get("id"), "error":{"code":-32600,"message":"Invalid Request"}}), 400

    rpc_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") or {}

    # a) initialize
    if method == "initialize":
        result = {
            "protocolVersion": params.get("protocolVersion","2025-06-18"),
            "capabilities": { "tools": { "list": True, "call": True } },
            "serverInfo": { "name": APP_NAME, "version": APP_VER }
        }
        return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result})

    # b) tools/list (모든 도구를 정확하게 자기소개)
    if method in ("tools/list", "listTools"):
        result = {
            "tools": [
                {
                    "name": "get_performance_list",
                    "description": "기간별, 조건별 공연 목록을 조회합니다.",
                    "inputSchema": {"type":"object", "properties":{"stdate":{"type":"string"},"eddate":{"type":"string"},"cpage":{"type":"integer"},"rows":{"type":"integer"},"shprfnm":{"type":"string"},"prfstate":{"type":"string"},"signgucode":{"type":"string"}},"required":["stdate","eddate"]}
                },
                {
                    "name": "get_performance_detail",
                    "description": "특정 공연의 상세 정보를 조회합니다.",
                    "inputSchema": {"type":"object", "properties":{"performance_id":{"type":"string"}},"required":["performance_id"]}
                },
                {
                    "name": "get_festival_list",
                    "description": "기간별, 조건별 축제 목록을 조회합니다.",
                    "inputSchema": {"type":"object", "properties":{"stdate":{"type":"string"},"eddate":{"type":"string"},"cpage":{"type":"integer"},"rows":{"type":"integer"},"shprfnm":{"type":"string"},"signgucode":{"type":"string"}},"required":["stdate","eddate"]}
                }
            ]
        }
        return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result})

    # c) tools/call (모든 도구를 실행)
    if method in ("tools/call", "callTool"):
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            if name == "get_performance_list":
                data = core_logic.get_performance_list(**args)
            elif name == "get_festival_list":
                data = core_logic.get_festival_list(**args)
            elif name == "get_performance_detail":
                data = core_logic.get_performance_detail(**args)
            else:
                raise ValueError(f"unknown tool: {name}")

            text = json.dumps(data, ensure_ascii=False)
            result = {"content":[{"type":"text","text":text}], "isError": False}

        except Exception as e:
            result = {"content":[{"type":"text","text":f"server error: {e}"}], "isError": True}
        
        return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result})

    # d) 알 수 없는 MCP 메서드
    return jsonify({"jsonrpc":"2.0","id":rpc_id,"error":{"code":-32601,"message":f"Unknown method: {method}"}})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "5000"))
    app.run(host='0.0.0.0', port=port)