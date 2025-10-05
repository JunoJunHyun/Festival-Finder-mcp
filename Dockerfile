# 1. 파이썬 3.11 버전의 가벼운 리눅스를 기반으로 시작합니다.
FROM python:3.11-slim

# 2. 컨테이너 안에서 작업할 폴더를 만듭니다.
WORKDIR /app

# 3. 필요한 라이브러리 목록 파일을 먼저 복사합니다.
COPY requirements.txt .

# 4. 라이브러리를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 모든 프로젝트 코드를 복사합니다.
COPY . .

# 6. 이 컨테이너가 실행될 때 최종적으로 실행할 명령어입니다.
# 쉘을 거치지 않고 직접 실행하여 인수 누락 문제를 해결합니다.
# 포트는 app.py에서 환경 변수를 읽어 설정합니다.
CMD ["uvicorn", "app:mcp.app", "--host", "0.0.0.0", "--port", "8000"]