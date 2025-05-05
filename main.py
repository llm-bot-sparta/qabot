# main.py
from flask import Flask, request, jsonify, abort
import os
# 슬랙 유틸리티 함수 임포트
from utils.slack_utils import verify_slack_request, send_message_to_slack, add_reaction_to_message, get_thread_messages
# Gemini 유틸리티 함수 임포트
from utils.gemini_utils import ask_gemini, DEV_MODE_GEMINI

app = Flask(__name__)

SYSTEM_PROMPT = (
    "정답을 직접적으로 알려주지 말고, 사용자가 스스로 답을 찾을 수 있도록 "
    "아주 간단한 답변(50자 이내)과 관련 개념 최대 5개를 다음 템플릿에 맞춰 작성해 주세요.\n\n"
    "간단한 답변: (답변 작성)\n"
    "관련 개념: (개념1), (개념2), (개념3), (개념4), (개념5)\n"
    "관련 개념이 5개 미만이면 빈 칸은 생략해도 됩니다.\n"
)

QUESTION_PROMPT = """
질문에 답변할 때 다음 지침을 따라주세요:

1. 답변 형식:
   - 간결하고 명확하게 정보를 제공하세요(최대 3-4 단락).
   - 질문의 핵심에 집중하고 군더더기 없이 답변하세요.
   - 학생 수준에 적합한 언어를 사용하세요.

2. 구조화된 답변:
   - 질문에 대한 직접적인 답변으로 시작하세요.
   - 실무 현장에서의 구체적인 예시를 1-2개 포함하세요.
   - 관련된 추가 자료나 참고 링크가 있다면 마지막에 제공하세요.

3. 코드 관련 질문:
   - 실행 가능한 코드 템플릿을 제공하세요.
   - 코드의 주요 부분에 주석을 달아 설명하세요.
   - 코드 실행 시 발생할 수 있는 일반적인 오류와 해결책을 간략히 언급하세요.
"""

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
        if not text:
            return jsonify({
                "response_type": "ephemeral",
                "text": "질문을 입력해주세요. 예: `/질문 파이썬으로 Hello World 코드를 작성해줘`"
            })
        try:
            question_message = f":question: <@{user_id}>님의 질문입니다:\n>{text}"
            question_response = send_message_to_slack(channel_id, question_message)
            if not question_response.get('ok', False):
                error_message = f"슬랙 메시지 전송 실패: {question_response.get('error', '알 수 없는 오류')}"
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            parent_ts = question_response.get('ts')
            if not parent_ts:
                error_message = "슬랙 메시지 ts를 가져오지 못했습니다."
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            # Gemini에 질문하기 (질문 프롬프트 적용)
            answer = ask_gemini(QUESTION_PROMPT + "\n" + text)

            # 답변을 스레드로 전송
            answer_response = send_message_to_slack(
                channel_id,
                answer,
                thread_ts=parent_ts
            )
            if not answer_response.get('ok', False):
                error_message = f"슬랙 답변 전송 실패: {answer_response.get('error', '알 수 없는 오류')}"
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            return '', 200
        except Exception as e:
            error_message = f"오류가 발생했습니다: {str(e)}"
            print(error_message)
            return jsonify({
                "response_type": "ephemeral",
                "text": error_message
            })
    
    elif command == '/힌트':
        if not text:
            return jsonify({
                "response_type": "ephemeral",
                "text": "질문을 입력해주세요. 예: `/힌트 파이썬으로 Hello World 코드를 작성해줘`"
            })
        try:
            question_message = f":question: <@{user_id}>님의 질문입니다:\n>{text}"
            question_response = send_message_to_slack(channel_id, question_message)
            if not question_response.get('ok', False):
                error_message = f"슬랙 메시지 전송 실패: {question_response.get('error', '알 수 없는 오류')}"
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            parent_ts = question_response.get('ts')
            if not parent_ts:
                error_message = "슬랙 메시지 ts를 가져오지 못했습니다."
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            # Gemini에 질문하기 (힌트 프롬프트 적용)
            answer = ask_gemini(SYSTEM_PROMPT + text)

            # 답변을 스레드로 전송
            answer_response = send_message_to_slack(
                channel_id,
                answer,
                thread_ts=parent_ts
            )
            if not answer_response.get('ok', False):
                error_message = f"슬랙 답변 전송 실패: {answer_response.get('error', '알 수 없는 오류')}"
                print(error_message)
                return jsonify({
                    "response_type": "ephemeral",
                    "text": error_message
                })

            return '', 200
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
                    "text": "• `/질문 [질문]` - Gemini AI에게 구조화된 답변 받기\n"
                            "• `/힌트 [질문]` - Gemini AI에게 힌트/키워드 받기\n"
                            "• `/테스트 [텍스트]` - 테스트 명령어 실행\n"
                            "• `/help` - 도움말 표시"
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

#이벤트 처리 라우트(미완성)
@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json

    # 슬랙 URL 검증용 challenge 응답
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data['challenge']})

    # 실제 이벤트 처리
    event = data.get('event', {})
    # 스레드 내 새 메시지 감지 (봇이 보낸 메시지는 무시)
    if event.get('type') == 'message' and event.get('thread_ts') and not event.get('bot_id'):
        channel_id = event['channel']
        user_id = event['user']
        text = event['text']
        thread_ts = event['thread_ts']

        # 1. 스레드의 모든 메시지 불러오기
        messages = get_thread_messages(channel_id, thread_ts)
        # 2. 대화 이력 정리 (질문, 답변, 추가질문 등)
        history = []
        for msg in messages:
            user = msg.get('user', 'user')
            msg_text = msg.get('text', '')
            # 봇 메시지와 사용자 메시지 구분
            if msg.get('bot_id'):
                history.append(f"[봇 답변]: {msg_text}")
            else:
                history.append(f"[{user}]: {msg_text}")

        # 3. CoT 프롬프트 생성
        cot_prompt = (
            "아래는 지금까지의 대화 이력입니다.\n"
            + "\n".join(history)
            + "\n\n마지막 사용자의 메시지에 대해 "
            "아주 간단한 답변(50자 이내)과 관련 개념 최대 5개를 다음 템플릿에 맞춰 작성해 주세요.\n\n"
            "간단한 답변: (답변 작성)\n"
            "관련 개념: (개념1), (개념2), (개념3), (개념4), (개념5)\n"
            "관련 개념이 5개 미만이면 빈 칸은 생략해도 됩니다.\n"
        )
        answer = ask_gemini(cot_prompt)
        send_message_to_slack(channel_id, answer, thread_ts=thread_ts)

    return '', 200

if __name__ == '__main__':
    # 개발 모드 확인
    dev_mode = DEV_MODE_GEMINI
    port = int(os.environ.get('PORT', 5000))  # 로컬에서는 5000 포트 사용
    
    if dev_mode:
        print("개발 모드로 서버를 실행합니다. Gemini 및 슬랙 검증이 비활성화됩니다.")
    
    app.run(host='0.0.0.0', port=port, debug=dev_mode)