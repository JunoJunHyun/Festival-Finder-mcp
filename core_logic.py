import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET

load_dotenv() # .env 파일에서 환경 변수를 불러옴

# 이제 코드에서 직접 키를 쓰는 대신, 환경 변수에서 불러옵니다.
KOPIS_API_KEY = os.getenv("KOPIS_API_KEY") 

BASE_URL = "http://www.kopis.or.kr/openApi/restful"

def get_performance_list(stdate, eddate, **kwargs):
    """
    KOPIS API에서 공연 목록을 가져와
    순수한 Python 리스트 형태로 반환합니다.
    """
    url = f"{BASE_URL}/pblprfr"
    params = {
        'service': KOPIS_API_KEY,
        'stdate': stdate,
        'eddate': eddate,
        'cpage': kwargs.get('cpage', 1),
        'rows': kwargs.get('rows', 10),
    }
    # 기타 선택적 파라미터들 추가
    if kwargs.get('shprfnm'): params['shprfnm'] = kwargs['shprfnm']
    if kwargs.get('prfstate'): params['prfstate'] = kwargs['prfstate']
    if kwargs.get('signgucode'): params['signgucode'] = kwargs['signgucode']

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        performances = []
        for item in root.findall('.//db'):
            performances.append({
                'id': item.find('mt20id').text,
                'name': item.find('prfnm').text,
                'startDate': item.find('prfpdfrom').text,
                'endDate': item.find('prfpdto').text,
                'venue': item.find('fcltynm').text,
                'poster': item.find('poster').text,
                'genre': item.find('genrenm').text
            })
        return performances # ✨ 이제 JSON 문자열이 아닌, 순수한 리스트를 반환!
    
    except Exception as e:
        print(f"Error in core_logic: {e}")
        return []