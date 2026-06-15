import streamlit as st
import google.generativeai as genai
import os
import json
import re

st.set_page_config(
    page_title="HR AI Tool – Tuyển Dụng Thông Minh",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
  .stTextArea textarea { font-size: 13px; }
  .stTextInput input  { font-size: 13px; }
  .tip-box {
    background: #EEF2FF;
    border-left: 3px solid #4F46E5;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 13px;
    margin-bottom: 12px;
  }
  .score-high { color: #10B981; font-size: 32px; font-weight: 800; }
  .score-mid  { color: #F59E0B; font-size: 32px; font-weight: 800; }
  .score-low  { color: #EF4444; font-size: 32px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ---- SETUP GEMINI ----
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY. Xem file HUONG_DAN_DEPLOY.md để biết cách thêm.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

def ask_ai(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text

# ---- HEADER ----
st.markdown("## 🤖 HR AI Tool – Tuyển Dụng Thông Minh")
st.caption("Tạo content tuyển dụng & lọc CV tự động bằng AI · Miễn phí 100%")
st.divider()

tab1, tab2, tab3 = st.tabs(["✍️ Content Facebook", "💬 Tạo Comment", "📋 Lọc CV"])

# ============================================================
# TAB 1: CONTENT FACEBOOK
# ============================================================
with tab1:
    st.markdown('<div class="tip-box">💡 Nhập JD, chọn phong cách → AI tạo bài post Facebook tuyển dụng ngay.</div>', unsafe_allow_html=True)

    position = st.text_input("Vị trí tuyển dụng *", placeholder="Frontend Developer, Kế toán tổng hợp...", key="c_pos")
    col1, col2 = st.columns(2)
    with col1:
        salary = st.text_input("Mức lương", placeholder="15-25 triệu, Thỏa thuận...", key="c_sal")
    with col2:
        location = st.text_input("Địa điểm", placeholder="TP.HCM, Remote...", key="c_loc")

    jd = st.text_area("Yêu cầu & mô tả công việc *", height=160,
        placeholder="Dán JD vào đây: kinh nghiệm, kỹ năng, học vấn, phúc lợi...", key="c_jd")

    col3, col4 = st.columns(2)
    with col3:
        tone = st.selectbox("Phong cách", [
            "🤝 Thân thiện & gần gũi",
            "👔 Chuyên nghiệp",
            "🔥 Gấp & thu hút",
            "🎨 Sáng tạo & độc đáo"
        ], key="c_tone")
    with col4:
        length = st.selectbox("Độ dài", [
            "📝 Vừa (200-300 chữ)",
            "✂️ Ngắn (~150 chữ)",
            "📃 Đầy đủ (400+ chữ)"
        ], key="c_len")

    if st.button("✨ Tạo bài post Facebook", type="primary", key="btn_content"):
        if not position or not jd:
            st.warning("⚠️ Vui lòng nhập vị trí và JD")
        else:
            tone_map = {
                "🤝 Thân thiện & gần gũi": "thân thiện, gần gũi, dùng emoji phù hợp",
                "👔 Chuyên nghiệp": "chuyên nghiệp, lịch sự, trang trọng",
                "🔥 Gấp & thu hút": "tạo cảm giác gấp, thu hút, có deadline cụ thể",
                "🎨 Sáng tạo & độc đáo": "sáng tạo, độc đáo, khác biệt"
            }
            len_map = {
                "📝 Vừa (200-300 chữ)": "200-300 từ",
                "✂️ Ngắn (~150 chữ)": "~150 từ",
                "📃 Đầy đủ (400+ chữ)": "400+ từ"
            }
            prompt = f"""Bạn là chuyên gia viết content tuyển dụng cho HR Freelancer tại Việt Nam.

Viết 1 bài post Facebook tuyển dụng:
- Vị trí: {position}
- Lương: {salary or 'Thỏa thuận'}
- Địa điểm: {location or 'Linh hoạt'}
- Phong cách: {tone_map[tone]}
- Độ dài: {len_map[length]}

JD:
{jd}

Yêu cầu: tiêu đề bắt mắt, mô tả ngắn gọn, yêu cầu ứng viên (3-5 điểm), quyền lợi nổi bật, call-to-action. Chỉ trả về bài post, không giải thích thêm."""

            with st.spinner("AI đang soạn bài viết..."):
                result = ask_ai(prompt)
            st.success("✅ Bài post đã tạo!")
            st.text_area("📱 Kết quả (click để copy):", value=result, height=320, key="c_result")

# ============================================================
# TAB 2: COMMENT
# ============================================================
with tab2:
    st.markdown('<div class="tip-box">💡 Tạo nhiều mẫu comment để đăng group, reply ứng viên hoặc nhờ giới thiệu.</div>', unsafe_allow_html=True)

    cm_pos = st.text_input("Vị trí / Ngành nghề tuyển *", placeholder="Senior ReactJS, Nhân viên kinh doanh...", key="cm_pos")
    col5, col6 = st.columns(2)
    with col5:
        cm_sal = st.text_input("Mức lương", placeholder="Up to 30M, Hấp dẫn...", key="cm_sal")
    with col6:
        cm_loc = st.text_input("Địa điểm", placeholder="TP.HCM, Remote...", key="cm_loc")

    cm_type = st.selectbox("Mục đích comment", [
        "📢 Đăng vào group tìm việc",
        "💌 Reply ứng viên đang tìm việc",
        "🤝 Nhờ bạn bè giới thiệu",
        "👤 Comment dưới profile ứng viên tiềm năng"
    ], key="cm_type")

    cm_extra = st.text_area("Thông tin thêm (tùy chọn)", height=70,
        placeholder="Phúc lợi nổi bật, deadline, điểm đặc biệt...", key="cm_extra")

    col7, col8 = st.columns(2)
    with col7:
        cm_count = st.selectbox("Số lượng mẫu", ["3 mẫu", "5 mẫu", "1 mẫu"], key="cm_count")
    with col8:
        cm_tone = st.selectbox("Phong cách", [
            "🤝 Thân thiện",
            "👔 Chuyên nghiệp",
            "⚡ Ngắn gọn & thẳng"
        ], key="cm_tone")

    if st.button("✨ Tạo comment", type="primary", key="btn_comment"):
        if not cm_pos:
            st.warning("⚠️ Vui lòng nhập vị trí tuyển")
        else:
            type_map = {
                "📢 Đăng vào group tìm việc": "đăng vào group tìm việc Facebook",
                "💌 Reply ứng viên đang tìm việc": "reply bài post của ứng viên đang tìm việc",
                "🤝 Nhờ bạn bè giới thiệu": "nhờ bạn bè giới thiệu ứng viên",
                "👤 Comment dưới profile ứng viên tiềm năng": "comment dưới profile ứng viên tiềm năng"
            }
            tone_map2 = {
                "🤝 Thân thiện": "thân thiện, tự nhiên, emoji phù hợp",
                "👔 Chuyên nghiệp": "chuyên nghiệp, lịch sự",
                "⚡ Ngắn gọn & thẳng": "ngắn gọn, thẳng vào vấn đề"
            }
            count_map = {"3 mẫu": "3", "5 mẫu": "5", "1 mẫu": "1"}
            prompt = f"""Bạn là HR Freelancer chuyên nghiệp tại Việt Nam. Viết {count_map[cm_count]} mẫu comment để {type_map[cm_type]}.

Thông tin:
- Vị trí: {cm_pos}
- Lương: {cm_sal or 'Thỏa thuận, hấp dẫn'}
- Địa điểm: {cm_loc or 'Linh hoạt'}
- Phong cách: {tone_map2[cm_tone]}
{f'- Thêm: {cm_extra}' if cm_extra else ''}

Yêu cầu: mỗi comment 2-5 câu, tự nhiên, có call-to-action, đánh số Mẫu 1:, Mẫu 2:... Chỉ trả về các mẫu, không giải thích."""

            with st.spinner("AI đang soạn comment..."):
                result = ask_ai(prompt)
            st.success("✅ Các mẫu comment đã tạo!")
            st.text_area("💬 Kết quả:", value=result, height=280, key="cm_result")

# ============================================================
# TAB 3: LỌC CV
# ============================================================
with tab3:
    st.markdown('<div class="tip-box">💡 Dán JD và CV, AI chấm điểm 0-100 và phân tích chi tiết.</div>', unsafe_allow_html=True)

    cv_jd = st.text_area("📋 Job Description (JD) *", height=150,
        placeholder="Dán toàn bộ JD: vị trí, yêu cầu, kỹ năng, học vấn...", key="cv_jd")
    st.divider()

    col9, col10 = st.columns(2)
    with col9:
        cv_name = st.text_input("Tên ứng viên", placeholder="Nguyễn Văn A", key="cv_name")
    with col10:
        cv_pos = st.text_input("Vị trí apply", placeholder="Frontend Developer...", key="cv_pos")

    cv_content = st.text_area("Nội dung CV *", height=200,
        placeholder="Dán CV vào đây: học vấn, kinh nghiệm, kỹ năng, thành tích...", key="cv_content")

    if st.button("🔍 Phân tích & Chấm điểm CV", type="primary", key="btn_cv"):
        if not cv_jd or not cv_content:
            st.warning("⚠️ Vui lòng nhập JD và nội dung CV")
        else:
            name = cv_name or "Ứng viên"
            prompt = f"""Phân tích mức độ phù hợp của ứng viên với JD. Chỉ trả về JSON (không text ngoài JSON):

JD: {cv_jd}

CV của {name}{f' (vị trí: {cv_pos})' if cv_pos else ''}: {cv_content}

JSON format:
{{"score":<0-100>,"verdict":"<Phù hợp cao/Phù hợp/Cần xem xét/Không phù hợp>","summary":"<1-2 câu tóm tắt>","strengths":["điểm 1","điểm 2","điểm 3"],"weaknesses":["điểm 1","điểm 2"],"recommendation":"<khuyến nghị cho HR>"}}"""

            with st.spinner("AI đang phân tích CV..."):
                raw = ask_ai(prompt)

            try:
                m = re.search(r'\{[\s\S]*\}', raw)
                data = json.loads(m.group(0) if m else raw)
                score = data.get("score", 0)

                css_class = "score-high" if score >= 70 else ("score-mid" if score >= 50 else "score-low")
                emoji = "🟢" if score >= 70 else ("🟡" if score >= 50 else "🔴")

                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.markdown(f'<div class="{css_class}">{score}/100</div>', unsafe_allow_html=True)
                    st.markdown(f"**{data.get('verdict', '')}**")
                with col_b:
                    st.markdown(f"### 👤 {name}")
                    st.write(data.get("summary", ""))

                st.divider()
                col_c, col_d = st.columns(2)
                with col_c:
                    st.markdown("**✅ Điểm phù hợp**")
                    for s in data.get("strengths", []):
                        st.markdown(f"- {s}")
                with col_d:
                    st.markdown("**⚠️ Điểm thiếu / yếu**")
                    for w in data.get("weaknesses", []):
                        st.markdown(f"- {w}")

                if data.get("recommendation"):
                    st.info(f"💡 **Khuyến nghị:** {data['recommendation']}")

                if "cv_history" not in st.session_state:
                    st.session_state.cv_history = []
                st.session_state.cv_history.append({
                    "name": name, "pos": cv_pos, "score": score,
                    "verdict": data.get("verdict", ""), "summary": data.get("summary", "")
                })

            except Exception:
                st.text_area("Kết quả phân tích:", value=raw, height=300)

    if "cv_history" in st.session_state and st.session_state.cv_history:
        st.divider()
        st.markdown("### 📊 Kết quả đã phân tích (xếp theo điểm)")
        for i, item in enumerate(sorted(st.session_state.cv_history, key=lambda x: x["score"], reverse=True), 1):
            s = item["score"]
            emoji = "🟢" if s >= 70 else ("🟡" if s >= 50 else "🔴")
            with st.expander(f"#{i} {emoji} {item['name']} — {s}/100 · {item['verdict']}"):
                if item.get("pos"):
                    st.caption(f"Vị trí: {item['pos']}")
                st.write(item.get("summary", ""))
        if st.button("🗑️ Xóa lịch sử"):
            st.session_state.cv_history = []
            st.rerun()

st.divider()
st.caption("HR AI Tool · Powered by Gemini AI · Miễn phí 100%")
