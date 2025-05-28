import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import tempfile
import datetime
from fpdf import FPDF

from analyze_contract import analyze_contract
from utils.helper import answer_question_about_contract, highlight_risk_sentences, calculate_risk_score

# 🔍 FAISS 관련 추가 import
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

# ✅ 페이지 제목과 아이콘 변경
st.set_page_config(page_title="전세계약서 분석 챗봇", page_icon="🏠")

# 🔍 FAISS 검색 함수
def search_existing_contracts(user_question, faiss_path="faiss_index"):
    db = FAISS.load_local(
        faiss_path,
        OpenAIEmbeddings(),
        allow_dangerous_deserialization=True
    )
    retriever = db.as_retriever(search_kwargs={"k": 3})
    return retriever.get_relevant_documents(user_question)

# 세션 상태 초기화 (uploaded_file_times 포함)
for key in [
    "analysis_result", "analysis_done", "uploaded_files", "show_exit_confirm",
    "uploaded_file_paths", "compare_docs", "user_question", "analysis_choice",
    "uploaded_file_times"
]:
    if key not in st.session_state:
        if key in ["uploaded_files", "compare_docs"]:
            st.session_state[key] = []
        elif key in ["uploaded_file_paths", "uploaded_file_times"]:
            st.session_state[key] = {}
        else:
            st.session_state[key] = None

# UI 제목 및 설명
st.markdown("<h1 style='text-align: center;'>🏠 전세계약서 분석 챗봇</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>전세 계약서를 업로드하면 위험 조항과 해설을 제공해 드립니다.</h4>", unsafe_allow_html=True)

# ✅ 사이드바: 설정, 날짜 필터, 업로드 목록, 미리보기
with st.sidebar:
    # 날짜 필터
    st.markdown("### ⏳ 업로드 날짜 필터")
    if st.session_state.uploaded_file_times:
        dates = [t.date() for t in st.session_state.uploaded_file_times.values()]
        start_date = st.date_input("시작일", value=min(dates))
        end_date = st.date_input("종료일", value=max(dates))
        filtered_files = [
            f for f, t in st.session_state.uploaded_file_times.items()
            if start_date <= t.date() <= end_date
        ]
    else:
        filtered_files = []

    # 업로드 목록 (삭제 기능)
    st.markdown("### 📂 업로드한 계약서 목록")

    # 삭제할 파일 이름을 담을 변수
    file_to_delete = None

    for filename in filtered_files:
        cols = st.columns([4, 1])
        cols[0].markdown(f"- {filename}")
        if cols[1].button("삭제", key=f"del_{filename}"):
            file_to_delete = filename

    # 루프 바깥에서 삭제 처리
    if file_to_delete:
        st.session_state.uploaded_files.remove(file_to_delete)
        st.session_state.uploaded_file_paths.pop(file_to_delete, None)
        st.session_state.uploaded_file_times.pop(file_to_delete, None)
        st.rerun()  # 삭제 후 즉시 UI 갱신
    # 미리보기
    st.markdown("### 🔍 계약서 미리보기")
    if filtered_files:
        preview_file = st.selectbox("파일 선택", filtered_files)
        preview_path = st.session_state.uploaded_file_paths.get(preview_file, "")
        if preview_path.lower().endswith(("png", "jpg", "jpeg")):
            st.image(preview_path, use_container_width=True)
        else:
            st.write(f"PDF 미리보기는 지원되지 않습니다: {preview_file}")

# 파일 업로드 영역
col1, col2, col3 = st.columns([1, 1, 2])
with col3:
     uploaded_file = st.file_uploader(
         "📎 전세계약서 업로드",
         type=["pdf", "png", "jpg", "jpeg"],
         key="uploader"
     )

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    st.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")
    if uploaded_file.name not in st.session_state.uploaded_files:
        # 저장 및 업로드 시간 기록
        st.session_state.uploaded_files.append(uploaded_file.name)
        st.session_state.uploaded_file_paths[uploaded_file.name] = temp_path
        st.session_state.uploaded_file_times[uploaded_file.name] = datetime.datetime.now()

    if file_ext in ("png", "jpg", "jpeg"):
        if st.checkbox("업로드된 계약서 이미지 보기", key="show_raw_image"):
            st.image(temp_path, caption="업로드한 계약서 이미지", use_container_width=True)

    if st.button("🔍 계약서 분석 시작"):
        with st.spinner("분석 중입니다..."):
            result = analyze_contract(temp_path)
            st.session_state.analysis_result = result
            st.session_state.analysis_done = True
            st.session_state.analysis_choice = None

