


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def summarize_text(text: str) -> str:
    """
    계약서 원문을 바탕으로 요약 및 해설을 생성합니다.

    Args:
        text (str): 계약서 전체 텍스트

    Returns:
        str: 자연어로 요약된 계약 내용
    """
    prompt = ChatPromptTemplate.from_template(
        "다음 계약서를 한국어로 이해하기 쉽게 요약해줘:\n\n{text}"
    )

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    chain = prompt | model | StrOutputParser()

    return chain.invoke({"text": text})