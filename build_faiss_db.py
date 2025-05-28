import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def build_faiss_from_contracts(contract_folder="contracts", save_path="faiss_index"):
    all_docs = []

    # 모든 PDF 문서 로드
    for file in os.listdir(contract_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(contract_folder, file)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file  # 계약서 이름 보존
            all_docs.extend(docs)

    # 텍스트 분할
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_docs = splitter.split_documents(all_docs)

    # 임베딩 및 벡터 저장
    db = FAISS.from_documents(split_docs, OpenAIEmbeddings())
    db.save_local(save_path)
    print(f"✅ FAISS DB 저장 완료: {save_path} (총 청크 수: {len(split_docs)})")

if __name__ == "__main__":
    build_faiss_from_contracts()