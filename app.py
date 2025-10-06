import os
from typing import Annotated, Optional
from pydantic import Field, BeforeValidator
from dateutil import parser
from fastmcp import FastMCP
import core_logic

# 날짜 자동 변환 함수와 타입 앨리어스

def auto_format_date(v: str) -> str:
    try:
        return parser.parse(v).strftime("%Y%m%d")
    except Exception:
        return str(v).replace("-", "").replace("/", "").replace(" ", "")

DateStr = Annotated[str, BeforeValidator(auto_format_date), Field(description="날짜 (자동 변환됨)")]

PORT = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Festival Finder")

@mcp.tool()
def get_performance_list(
    stdate: DateStr,
    eddate: DateStr,
    cpage: int = 1,
    rows: int = 10,
    shprfnm: Optional[str] = None,
    prfstate: Optional[str] = None,
    signgucode: Optional[str] = None,
):
    """기간별, 조건별 공연 목록을 조회합니다."""
    return core_logic.get_performance_list(
        stdate=stdate,
        eddate=eddate,
        cpage=cpage,
        rows=rows,
        shprfnm=shprfnm,
        prfstate=prfstate,
        signgucode=signgucode,
    )

@mcp.tool()
def get_festival_list(
    stdate: DateStr,
    eddate: DateStr,
    cpage: int = 1,
    rows: int = 10,
    shprfnm: Optional[str] = None,
    signgucode: Optional[str] = None,
):
    """기간별, 조건별 축제 목록을 조회합니다."""
    return core_logic.get_festival_list(
        stdate=stdate,
        eddate=eddate,
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
