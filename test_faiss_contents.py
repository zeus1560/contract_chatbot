from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 벡터 DB 로딩
db = FAISS.load_local("faiss_index", OpenAIEmbeddings())

# 특정 키워드로 유사 문장 검색
query = "보증금 반환 시점을 조정할 수 있다"
docs = db.similarity_search(query, k=5)

print("\n🔍 FAISS DB 유사 문장 검색 결과:")
for i, doc in enumerate(docs, 1):
    print(f"[{i}] {doc.page_content.strip()}\n")
