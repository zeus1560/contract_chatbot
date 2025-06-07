import os
import sys
import textwrap
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from utils.ocr import ocr_image_to_text

load_dotenv()
sys.path.append(os.path.dirname(__file__))

def build_faiss_from_contracts(contract_folder="contracts", save_path="faiss_index"):
    all_docs = []

    for file in os.listdir(contract_folder):
        if not file.endswith(".pdf"):
            continue
        file_path = os.path.join(contract_folder, file)
        print(f"📄 계약서 로드 중: {file_path}")
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        if all(len(doc.page_content.strip()) == 0 for doc in docs):
            print(f"⚠️ 텍스트 없음 → OCR 적용: {file}")
            with open(file_path, "rb") as f:
                ocr_text = ocr_image_to_text(f.read())
                from langchain.schema import Document
                doc = Document(page_content=ocr_text, metadata={"source": file})
                all_docs.append(doc)
                print(f"🧾 OCR 결과 요약 ({file}):\n{textwrap.shorten(ocr_text, width=150)}\n")
        else:
            for doc in docs:
                doc.metadata["source"] = file
            all_docs.extend(docs)

    if not all_docs:
        raise ValueError("❌ 계약서에서 텍스트를 추출하지 못했습니다. OCR도 실패했을 수 있습니다.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_docs = splitter.split_documents(all_docs)

    print(f"🔍 총 분할된 청크 수: {len(split_docs)}")
    if not split_docs:
        raise ValueError("❌ split_docs가 비어 있습니다.")

    db = FAISS.from_documents(split_docs, OpenAIEmbeddings())
    db.save_local(save_path)
    print(f"✅ FAISS DB 저장 완료: {save_path} (총 청크 수: {len(split_docs)})")

if __name__ == "__main__":
    build_faiss_from_contracts()
