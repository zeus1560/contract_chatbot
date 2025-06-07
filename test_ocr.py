import easyocr
import os

# 1. 이미지 경로 (한글 X, 공백 X, 영어 추천)
image_path = r'C:\Users\82107\Downloads\contract_chatbot\contract_sample.png'

# 2. 존재 여부 확인
if not os.path.exists(image_path):
    raise FileNotFoundError(f"❌ 이미지 파일이 존재하지 않습니다: {image_path}")

# 3. EasyOCR 실행
reader = easyocr.Reader(['ko'], gpu=False)
results = reader.readtext(image_path, detail=0)

# 4. 결과 출력
print("📄 OCR 추출 결과:")
for line in results:
    print(line)
