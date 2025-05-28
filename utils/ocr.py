

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    주어진 PDF 파일에서 페이지별로 텍스트를 추출합니다.
    
    Args:
        pdf_path (str): PDF 파일 경로
    
    Returns:
        str: 전체 페이지의 텍스트를 이어붙인 문자열
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text