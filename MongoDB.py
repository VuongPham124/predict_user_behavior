import pandas as pd
import ast
import numpy as np
from pymongo import MongoClient

# ====== Cấu hình ======
MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'db'

# Danh sách các file và collection tương ứng
DATA_CONFIGS = [
    {'csv_path': 'data_base.csv', 'collection': 'posts_base'},
    {'csv_path': 'data_full.csv', 'collection': 'posts_full'},
]

# ====== Kết nối MongoDB ======
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ====== Xử lý từng file ======
for config in DATA_CONFIGS:
    csv_path = config['csv_path']
    collection_name = config['collection']
    collection = db[collection_name]

    print(f'Đang xử lý file: {csv_path}')

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f'Không thể đọc file {csv_path}: {e}')
        continue

    # Thay NaN thành chuỗi 'None' để lưu dạng text trong MongoDB
    df = df.fillna('None')

    # Chuyển đổi chuỗi sang list/dict nếu có cột phù hợp
    columns_to_eval = ['media_path_list']
    for col in columns_to_eval:
        if col in df.columns:
            try:
                df[col] = df[col].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) and (x.startswith('[') or x.startswith('{')) else x
                )
            except Exception as e:
                print(f'Không thể chuyển cột {col} trong {csv_path}: {e}')

    # Xử lý cột cleaned_text nếu có
    if 'cleaned_text' in df.columns:
        df['cleaned_text'] = df['cleaned_text'].replace(
            to_replace=['NaN', 'nan', None],
            value=''
        )

    # Chuyển đổi và chèn vào MongoDB
    records = df.to_dict(orient='records')
    if records:
        # Xoá collection cũ (nếu có)
        collection.drop()
        print(f'Đã xóa collection cũ: {collection_name}')

        # Chèn dữ liệu mới
        collection.insert_many(records)
        print(f'Đã lưu {len(records)} dòng vào collection {collection_name}.')
    else:
        print(f'Không có dữ liệu để chèn từ file {csv_path}.')