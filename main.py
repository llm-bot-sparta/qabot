# main.py
from flask import Flask, request, jsonify, abort
import os
# 슬랙 유틸리티 함수 임포트
from slack_utils import verify_slack_request, send_message_to_slack
# Gemini 유틸리티 함수 임포트
from gemini_utils import ask_gemini, DEV_MODE_GEMINI

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    status = "슬랙 커맨드 서버가 정상적으로 실행 중입니다!"
    
    # Gemini 상태 추가
    if DEV_MODE_GEMINI:
        status += "\n⚠️ Gemini API는 개발 모드입니다. 환경 변수 GEMINI_API_KEY를 설정하세요."
    else:
        status += "\n✅ Gemini API가 연결되었습니다."
    
    return status

@app.route('/test', methods=['GET'])
def test_page():
    return """
    <html>
        <head>
            <title>슬랙 커맨드 테스트</title>
        </head>
        <body>
            <h1>슬랙 커맨드 테스트</h1>
            <form action="/slack/commands" method="POST">
                <label>Command:</label>
                <input type="text" name="command" value="/ask"><br>
                <label>Text:</label>
                <input type="text" name="text" value="파이썬으로 Hello World 코드를 작성해줘"><br>
                <label>User ID:</label>
                <input type="text" name="user_id" value="U123456"><br>
                <label>Channel ID:</label>
                <input type="text" name="channel_id" value="C123456"><br>
                <button type="submit">테스트 요청 보내기</button>
            </form>
        </body>
    </html>
    """

@app.route('/slack/commands', methods=['POST'])
def slack_command():
    # 슬랙 요청 검증 (개발 환경에서는 주석 처리 가능)
    if not DEV_MODE_GEMINI and not verify_slack_request():
        abort(401)  # 인증 실패
    
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
    if command == '/질문':
        # 입력이 없는 경우 도움말 제공
        if not text:
            return jsonify({
                "response_type": "ephemeral",  # 사용자에게만 표시
                "text": "질문을 입력해주세요. 예: `/질문 파이썬으로 Hello World 코드를 작성해줘`"
            })
        
        # 즉시 응답 (3초 내에 응답해야 함)
        initial_response = {
            "response_type": "in_channel",
            "text": f"<@{user_id}>님의 질문: {text}\n\n처리 중입니다... ⏳"
        }
        
        # 백그라운드에서 Gemini API 호출하고 결과 게시 (비동기 처리가 이상적이지만 간단한 예시)
        # Flask의 특성상 여기서는 간단하게 구현합니다
        try:
            # Gemini에 질문하기
            print('ask')
            answer = ask_gemini(text)
            
            # 슬랙 메시지 형식 준비
            print('messag준비')
            message = f"<@{user_id}>님의 질문: {text}\n\n{answer}"
            
            # 새 메시지로 결과 게시 (실제로는 initial_response를 업데이트하는 것이 더 좋음)
            # 그러나 이 예시에서는 간단하게 처리합니다
            print('sendtomessagetoslack')
            slack_response = send_message_to_slack(channel_id, message)
            if not slack_response.get('ok', False):
                error_message = f"슬랙 메시지 전송 실패: {slack_response.get('error', '알 수 없는 오류')}"
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            # 클라이언트에게 빠른 응답
            return jsonify(initial_response)
        except Exception as e:
            error_message = f"오류가 발생했습니다: {str(e)}"
            print(error_message)
            return jsonify({
                "response_type": "ephemeral",
                "text": error_message
            })
    
    elif command == '/테스트':
        response = {
            "response_type": "in_channel",
            "text": "테스트 명령어가 실행되었습니다!",
            "attachments": [
                {
                    "text": f"파라미터: {text or '없음'}"
                }
            ]
        }
        return jsonify(response)
    
    elif command == '/help':
        response = {
            "response_type": "ephemeral",
            "text": "사용 가능한 명령어 목록:",
            "attachments": [
                {
                    "text": "• `/ask [질문]` - Gemini AI에게 질문하기\n• `/테스트 [텍스트]` - 테스트 명령어 실행\n• `/help` - 도움말 표시"
                }
            ]
        }
        return jsonify(response)
    
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
    # 개발 모드 확인
    dev_mode = DEV_MODE_GEMINI
    port = int(os.environ.get('PORT', 5000))  # 로컬에서는 5000 포트 사용
    
    if dev_mode:
        print("개발 모드로 서버를 실행합니다. Gemini 및 슬랙 검증이 비활성화됩니다.")
    
    app.run(host='0.0.0.0', port=port, debug=dev_mode)