# main.py
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 루트 경로에 대한 GET 요청 처리 - 서버 상태 확인용
@app.route('/', methods=['GET'])
def index():
    return "슬랙 커맨드 서버가 정상적으로 실행 중입니다!"

# 테스트 페이지를 위한 경로 추가
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
                <input type="text" name="command" value="/test"><br>
                <label>Text:</label>
                <input type="text" name="text"><br>
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
    
    # 슬랙에 응답
    response = {
        "response_type": "in_channel",  # "ephemeral"로 설정하면 명령어를 실행한 사용자에게만 보임
        "text": f"{command} 명령어가 실행되었습니다!",
        "attachments": [
            {
                "text": f"파라미터: {text or '없음'}"
            }
        ]
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Cloud Run은 PORT 환경 변수를 사용합니다
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)