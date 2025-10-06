# app.py (2단계 수정 확정본)
import os
from typing import Optional
from fastmcp import FastMCP
import core_logic
from dateutil import parser


def auto_format_date(date_str: str) -> str:
    try:
        parsed_date = parser.parse(date_str)
        return parsed_date.strftime("%Y%m%d")
    except Exception:
        return str(date_str).replace("-", "").replace("/", "").replace(" ", "")

PORT = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Festival Finder")

@mcp.tool()
def get_performance_list(
    stdate: str,
    eddate: str,
    cpage: int = 1,
    rows: int = 10,
    shprfnm: Optional[str] = None,
    prfstate: Optional[str] = None,
    signgucode: Optional[str] = None,
):
    """기간별, 조건별 공연 목록을 조회합니다."""
    formatted_stdate = auto_format_date(stdate)
    formatted_eddate = auto_format_date(eddate)
    return core_logic.get_performance_list(
        stdate=formatted_stdate,
        eddate=formatted_eddate,
        cpage=cpage,
        rows=rows,
        shprfnm=shprfnm,
        prfstate=prfstate,
        signgucode=signgucode,
    )

@mcp.tool()
def get_festival_list(
    stdate: str,
    eddate: str,
    cpage: int = 1,
    rows: int = 10,
    shprfnm: Optional[str] = None,
    signgucode: Optional[str] = None,
):
    """기간별, 조건별 축제 목록을 조회합니다."""
    formatted_stdate = auto_format_date(stdate)
    formatted_eddate = auto_format_date(eddate)
    return core_logic.get_festival_list(
        stdate=formatted_stdate,
        eddate=formatted_eddate,
        cpage=cpage,
        rows=rows,
        shprfnm=shprfnm,
        signgucode=signgucode,
    )

@mcp.tool()
def get_performance_detail(performance_id: str):
    """특정 공연의 상세 정보를 조회합니다."""
    return core_logic.get_performance_detail(performance_id=performance_id)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=PORT)
