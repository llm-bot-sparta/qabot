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
def ask_gemini(prompt, model_name="gemini-1.5-flash"):
    """Gemini 모델에 질문하고 응답 받기
    
    Args:
        prompt (str): 사용자의 질문/프롬프트
        model_name (str): 사용할 Gemini 모델명
    
    Returns:
        str: Gemini 모델의 응답 텍스트
    """
    print('ask_gemini발동')
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