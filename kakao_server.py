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

        # b) tools/list  (지금은 한 개만 노출)
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
                                "signgucode":{"type":"string","description":"지역코드(예: '11'=서울)","nullable":True},
                                "cpage":{"type":"integer","default":1},
                                "rows":{"type":"integer","default":10},
                                "shprfnm":{"type":"string"},
                                "prfstate":{"type":"string"}
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
                
                # 👇 [추가] '축제 찾기' 레시피를 여기에 추가합니다.
                elif name == "get_festival_list":
                    # 우선 '공연 찾기' 기능으로 축제 정보를 가져옵니다. (나중에 전용 함수로 바꿀 수 있습니다)
                    data = core_logic.get_performance_list(**args) 
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
