# qabot

- 목적: 슬랙 질문 채널을 활성화하고 질문 답변에 대한 중간 힌트를 주기 위한 봇을 만드는 리포지토리
```
qabot/
  ├── main.py           # 기존 메인 애플리케이션 파일
  ├── requirements.txt  # 필요한 패키지 목록
  └── Procfile          # 애플리케이션 실행 방법 지정
  └utils
    ├── slack_utils.py    # 슬랙 관련 유틸리티 함수 (토큰 검증 등)
    └── gemini_utils.py   # Gemini 관련 유틸 함수(모델 호출 등)

  ```