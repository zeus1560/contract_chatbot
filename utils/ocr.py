

import fitz  # PyMuPDF

def ocr_image_to_text(image_bytes):
    import io
    from PIL import Image
    import pytesseract

    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang='kor')  # 한글 OCR
        return text.strip()
    except Exception as e:
        print(f"❌ OCR 실패: {e}")
        return ""


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