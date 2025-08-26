import streamlit as st
from style import inject_custom_css
import pandas as pd
import joblib
import re
from datetime import datetime, date
import plotly.express as px
import time
import emoji
import calendar

def run():
    # Cấu hình trang
    st.set_page_config(page_title="Dự báo Hành vi", layout="wide")
    inject_custom_css()

    # Load mô hình + encoder + features
    @st.cache_resource
    def load_model():
        data = joblib.load("model/model_base_multiclass.joblib")
        return data['model'], data['label_encoders'], data['features']
    try:
        with st.spinner("Đang tải mô hình..."):
            model, label_encoders, feature_cols = load_model()
    except Exception as e:
        st.error(f"Không thể tải mô hình: {e}")
        st.stop()

    target_cols = list(label_encoders.keys())

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Dự báo hành vi người dùng trên mạng xã hội</h1>
        <p>Hệ thống demo dựa trên Scikit-learn, dự đoán mức độ tương tác</p>
    </div>
    """, unsafe_allow_html=True)

    # Hàm trích xuất đặc trưng
    @st.cache_data
    def extract_features(post_text, post_date, post_time_str):
        if not post_text or pd.isna(post_text):
            post_text = ""
        char_count = len(post_text)
        hashtag_count = len(re.findall(r'#\w+', post_text))
        mention_count = len(re.findall(r'@\w+', post_text))
        url_count = len(re.findall(r'https?://\S+', post_text))
        has_emoji = int(any(c in emoji.EMOJI_DATA for c in post_text))
        has_caps_words = int(bool(re.search(r'\b[A-Z]{2,}\b', post_text)))

        time_parts = post_time_str.split(':') if post_time_str else ['0', '0']
        hour = int(time_parts[0])
        minute = int(time_parts[1])

        day_of_week = post_date.weekday() if post_date else 0
        is_weekend = int(day_of_week >= 5)
        month = post_date.month if post_date else 1

        return {
            'char_count': char_count,
            'hashtag_count': hashtag_count,
            'mention_count': mention_count,
            'url_count': url_count,
            'has_emoji': has_emoji,
            'has_caps_words': has_caps_words,
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'month': month,
            'minute': minute
        }

    # Form nhập liệu
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header('Nhập thông tin bài đăng')
        with st.form(key='post_form'):
            post_text = st.text_area("Nội dung bài đăng", height=100, placeholder="Nhập nội dung...")
            st.divider()

            # Ngày giờ (vẫn giữ AM/PM)
            st.markdown("### Thời gian đăng")
            col_date1, col_date2, col_date3 = st.columns(3)
            current_year = datetime.now().year
            with col_date1:
                years = list(range(2020, current_year + 1))
                selected_year = st.selectbox("Năm", options=years, index=len(years)-1)
            with col_date2:
                months = list(range(1, 13))
                selected_month = st.selectbox("Tháng", options=months, index=datetime.now().month-1)
            with col_date3:
                days_in_month = calendar.monthrange(selected_year, selected_month)[1]
                days = list(range(1, days_in_month + 1))
                selected_day = st.selectbox("Ngày", options=days, index=datetime.now().day-1)

            col_time1, col_time2, col_time3 = st.columns(3)
            with col_time1:
                selected_hour = st.selectbox("Giờ", list(range(1, 13)))
            with col_time2:
                selected_minute = st.selectbox("Phút", list(range(0, 60)))
            with col_time3:
                am_pm = st.selectbox("Buổi", ["AM", "PM"])

            try:
                hour_24 = selected_hour % 12 + (12 if am_pm == "PM" else 0)
                post_date = date(selected_year, selected_month, selected_day)
                post_time_str = f"{hour_24:02d}:{selected_minute:02d}"
            except:
                st.error("Lỗi khi xử lý ngày giờ")
                post_date = date.today()
                post_time_str = datetime.now().strftime('%H:%M')
            st.divider()

            # Thông tin tài khoản
            st.markdown("### Thông tin tài khoản")
            col_acc1, col_acc2, col_acc3 = st.columns(3)
            with col_acc1:
                user_followers_count = st.number_input("Số Followers", min_value=0, placeholder="Ví dụ: 1200")
            with col_acc2:
                user_following_count = st.number_input("Số Following", min_value=0, placeholder="Ví dụ: 800")
            with col_acc3:
                user_post_count = st.number_input("Tổng Bài đăng", min_value=0, placeholder="Ví dụ: 350")
            st.divider()

            # Media & loại bài
            st.markdown("### Tùy chọn bài đăng")
            col_opt1, _, col_opt2 = st.columns([1, 0.2, 1])
            with col_opt1:
                photo_count = st.number_input("Số hình ảnh", min_value=0, max_value=4, value=0)
                video_count = st.number_input("Số video", min_value=0, max_value=4, value=0)
                animated_gif_count = st.number_input("Số GIF", min_value=0, max_value=4, value=0)
            with col_opt2:
                is_repost = st.checkbox("Bài chia sẻ lại (Repost)")
                is_reply = st.checkbox("Là trả lời (Reply)")
                is_quote = st.checkbox("Là trích dẫn (Quote)")

            submit_button = st.form_submit_button("Dự báo")

    with col2:
        st.header('Thống kê nhanh & gợi ý')
        if post_text:
            char_count = len(post_text)
            hashtag_count = len(re.findall(r'#\w+', post_text))
            mention_count = len(re.findall(r'@\w+', post_text))
            url_count = len(re.findall(r'https?://\S+', post_text))
            has_emoji = int(any(c in emoji.EMOJI_DATA for c in post_text))
            has_caps_words = int(bool(re.search(r'\b[A-Z]{2,}\b', post_text)))
            media_total = photo_count + video_count + animated_gif_count
            is_influencer = int(user_followers_count > 100_000)

            stats = [
                ("Số ký tự", char_count),
                ("Số URL", url_count),
                ("Số Hashtags", hashtag_count),
                ("Số Mentions", mention_count),
                ("Emoji", "Có" if has_emoji else "Không"),
                ("Từ IN HOA", "Có" if has_caps_words else "Không"),
                ("Tổng media", media_total),
                ("Influencer", "Có" if is_influencer else "Không"),
            ]
            for label, value in stats:
                st.markdown(f"<div style='display:flex;justify-content:space-between'><span>{label}</span><span style='font-weight:600'>{value}</span></div>", unsafe_allow_html=True)

            st.write("---")
            if hashtag_count == 0:
                st.info("Thêm 1–2 hashtag có liên quan để tăng khả năng hiển thị.")
            if not has_emoji:
                st.info("Cân nhắc thêm 1 emoji để bài đăng sinh động hơn.")
            if char_count < 20:
                st.info("Nội dung khá ngắn, thử mở rộng để tăng tương tác.")
        else:
            st.info("Nhập nội dung để xem thống kê")

    # Dự báo
    if submit_button:
        if not post_text.strip():
            st.error("Vui lòng nhập nội dung bài đăng!")
        else:
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.005)
            progress_bar.empty()

            input_data = extract_features(post_text, post_date, post_time_str)
            input_data.update({
                'user_followers_count': user_followers_count,
                'user_following_count': user_following_count,
                'user_post_count': user_post_count,
                'is_repost': int(is_repost),
                'is_reply': int(is_reply),
                'is_quote': int(is_quote),
                'has_photo': int(photo_count > 0),
                'has_video': int(video_count > 0),
                'has_animated_gif': int(animated_gif_count > 0),
                'media_count': photo_count + video_count + animated_gif_count,
                'is_influencer': int(user_followers_count > 100_000)
            })
            input_df = pd.DataFrame([input_data], columns=feature_cols)

            try:
                preds = model.predict(input_df)
                probas = model.predict_proba(input_df)

                st.success("Dự báo hoàn tất!")
                st.markdown('<h2 class="section-header">Kết quả dự báo</h2>', unsafe_allow_html=True)
                st.caption("Tỉ lệ % thể hiện xác suất mô hình dự đoán mức độ này xảy ra.")

                cols = st.columns(4)
                prediction_data = []
                for i, col in enumerate(target_cols):
                    le = label_encoders[col]
                    pred_label = le.inverse_transform([preds[0, i]])[0]
                    proba_dict = dict(zip(le.classes_, probas[i][0]))
                    top_prob = proba_dict[pred_label]

                    with cols[i]:
                        st.markdown(f"""
                        <div class="predict-card">
                            <div class="predict-card-title">{col}</div>
                            <div>{pred_label}</div>
                            <div class="predict-card-prob">{top_prob:.1%}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    for level, prob in proba_dict.items():
                        prediction_data.append({
                            'Hành vi': col,
                            'Mức': level,
                            'Xác suất': prob
                        })

                if prediction_data:
                    prob_df = pd.DataFrame(prediction_data)
                    fig = px.bar(
                        prob_df, x='Hành vi', y='Xác suất',
                        color='Mức', barmode='group',
                        title="Xác suất dự đoán theo từng mức"
                    )
                    fig.update_layout(
                        yaxis_tickformat=".1%",
                        yaxis_title="Xác suất (%)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend_title="Mức"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Lỗi dự báo: {e}")

    st.markdown('<div class="footer">© 2025 - Phạm Tấn Vương</div>', unsafe_allow_html=True)