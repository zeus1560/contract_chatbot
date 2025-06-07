from utils.ocr import extract_text_from_pdf
from utils.summarizer import summarize_text
from utils.risk_rules import detect_risks

def analyze_contract(file_path: str) -> dict:
    """
    계약서를 분석하여 텍스트, 요약, 위험 요소를 반환합니다.

    Args:
        file_path (str): 계약서 PDF 파일 경로

    Returns:
        dict: 분석 결과 딕셔너리 (원문, 요약, 리스크)
    """
    # 1. OCR로 텍스트 추출
    full_text = extract_text_from_pdf(file_path)

    # 2. 계약서 요약
    summary = summarize_text(full_text)

    # 3. 위험 요소 탐지
    risks = detect_risks(full_text)

    return {
        "text": full_text,
        "summary": summary,
        "risks": risks
    }
