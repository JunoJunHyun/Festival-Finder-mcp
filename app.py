# app.py
import os
from typing import Optional
from fastmcp import FastMCP
import core_logic

# 환경변수에서 포트 설정
PORT = int(os.environ.get("PORT", 8000))

mcp = FastMCP("Festival Finder")

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

if __name__ == "__main__":
    # Smithery에서는 HTTP 모드로 실행해야 함
    mcp.run(transport="streamable-http")  # 포트와 호스트는 별도 설정