# 분석 결과 표시
if st.session_state.analysis_done and st.session_state.analysis_result:
    result = st.session_state.analysis_result

    # 위험 점수 계산
    # 위험도 점수 계산 후, LLM 탐지 결과를 강제로 초기화
if st.session_state.analysis_done and st.session_state.analysis_result:
    result = st.session_state.analysis_result

    # 1) 위험도 계산
    risk_keywords = [
        "확정일자", "전입신고", "보증금", "손해배상",
        "이중계약", "등기부등본", "불공정", "계약해지"
    ]
    score = calculate_risk_score(result["text"], risk_keywords)
    st.markdown(f"🔥 **종합 위험도: {score}%**")

    # 2) 위험도가 0일 때 LLM 탐지 결과 비우기
    if score == 0:
        result["risks"] = ""

    # 3) 실제 위험 요소 표시
    if result["risks"].strip():
        st.warning(result["risks"])
    else:
        st.info("위험 요소가 발견되지 않았습니다. 🔒")

    # …이후 PDF 생성 및 QA 로직…

    # PDF 생성 함수
    def generate_pdf(summary, risks, score):
        pdf = FPDF()
        pdf.add_page()
        font_path = os.path.join("fonts", "NanumGothic.ttf")
        pdf.add_font("Nanum", "", font_path, uni=True)
        pdf.set_font("Nanum", size=12)
        pdf.cell(200, 10, txt="계약서 분석 리포트", ln=True)
        pdf.cell(200, 10, txt=f"분석 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)
        pdf.cell(200, 10, txt="계약서 요약", ln=True)
        for line in summary.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.ln(5)
        pdf.cell(200, 10, txt="위험 요소", ln=True)
        for line in risks.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.ln(5)
        pdf.cell(200, 10, txt=f"종합 위험 점수: {score}%", ln=True)
        # 문자열로 생성 후 latin-1로 인코딩
        pdf_str = pdf.output(dest='S')
        return pdf_str.encode('latin-1')

    # 다운로드 버튼
    pdf_bytes = generate_pdf(result["summary"], result["risks"], score)
    st.download_button(
        "분석 결과 PDF 다운로드",
        data=pdf_bytes,
        file_name=f"contract_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

    # 요약 및 QA
    st.subheader("📘 계약서 요약")
    st.markdown(result["summary"])

    model_choice = st.selectbox("GPT 모델 선택", ["gpt-3.5-turbo", "gpt-4"])
    llm = ChatOpenAI(model=model_choice, temperature=0)

    st.subheader("📌 분석 선택지")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.button("위험 요소 확인", on_click=lambda: st.session_state.update(analysis_choice="위험 요소 확인"))
    with c2: st.button("추천 수정내용", on_click=lambda: st.session_state.update(analysis_choice="위험 요소 추천 수정내용"))
    with c3: st.button("조항 질의", on_click=lambda: st.session_state.update(analysis_choice="조항 질의 (해설)"))
    with c4: st.button("종료", on_click=lambda: st.session_state.update(analysis_choice="종료"))

    if st.session_state.analysis_choice == "위험 요소 확인":
        st.subheader("⚠️ 위험 요소 탐지")
        # 실제 위험요소가 있을 때만 경고, 없으면 정보 메시지
        if result["risks"].strip():
            st.warning(result["risks"])
        else:
            st.info("위험 요소가 발견되지 않았습니다. 🔒")

    elif st.session_state.analysis_choice == "위험 요소 추천 수정내용":
        st.subheader("✏️ 추천 수정내용")
        if result["risks"].strip():
            keyword_suggestions = {
                "손해배상": "💡 손해배상 조항은 계약 불이행 시 과도한 책임을 임차인에게 전가할 수 있습니다. 손해배상 한도나 사유를 명확히 규정하는 것이 필요합니다.",
                "해지권": "💡 일방적 해지권은 임대인 또는 임차인 중 한쪽에 과도한 권한을 부여하여 계약의 형평성을 해칠 수 있습니다. 쌍방 합의에 의한 해지 조건으로 수정하는 것이 바람직합니다.",
                "보증금": "💡 보증금 반환 조건이 명확하지 않거나 임대인의 책임 범위가 불분명할 경우, 임차인에게 불리할 수 있습니다. 반환 시기 및 조건을 명시해야 합니다.",
                "이중계약": "💡 이중계약은 심각한 법적 분쟁을 초래할 수 있습니다. 계약 체결 전 등기부등본 확인과 계약 상대방의 실소유 여부를 반드시 검토해야 합니다.",
                "계약해지": "💡 계약해지 조항이 모호하거나 일방에 유리하게 작성되어 있다면, 공정한 해지 사유와 절차를 명확히 정해야 합니다.",
                "불공정": "💡 계약 내용이 일방적으로 편중되어 있다면, 불공정 조항으로 판단될 수 있습니다. 각 조항의 형평성과 상호 책임을 고려해야 합니다.",
                "확정일자": "💡 확정일자는 임차인의 보증금을 보호하는 핵심 절차입니다. 확정일자를 받지 않으면 우선순위 보호를 받기 어려우므로 반드시 명시해야 합니다.",
                "전입신고": "💡 전입신고는 보증금 보호와 직결되므로, 전입신고 기한과 방법을 명시하고 실행 가능성을 사전에 확인해야 합니다.",
                "등기부등본": "💡 등기부등본 확인은 기본 절차입니다. 근저당, 가압류, 소유주 정보 등을 사전에 확인하여 계약 안정성을 확보해야 합니다."
            }
            for keyword, suggestion in keyword_suggestions.items():
                if keyword in result["risks"]:
                    st.info(suggestion)
        else:
            st.info("위험 요소가 없으므로 추천 수정사항이 없습니다.")
    elif st.session_state.analysis_choice == "조항 질의 (해설)":
        st.subheader("❓ 계약 내용 질의")
        sample_qs = [
            "확정일자 조항이 빠져있나요?",
            "깡통전세 위험이 있나요?",
            "보증금 반환 책임은?",
            "전입신고 문제는?"
        ]
        for i, q in enumerate(sample_qs):
            if st.button(q, key=f"sq{i}"):
                st.session_state.user_question = q
        user_q = st.text_input("질문 입력", value=st.session_state.user_question)
        if user_q:
            with st.spinner("답변 생성 중..."):
                docs = search_existing_contracts(user_q)
                chain = load_qa_chain(llm, chain_type="stuff")
                answer = chain.run(input_documents=docs, question=user_q)
            st.success("🧾 해설:")
            st.markdown(answer)

    elif st.session_state.analysis_choice == "종료":
        st.subheader("🔚 종료하시겠습니까?")
        col_yes, col_no = st.columns(2)

        if col_yes.button("예"):
            # 메인 분석 상태만 초기화 (업로드 목록은 유지)
            st.session_state.analysis_result = None
            st.session_state.analysis_done = False
            st.session_state.analysis_choice = None
            st.session_state.show_uploader = False

            st.success("초기화 완료! 업로드 목록은 유지됩니다.")
            st.rerun()

        if col_no.button("아니요"):
            pass
    # 비교 기능 유지
    if st.button("📋 비교 대상 추가"):
        if len(st.session_state.compare_docs) < 2:
            st.session_state.compare_docs.append({
                "filename": uploaded_file.name,
                "summary": result["summary"],
                "risks": result["risks"]
            })
            st.success("✅ 비교 목록 추가")
        else:
            st.warning("⚠️ 최대 2개까지만")
