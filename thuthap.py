import os
import time
import requests
import tweepy
import pandas as pd
from yt_dlp import YoutubeDL

# --- Thông tin xác thực ---
BEARER_TOKEN = ''
USERNAME = ''

client = tweepy.Client(bearer_token=BEARER_TOKEN)

# --- Lấy thông tin người dùng ---
user = client.get_user(username=USERNAME)
user_id = user.data.id
user_info = client.get_user(id=user_id, user_fields=['public_metrics'])
user_metrics = user_info.data.public_metrics

# --- Tạo thư mục lưu media ---
media_dir = os.path.join('media', USERNAME)
os.makedirs(media_dir, exist_ok=True)

# --- Tải ảnh ---
def download_media_image(media_url, tweet_id, index):
    try:
        response = requests.get(media_url)
        if response.status_code == 200:
            ext = '.jpg' if 'jpg' in media_url or 'jpeg' in media_url else '.png'
            filename = os.path.normpath(f'{media_dir}/{tweet_id}_image_{index}{ext}').replace('\\', '/')
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f'Lỗi khi tải ảnh: {e}')
    return None

# --- Tải video ---
def download_twitter_video(tweet_url, tweet_id, index):
    outtmpl = os.path.normpath(f'{media_dir}/{tweet_id}_video_{index}.%(ext)s').replace('\\', '/')
    ydl_opts = {
        'outtmpl': outtmpl,
        'quiet': True,
        'format': 'bestvideo+bestaudio/best'
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tweet_url, download=True)
            path = ydl.prepare_filename(info)
            if os.path.exists(path):
                return os.path.normpath(path).replace('\\', '/')
            else:
                print(f'File video không tồn tại: {path}')
    except Exception as e:
        print(f'Lỗi khi tải video: {e}')
    return None

# --- Thu thập tweet ---
def fetch_user_tweets(user_id):
    tweets_data = []
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            response = client.get_users_tweets(
                id=user_id,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics', 'text', 'entities', 'referenced_tweets', 'attachments'],
                expansions=['attachments.media_keys'],
                media_fields=['media_key', 'type', 'url', 'preview_image_url']
            )

            tweets = response.data
            media = response.includes.get('media', []) if response.includes else []
            media_dict = {m['media_key']: m for m in media}

            if tweets:
                print(f"Đã tìm thấy {len(tweets)} tweet.")
                for tweet in tweets:
                    media_types = []
                    media_paths = []

                    if tweet.attachments and 'media_keys' in tweet.attachments:
                        for index, key in enumerate(tweet.attachments['media_keys']):
                            m = media_dict.get(key)
                            if m:
                                media_types.append(m['type'])
                                if m['type'] == 'photo':
                                    media_url = m.get('url')
                                    path = download_media_image(media_url, tweet.id, index)
                                    if path and os.path.exists(path):
                                        media_paths.append(path)
                                    else:
                                        print(f'Ảnh không tồn tại hoặc lỗi tải: {path}')
                                elif m['type'] in ['video', 'animated_gif']:
                                    tweet_url = f'https://twitter.com/{USERNAME}/status/{tweet.id}'
                                    path = download_twitter_video(tweet_url, tweet.id, index)
                                    if path and os.path.exists(path):
                                        media_paths.append(path)
                                    else:
                                        print(f'Video không tồn tại hoặc lỗi tải: {path}')

                    entities = tweet.entities or {}
                    hashtags = entities.get('hashtags', [])
                    mentions = entities.get('mentions', [])
                    urls = entities.get('urls', [])

                    tweet_info = {
                        'post_id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'char_count': len(tweet.text),
                        'hashtag_count': len(hashtags),
                        'mention_count': len(mentions),
                        'url_count': len(urls),
                        'media_type': ','.join(media_types) if media_paths else '',
                        'media_path': ','.join(media_paths) if media_paths else '',
                        'is_repost': any(ref.type == 'retweeted' for ref in tweet.referenced_tweets or []),
                        'is_reply': any(ref.type == 'replied_to' for ref in tweet.referenced_tweets or []),
                        'is_quote': any(ref.type == 'quoted' for ref in tweet.referenced_tweets or []),
                        'repost_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'user_followers_count': user_metrics['followers_count'],
                        'user_following_count': user_metrics['following_count'],
                        'user_post_count': user_metrics['tweet_count'],
                    }

                    tweets_data.append(tweet_info)

            return tweets_data

        except tweepy.TooManyRequests:
            wait_time = 2 ** retries
            print(f'Quá giới hạn, chờ {wait_time} giây...')
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            print(f'Lỗi không xác định: {e}')
            break

    return None

# --- Thu thập và xuất dữ liệu ---
tweets_data = fetch_user_tweets(user_id)

if not tweets_data:
    print("Không thu thập được tweet nào.")
    df = pd.DataFrame()
else:
    df = pd.DataFrame(tweets_data)

if 'media_path' in df.columns:
    df['media_path'] = df['media_path'].str.replace('\\', '/', regex=False)
else:
    print("Cột 'media_path' không tồn tại — bỏ qua chuẩn hóa đường dẫn.")

# --- Lưu ra file CSV ---
if not df.empty:
    output_csv = f'{USERNAME}.csv'
    df.to_csv(output_csv, index=False)
    print(f"Đã lưu dữ liệu vào: {output_csv}")
else:
    print("DataFrame rỗng — không xuất file CSV.")