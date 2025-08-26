import streamlit as st
import pandas as pd
from pymongo import MongoClient
import joblib

# Kết nối MongoDB
DB_NAME = "db"
COLLECTION_NAME = "posts_base"
MONGO_URI = "mongodb://localhost:27017"

# Lấy target_cols từ model
model_data = joblib.load("model/model_base_multiclass.joblib")
label_encoders = model_data['label_encoders']
target_cols = list(label_encoders.keys())  # ví dụ: ['Like_Level', 'Reply_Level', 'Quote_Level', 'Repost_Level']

def get_data_from_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    data = list(collection.find())
    df = pd.DataFrame(data)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df

def run():
    st.title("Kết quả dự báo mẫu")

    df = get_data_from_mongodb()

    column_display_map = {
        'char_count': 'Số ký tự',
        'hashtag_count': 'Số hashtag',
        'mention_count': 'Số mention (@)',
        'url_count': 'Số URL',
        'is_retweet': 'Là Retweet',
        'is_reply': 'Là Reply',
        'is_quote': 'Là Quote',
        'user_followers_count': 'Số followers',
        'user_following_count': 'Số following',
        'user_post_count': 'Tổng số bài đăng',
        'has_emoji': 'Có emoji',
        'has_caps_words': 'Có chữ IN HOA',
        'has_photo': 'Có ảnh',
        'has_video': 'Có video',
        'has_animated_gif': 'Có GIF',
        'media_count': 'Tổng media',
        'hour': 'Giờ đăng',
        'day_of_week': 'Thứ trong tuần',
        'is_weekend': 'Cuối tuần',
        'month': 'Tháng đăng',
        'is_influencer': 'Là Influencer',
    }

    df = df.rename(columns=column_display_map)

    feature_cols = [col for col in df.columns if col not in target_cols]

    df_features = df[feature_cols].head(100).reset_index().rename(columns={'index': 'STT'})
    df_features['STT'] = df_features['STT'] + 1

    df_targets = df[target_cols].head(100).reset_index().rename(columns={'index': 'STT'})
    df_targets['STT'] = df_targets['STT'] + 1

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Đặc trưng đầu vào")
        st.dataframe(df_features, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Kết quả dự báo")
        st.dataframe(df_targets, use_container_width=True, hide_index=True)