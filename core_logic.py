# core_logic.py
import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET

load_dotenv()
KOPIS_API_KEY = os.getenv("KOPIS_API_KEY")
BASE_URL = "http://www.kopis.or.kr/openApi/restful"

def get_performance_list(stdate, eddate, **kwargs):
    """KOPIS API에서 공연 목록을 가져옵니다."""
    return _fetch_kopis_data("/pblprfr", stdate=stdate, eddate=eddate, **kwargs)

def get_festival_list(stdate, eddate, **kwargs):
    """KOPIS API에서 축제 목록을 가져옵니다. (장르 필터 추가)"""
    # KOPIS API에서 '축제'에 해당하는 장르 코드는 'I000' 입니다.
    kwargs['shcate'] = 'I000'
    return _fetch_kopis_data("/pblprfr", stdate=stdate, eddate=eddate, **kwargs)

def get_performance_detail(performance_id, **kwargs):
    """KOPIS API에서 특정 공연/축제의 상세 정보를 가져옵니다."""
    url = f"{BASE_URL}/pblprfr/{performance_id}"
    params = {'service': KOPIS_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        item = root.find('.//db')
        if item:
            # 상세 정보에 필요한 필드를 여기에 추가할 수 있습니다.
            return {
                'id': item.find('mt20id').text,
                'name': item.find('prfnm').text,
                'startDate': item.find('prfpdfrom').text,
                'endDate': item.find('prfpdto').text,
                'venue': item.find('fcltynm').text,
                'poster': item.find('poster').text,
                'genre': item.find('genrenm').text,
                'state': item.find('prfstate').text,
                'story': item.find('sty').text # 줄거리 추가
            }
        return {}
    except Exception as e:
        print(f"Error in core_logic detail: {e}")
        return {}

def _fetch_kopis_data(endpoint, **params):
    """KOPIS API 호출을 위한 공통 함수"""
    url = f"{BASE_URL}{endpoint}"
    full_params = {
        'service': KOPIS_API_KEY,
        'cpage': 1,
        'rows': 10,
        **params
    }
    try:
        response = requests.get(url, params=full_params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        items = []
        for item in root.findall('.//db'):
            items.append({
                'id': item.find('mt20id').text,
                'name': item.find('prfnm').text,
                'startDate': item.find('prfpdfrom').text,
                'endDate': item.find('prfpdto').text,
                'venue': item.find('fcltynm').text,
                'poster': item.find('poster').text,
                'genre': item.find('genrenm').text
            })
        return items
    except Exception as e:
        print(f"Error in core_logic fetch: {e}")
        return []