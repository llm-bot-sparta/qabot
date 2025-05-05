# gemini_utils.py
import os
import google.generativeai as genai

# 환경 변수에서 Gemini API 키 가져오기
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# API 키가 없으면 개발 모드로 설정
DEV_MODE_GEMINI = not GEMINI_API_KEY

# Gemini API 설정
def setup_gemini():
    """Gemini API 설정"""
    if DEV_MODE_GEMINI:
        print("개발 모드: Gemini API 키가 설정되지 않았습니다. 가짜 응답을 반환합니다.")
        return False
    
    # API 키 설정
    genai.configure(api_key=GEMINI_API_KEY)
    return True

# Gemini에 질문하기
def ask_gemini(
    prompt,
    model_name="gemini-1.5-flash",
    system_prompt=(
        "정답을 직접적으로 알려주지 말고, 사용자가 스스로 답을 찾을 수 있도록 "
        "다음 템플릿에 맞춰 작성해 주세요.\n\n"
        "답변: (답변 작성)\n"
        "관련 개념: (개념1), (개념2), (개념3), (개념4), (개념5)\n"
        "예시: \n\n"
        "관련 개념이 5개 미만이면 빈 칸은 생략해도 됩니다.\n"
        "예시에서는 Python/SQL 질문이면 파이썬 코드와 SQL 코드를 주고, 실무적 질문이면 그 활용의 예시를 주세요."
    )
):
    """Gemini 모델에 질문하고 응답 받기"""
    print('ask_gemini발동')
    if system_prompt:
        prompt = system_prompt + prompt
    if DEV_MODE_GEMINI:
        print(f"개발 모드: 가짜 Gemini 응답 반환. 받은 프롬프트: {prompt}")
        return f"[개발 모드] 프롬프트 '{prompt}'에 대한 가짜 응답입니다. Gemini API 키를 설정하면 실제 응답을 받을 수 있습니다."
    try:
        # 모델 설정
        print('모델설정시작')
        model = genai.GenerativeModel(model_name)
        print('모델설정완료')
        # 응답 생성 
        response = model.generate_content(prompt)
        print('응답생성')
        # 응답 텍스트 반환
        return response.text
    except Exception as e:
        error_message = f"Gemini API 호출 중 오류 발생: {str(e)}"
        print(error_message)
        return f"죄송합니다. 응답을 생성하는 중 오류가 발생했습니다: {str(e)}"

# 초기 설정
setup_gemini()
print('setup_gemini 실행')