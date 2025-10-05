# kakao_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import core_logic

APP_NAME = "festival-finder-mcp"
APP_VER  = "0.1.0"

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False

def render_md(items):
    if not items:
        return "해당 조건에 맞는 공연이 없습니다."
    lines = []
    for p in items:
        name = p.get('name','')
        genre = p.get('genre','')
        start_ = p.get('startDate','')
        end_ = p.get('endDate','')
        venue = p.get('venue','')
        poster = p.get('poster','')
        lines.append(
            f"- **{name}** ({genre})  \n"
            f"  날짜: {start_}–{end_}  \n"
            f"  장소: {venue}  \n"
            f"  포스터: {poster}"
        )
    return "\n".join(lines)

@app.route('/', methods=['GET','POST','OPTIONS'])
@app.route('/kakao', methods=['GET','POST','OPTIONS'])
@app.route('/mcp', methods=['GET','POST','OPTIONS'])
def adapter():
    if request.method == 'OPTIONS':
        return ("", 204)
    if request.method == 'GET':
        return jsonify({"status":"ok","message":"POST MCP JSON-RPC (initialize/tools.list/tools.call) or simple tool call"}), 200

    payload = request.get_json(silent=True) or {}

    # ===== 1) MCP JSON-RPC 처리 =====
    if payload.get("jsonrpc") == "2.0" and "method" in payload:
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
            return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result}), 200


        # b) tools/list (툴 목록/스키마)
        if method in ("tools/list","tools.list","listTools"):
            result = {
                "tools": [
                    # Tool 1: get_performance_list
                    {
                        "name": "get_performance_list",
                        "description": "기간별, 조건별 공연 목록을 조회합니다.",
                        "inputSchema": {
                            "type":"object",
                            "properties":{
                                "stdate":{"type":"string","description":"공연 시작일 (형식: YYYYMMDD)"},
                                "eddate":{"type":"string","description":"공연 종료일 (형식: YYYYMMDD)"},
                                "cpage": {"type": "integer", "description": "현재 페이지 번호", "default": 1},
                                "rows": {"type": "integer", "description": "페이지 당 목록 수", "default": 10},
                                "shprfnm": {"type": "string", "description": "조회할 공연명", "optional": True},
                                "prfstate": {"type": "string", "description": "공연 상태 코드 ('01':공연예정, '02':공연중, '03':공연완료)", "optional": True},
                                "signgucode":{"type":"string","description":"지역(시도) 코드 (예: '11'은 서울)", "optional": True}
                            },
                            "required":["stdate","eddate"]
                        }
                    },
                    # Tool 2: get_performance_detail
                    {
                        "name": "get_performance_detail",
                        "description": "특정 공연의 상세 정보를 조회합니다.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "performance_id": {"type": "string", "description": "조회할 공연의 고유 ID"}
                            },
                            "required": ["performance_id"]
                        }
                    },
                    # Tool 3: get_festival_list
                    {
                        "name": "get_festival_list",
                        "description": "기간별, 조건별 축제 목록을 조회합니다.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "stdate": {"type": "string", "description": "축제 시작일 (형식: YYYYMMDD)"},
                                "eddate": {"type": "string", "description": "축제 종료일 (형식: YYYYMMDD)"},
                                "cpage": {"type": "integer", "description": "현재 페이지 번호", "default": 1},
                                "rows": {"type": "integer", "description": "페이지 당 목록 수", "default": 10},
                                "shprfnm": {"type": "string", "description": "조회할 축제명", "optional": True},
                                "signgucode": {"type": "string", "description": "지역(시도) 코드 (예: '11'은 서울)", "optional": True}
                            },
                            "required": ["stdate", "eddate"]
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
                
                elif name == "get_festival_list":
                    data = core_logic.get_festival_list(**args) 
                    text = json.dumps(data, ensure_ascii=False)
                    result = {"content":[{"type":"text","text":text}], "isError": False}

                elif name == "get_performance_detail":
                    data = core_logic.get_performance_detail(**args)
                    text = json.dumps(data, ensure_ascii=False)
                    result = {"content":[{"type":"text","text":text}], "isError": False}

                else:
                    result = {"content":[{"type":"text","text":f"unknown tool: {name}"}], "isError": True}
            
            except Exception as e:
                result = {"content":[{"type":"text","text":f"server error: {e}"}], "isError": True}
            return jsonify({"jsonrpc":"2.0","id":rpc_id,"result":result}), 200

        # d) 알 수 없는 메서드
        return jsonify({"jsonrpc":"2.0","id":rpc_id,"error":{"code":-32601,"message":f"Unknown method: {method}"}}), 200

    # ===== 2) 예전(단순) 형식도 백워드 호환 =====
    name = (payload.get('name')
            or payload.get('tool')
            or (payload.get('params') or {}).get('name'))
    args = (payload.get('arguments')
            or payload.get('params')
            or {}) or {}

    is_error = False
    try:
        if name == "get_performance_list":
            data = core_logic.get_performance_list(**args)
            text = render_md(data)
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
    port = int(os.environ.get("PORT", "5000"))
    app.run(port=port)
