
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

def search_and_judge_fraud(text, faiss_path="faiss_index", threshold=0.4, top_k=3):
    """
    텍스트가 사기 계약서와 유사한지 판단하고 관련 문서도 함께 반환
    """
    embedding = OpenAIEmbeddings()
    db = FAISS.load_local(faiss_path, embedding, allow_dangerous_deserialization=True)
    results = db.similarity_search_with_score(text, k=top_k)

    is_fraud = any(score < threshold for _, score in results)
    top_docs = [doc for doc, score in results]

    return is_fraud, top_docs
