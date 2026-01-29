# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
# ]
# ///

import json
import os
import re
import subprocess


import requests
from bs4 import BeautifulSoup

# video_bvid 是一个从外部得到的单个视频ID
# video_bvid 是一个从外部得到的单个视频ID
video_bvid = os.getenv("BVID")

def load_secrets_bilibili_cookie():
    """向上查找 secrets.json 并提取 Cookie 字符串"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        secrets_path = os.path.join(current_dir, "secrets.json")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 优先返回拼接好的完整 Cookie 字符串
                    if data.get("BILIBILI_COOKIE"):
                        return data["BILIBILI_COOKIE"]
                    # 否则尝试拼接 SESSDATA
                    if data.get("SESSDATA"):
                        return f"SESSDATA={data['SESSDATA']}; bili_jct={data.get('BILI_JCT','')}"
            except:
                pass
        parent = os.path.dirname(current_dir)
        if parent == current_dir: break
        current_dir = parent
    return os.getenv("BILIBILI_COOKIE")

BILIBILI_COOKIE = load_secrets_bilibili_cookie()

# =========================   从B站下载视频和音频，然后进行合并  ================================
class BilibiliVideoAudio:
    def __init__(self, bvid):
        self.bvid = bvid
        self.headers = {
            "referer": "https://search.bilibili.com/all?keyword=%E4%B8%BB%E6%92%AD%E8%AF%B4%E8%81%94%E6%92%AD&from_source=webtop_search&spm_id_from=333.1007&search_source=5&page=4&o=90",
            "origin": "https://search.bilibili.com",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': BILIBILI_COOKIE
        }

    def get_video_audio(self):
        # 构造视频链接并发送请求获取页面内容
        url = f'https://www.bilibili.com/video/{self.bvid}/?spm_id_from=333.337.search-card.all.click&vd_source=14378ecd144bed421affe1fe0ddd8981'
        content = requests.get(url, headers=self.headers).content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')

        # 获取视频标题
        meta_tag = soup.head.find('meta', attrs={'name': 'title'})
        title = meta_tag['content']

        # 获取视频和音频链接
        pattern = r'window\.__playinfo__=({.*?})\s*</script>'
        json_data = re.findall(pattern, content)[0]
        data = json.loads(json_data)

        video_url = data['data']['dash']['video'][0]['base_url']
        audio_url = data['data']['dash']['audio'][0]['base_url']

        return {
            'title': title,
            'video_url': video_url,
            'audio_url': audio_url
        }

    def download_video_audio(self, url, filename):
        # 对文件名进行清理，去除不合规字符
        sanitized_filename = self.sanitize_filename(filename)
        try:
            # 发送请求下载视频或音频文件
            resp = requests.get(url, headers=self.headers).content
            download_path = os.path.join('D:\\video', sanitized_filename)  # 构造下载路径
            with open(download_path, mode='wb') as file:
                file.write(resp)
            print("{:*^30}".format(f"下载完成：{sanitized_filename}"))
        except Exception as e:
            print(e)

    def sanitize_filename(self, filename):
        # 定义不合规字符的正则表达式
        invalid_chars_regex = r'[\"*<>?\\|/:,]'

        # 替换不合规字符为空格
        sanitized_filename = re.sub(invalid_chars_regex, ' ', filename)

        return sanitized_filename

    def merge_video_audio(self, video_path, audio_path, output_path):
        """
        使用ffmpeg来合并视频和音频。
        """
        try:
            command = [
                r'D:\Program Files\ffmpeg-7.0.2-essentials_build\bin\ffmpeg.exe',
                '-y',  # 覆盖输出文件如果它已经存在
                '-i', video_path,  # 输入视频路径
                '-i', audio_path,  # 输入音频路径
                '-c', 'copy',  # 复制原始数据，不进行转码
                output_path  # 输出视频路径
            ]
            subprocess.run(command, check=True)
            print(f"视频和音频合并完成：{output_path}")
        except subprocess.CalledProcessError as e:
            print(f"合并失败: {e}")


def get_target_bvids():
    import sys
    # 1. 优先从命令行参数获取
    if len(sys.argv) > 1:
        raw_args = sys.argv[1:]
        all_found = []
        for arg in raw_args:
            found = re.findall(r'BV[a-zA-Z0-9]+', arg)
            all_found.extend(found)
        return list(set(all_found))
    
    # 2. 从环境变量获取
    env_bvid = os.getenv("BVID")
    if env_bvid:
        return [env_bvid]
        
    return []

def main():
    bvids = get_target_bvids()
    if not bvids:
        print("未发现 BVID，请通过命令行参数传入：python bili_video.py BVxxx BVyyy")
        return

    print(f"准备下载 {len(bvids)} 个视频...")
    
    # 确保基础目录存在
    if not os.path.exists('D:\\video'):
        os.makedirs('D:\\video')

    processed_videos_path = 'D:\\processed_videos'
    if not os.path.exists(processed_videos_path):
        os.makedirs(processed_videos_path)

    for index, bvid in enumerate(bvids, 1):
        print(f"\n[{index}/{len(bvids)}] 正在下载: {bvid}")
        try:
            bilibili = BilibiliVideoAudio(bvid)
            video_audio_info = bilibili.get_video_audio()

            title = video_audio_info['title']
            video_url = video_audio_info['video_url']
            audio_url = video_audio_info['audio_url']

            video_filename = f"{title}.mp4"
            audio_filename = f"{title}.mp3"
            output_filename = f"{title} - combined.mp4"

            # 对文件名进行清理
            sanitized_video_filename = bilibili.sanitize_filename(video_filename)
            sanitized_audio_filename = bilibili.sanitize_filename(audio_filename)
            sanitized_output_filename = bilibili.sanitize_filename(output_filename)

            video_file_path = os.path.join('D:\\video', sanitized_video_filename)
            audio_file_path = os.path.join('D:\\video', sanitized_audio_filename)
            output_file_path = os.path.join(processed_videos_path, sanitized_output_filename)

            bilibili.download_video_audio(video_url, sanitized_video_filename)  # 下载视频
            bilibili.download_video_audio(audio_url, sanitized_audio_filename)  # 下载音频
            bilibili.merge_video_audio(video_file_path, audio_file_path, output_file_path)  # 合并视频和音频

        except Exception as ex:
            print(f"❌ 视频 {bvid} 下载失败: {ex}")

    print("\n所有任务执行完毕。")

if __name__ == "__main__":
    main()
