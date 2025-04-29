# main.py
from flask import Flask, request, jsonify, abort
import os
# 슬랙 유틸리티 함수 임포트
from slack_utils import verify_slack_request, send_message_to_slack

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "우리 슬랙 커맨드 서버 정상 영업 합니다!"

@app.route('/slack/commands', methods=['POST'])
def slack_command():
    # 슬랙 요청 검증 (개발 중에는 주석 처리 가능)
    if not verify_slack_request():
        # 401 Unauthorized 응답
        abort(401)
    
    # 슬랙에서 받은 데이터 추출
    command = request.form.get('command', '')
    text = request.form.get('text', '')
    user_id = request.form.get('user_id', '')
    channel_id = request.form.get('channel_id', '')
    
    # 로그 출력
    print(f'받은 명령어: {command}')
    print(f'파라미터: {text}')
    print(f'사용자: {user_id}')
    print(f'채널: {channel_id}')
    
    # 명령어에 따라 다른 응답 제공
    if command == '/테스트':
        response = {
            "response_type": "in_channel",  # 채널에 공개
            "text": "테스트 명령어가 실행되었습니다!",
            "attachments": [
                {
                    "text": f"파라미터: {text or '없음'}"
                }
            ]
        }
    elif command == '/help':
        response = {
            "response_type": "ephemeral",  # 사용자에게만 표시
            "text": "사용 가능한 명령어 목록:",
            "attachments": [
                {
                    "text": "• `/테스트 [텍스트]` - 테스트 명령어 실행\n• `/help` - 도움말 표시"
                }
            ]
        }
    else:
        # 기본 응답
        response = {
            "response_type": "ephemeral",
            "text": f"{command} 명령어를 인식할 수 없습니다.",
            "attachments": [
                {
                    "text": "사용 가능한 명령어를 보려면 `/help`를 입력하세요."
                }
            ]
        }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)