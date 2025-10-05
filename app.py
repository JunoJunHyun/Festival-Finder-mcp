# app.py
import os
from typing import Optional
from fastmcp import FastMCP
import core_logic

# 1. FastMCP 앱 생성
mcp = FastMCP("Festival Finder")

# 2. smithery.yaml에 정의된 각 도구를 함수로 만들고, @mcp.tool() 데코레이터를 붙여줍니다.
#    FastMCP가 이 함수들을 자동으로 MCP 규칙에 맞게 변환해줍니다.

@mcp.tool()
def get_performance_list(stdate: str, eddate: str, cpage: int = 1, rows: int = 10, shprfnm: Optional[str] = None, prfstate: Optional[str] = None, signgucode: Optional[str] = None):
    """기간별, 조건별 공연 목록을 조회합니다."""
    return core_logic.get_performance_list(
        stdate=stdate, eddate=eddate, cpage=cpage, rows=rows, shprfnm=shprfnm, prfstate=prfstate, signgucode=signgucode
    )

@mcp.tool()
def get_festival_list(stdate: str, eddate: str, cpage: int = 1, rows: int = 10, shprfnm: Optional[str] = None, signgucode: Optional[str] = None):
    """기간별, 조건별 축제 목록을 조회합니다."""
    return core_logic.get_festival_list(
        stdate=stdate, eddate=eddate, cpage=cpage, rows=rows, shprfnm=shprfnm, signgucode=signgucode
    )

@mcp.tool()
def get_performance_detail(performance_id: str):
    """특정 공연의 상세 정보를 조회합니다."""
    return core_logic.get_performance_detail(performance_id=performance_id)

# 3. 서버를 실행하는 부분
if __name__ == "__main__":
    # PORT 환경 변수가 있으면 사용하고, 없으면 8000번 포트 사용
    port = int(os.environ.get("PORT", 8000))
    mcp.run(port=port)