from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def detect_risks(text: str) -> str:
    """
    전세계약서 원문 내 잠재적인 위험 요소를 탐지합니다.

    Args:
        text (str): 계약서 전체 텍스트

    Returns:
        str: 감지된 위험 요소 설명
    """
    prompt = ChatPromptTemplate.from_template(
        "다음 계약서 원문에서 다음과 같은 전세계약서 관련 위험 요소가 있는지 확인하고, 있다면 어떤 조항이 문제인지 구체적으로 설명해줘:\n"
        "- 확정일자 누락 또는 지연\n"
        "- 전입신고 유예\n"
        "- 보증금 이중계약\n"
        "- 임대인과 등기부등본 소유주 불일치\n"
        "- 깡통전세 (보증금 > 시세)\n"
        "- 무자격 중개사 활용\n"
        "- 과도한 손해배상 책임\n"
        "- 일방적 계약 해지권\n"
        "- 불공정한 계약 기간 또는 특약\n"
        "- 기타 임차인에게 불리한 조건\n\n"
        "계약서 원문:\n{text}"
    )

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    chain = prompt | model | StrOutputParser()

    return chain.invoke({"text": text})