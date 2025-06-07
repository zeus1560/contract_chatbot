from fraud_judger import search_and_judge_fraud

# 테스트할 사기 문장
text = "임대인은 계약 종료 시점과 무관하게, 자금 사정에 따라 보증금 반환 시점을 조정할 수 있으며 이에 대해 임차인은 이의를 제기하지 않기로 한다."

# FAISS DB에 대해 유사도 검색 실행
is_fraud, top_docs = search_and_judge_fraud(text, faiss_path="faiss_index", threshold=0.4)

print("\n📌 사기 판단 결과:", "⭕ 사기 계약 가능성 있음" if is_fraud else "✅ 정상 계약")
print("\n🔍 유사 문장:")
for i, doc in enumerate(top_docs, 1):
    print(f"[{i}] {doc.page_content.strip()}\n")