# Festival-Finder-mcp

# Festival Finder (페스티벌 파인더)

범용 AI 에이전트 '페스티벌 파인더'입니다. 핵심 로직과 플랫폼별 어댑터를 분리하여 카카오톡, 일반 웹사이트 등 다양한 플랫폼에 연결할 수 있도록 설계되었습니다. KOPIS(공연예술통합전산망) API를 사용하여 전국의 공연 및 축제 정보를 제공합니다.

---

## 🏗️ 아키텍처

이 프로젝트는 **'핵심 엔진(Core Engine)'**과 **'연결 어댑터(Connection Adapters)'**라는 두 가지 주요 부분으로 구성된 확장 가능한 구조를 따릅니다.

### 🧠 핵심 엔진: `core_logic.py`
-   플랫폼에 독립적인 순수 비즈니스 로직입니다.
-   KOPIS API에서 데이터를 가져오고, 가공되지 않은 순수한 파이썬 데이터 형태로 반환하는 역할만 담당합니다.
-   어떤 플랫폼에 연결되는지 전혀 알지 못하며, 어디서든 재사용이 가능합니다.

### 📞 연결 어댑터
-   핵심 엔진을 다양한 외부 플랫폼에 연결하는 '플러그' 역할을 합니다.
-   각 플랫폼의 고유한 요청/응답 형식을 처리하고, 핵심 엔진과 통신합니다.

-   **`kakao_server.py`**: **카카오 PlayMCP**용 어댑터 서버입니다.
-   **`web_server.py`**: **일반 웹사이트나 앱**을 위한 범용 API 어댑터 서버입니다.

---

## 🛠️ 시작하기

1.  **필요 라이브러리 설치**
    ```bash
    pip install -r requirements.txt
    ```

2.  **KOPIS API 키 설정**
    `core_logic.py` 파일을 열어 `KOPIS_API_KEY` 변수에 발급받은 본인의 API 키를 입력하세요.

3.  **어댑터 서버 실행**
    필요한 어댑터 서버를 터미널에서 실행합니다.

    -   **카카오톡 연동 테스트 시:**
        ```bash
        python kakao_server.py
        ```
        - ngrok을 `http://localhost:5000`에 연결하고, PlayMCP Endpoint에 `[ngrok 주소]/kakao`를 등록합니다.

    -   **일반 웹 API 테스트 시:**
        ```bash
        python web_server.py
        ```
        - 웹 브라우저나 다른 프로그램에서 `http://localhost:5001/api/performances?stdate=...` 형식으로 요청하여 테스트할 수 있습니다.