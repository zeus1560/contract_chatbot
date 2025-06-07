from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

def answer_question_about_contract(contract_text: str, question: str) -> str:
    """
    전세계약서 내용을 바탕으로 사용자의 질문에 대해 자연어로 해설을 생성합니다.

    Args:
        contract_text (str): 계약서 원문 텍스트
        question (str): 사용자의 질문

    Returns:
        str: 계약서에 기반한 질문 해설
    """
    prompt = ChatPromptTemplate.from_template(
        "다음 전세계약서 내용을 참고하여 사용자의 질문에 대해 법률 용어를 쉽게 풀어서 설명해줘. "
        "계약서 내 전입신고, 확정일자, 보증금 반환, 손해배상 등 조항에 대해 명확하고 실제적인 설명을 제공해줘.\n\n"
        "계약서 내용:\n{contract}\n\n"
        "질문:\n{question}"
    )

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    chain = prompt | model | StrOutputParser()

    return chain.invoke({"contract": contract_text, "question": question})


def highlight_risk_sentences(text: str, risk_keywords: list) -> str:
    """
    위험 키워드가 포함된 문장 내에서 키워드만 하이라이트 마크업으로 강조하고, 줄바꿈 유지.

    Args:
        text (str): 계약서 전체 텍스트
        risk_keywords (list): 키워드 목록

    Returns:
        str: 하이라이트된 HTML 텍스트
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    highlighted = []
    for sentence in sentences:
        highlighted_sentence = sentence
        for keyword in risk_keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_sentence = pattern.sub(f"<mark>{keyword}</mark>", highlighted_sentence)
        highlighted.append(highlighted_sentence)
    return "<br><br>".join(highlighted)


def calculate_risk_score(text: str, risk_keywords: list) -> int:
    """
    위험 키워드 출현 빈도 기반으로 위험 점수 계산 (0~100%)

    Args:
        text (str): 계약서 전체 텍스트
        risk_keywords (list): 위험 키워드 리스트

    Returns:
        int: 위험 점수 (0~100)
    """
    total_keywords = 0
    for keyword in risk_keywords:
        total_keywords += text.lower().count(keyword.lower())

    # 간단한 점수 공식: 키워드 1개당 10점, 최대 100점 제한
    score = min(total_keywords * 10, 100)
    return score


def highlight_risk_patterns(text: str, risk_patterns: list) -> str:
    """
    위험 패턴 리스트를 정규식으로 검사하여 문장 내 일치 시 하이라이트 표시.

    Args:
        text (str): 전체 계약서 원문
        risk_patterns (list): {"label": str, "pattern": str} 형태의 위험 조항 패턴 리스트

    Returns:
        str: 하이라이트가 적용된 HTML 문자열
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    highlighted = []
    for sentence in sentences:
        highlighted_sentence = sentence
        for pattern in risk_patterns:
            regex = re.compile(pattern["pattern"], re.IGNORECASE)
            highlighted_sentence = regex.sub(
                f"<mark>{pattern['label']}</mark>", highlighted_sentence
            )
        highlighted.append(highlighted_sentence)
    return "<br><br>".join(highlighted)