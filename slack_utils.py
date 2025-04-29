# slack_utils.py
import os
import hmac
import hashlib
import time
import requests
from flask import request

# 환경 변수에서 슬랙 토큰 가져오기
# 배포할 때 Cloud Run에 환경 변수 설정 필요
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET', '')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', '')

def verify_slack_request():
    """슬랙 요청 검증 함수"""
    # 개발 환경에서는 검증을 건너뛸 수 있음 (SLACK_SIGNING_SECRET이 비어있을 경우)
    if not SLACK_SIGNING_SECRET:
        print("경고: SLACK_SIGNING_SECRET이 설정되지 않았습니다. 요청 검증을 건너뜁니다.")
        return True
    
    # 슬랙에서 보낸 서명 및 타임스탬프
    slack_signature = request.headers.get('X-Slack-Signature', '')
    slack_request_timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    
    # 타임스탬프가 없으면 검증 실패
    if not slack_signature or not slack_request_timestamp:
        print("오류: 슬랙 서명 또는 타임스탬프가 없습니다.")
        return False
    
    # 타임스탬프 검증 (5분 이상 지난 요청은 거부 - 재생 공격 방지)
    try:
        if abs(time.time() - float(slack_request_timestamp)) > 300:
            print("오류: 요청이 너무 오래되었습니다.")
            return False
    except ValueError:
        print("오류: 잘못된 타임스탬프 형식입니다.")
        return False
    
    # 요청 본문 가져오기
    req_body = request.get_data(as_text=True)
    
    # 서명 베이스 문자열 생성
    basestring = f"v0:{slack_request_timestamp}:{req_body}"
    
    # HMAC-SHA256 해시 생성
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 서명 비교
    is_valid = hmac.compare_digest(my_signature, slack_signature)
    if not is_valid:
        print("오류: 슬랙 서명이 일치하지 않습니다.")
    return is_valid

def send_message_to_slack(channel, text, blocks=None):
    """슬랙 채널에 메시지 전송"""
    print('메시지전송')
    if not SLACK_BOT_TOKEN:
        print("경고: SLACK_BOT_TOKEN이 설정되지 않았습니다.")
        return {"ok": False, "error": "토큰이 설정되지 않았습니다."}
    
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'channel': channel,
        'text': text
    }
    
    print('블록전')
    if blocks:
        payload['blocks'] = blocks
    
    try:
        print("메시지 보내기 트라이")
        response = requests.post(url, json=payload, headers=headers)
        print('결과리턴')
        return response.json()
    except Exception as e:
        print(f"슬랙 메시지 전송 중 오류 발생: {e}")
        return {"ok": False, "error": str(e)}