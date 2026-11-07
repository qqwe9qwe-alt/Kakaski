import os
import random
import re
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

def get_random_butterfly():
    """
    从 Wikimedia Commons 的 Category:Human_feces 获取随机图片。
    先拉取分类下的文件列表，随机选一个，再查它的 imageinfo。
    """
    api_url = "https://commons.wikimedia.org/w/api.php"
    headers = {'User-Agent': 'ButterflyBot/1.0 (your_email@example.com)'}

    # 第一步：列出 Category:Human_feces 下的所有文件
    list_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Human_feces",  # 目标分类
        "cmtype": "file",
        "cmlimit": "50",  # 一次取 50 个，够随机选了
    }

    try:
        resp = requests.get(api_url, params=list_params, headers=headers, timeout=15)
        data = resp.json()
        members = data.get("query", {}).get("categorymembers", [])

        if not members:
            print("分类中没有找到文件。")
            return None, None, None

        # 随机选一个文件标题
        chosen = random.choice(members)
        title = chosen["title"]  # 形如 "File:Xxx.jpg"

        # 第二步：查这个文件的 imageinfo（URL + 描述）
        info_params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 1024,  # 缩略图宽度
        }

        resp2 = requests.get(api_url, params=info_params, headers=headers, timeout=15)
        data2 = resp2.json()
        pages = data2.get("query", {}).get("pages", {})

        for page in pages.values():
            imageinfo = page.get("imageinfo", [{}])[0]
            image_url = imageinfo.get("thumburl") or imageinfo.get("url")
            if not image_url:
                continue

            metadata = imageinfo.get("extmetadata", {})
            desc = metadata.get("ImageDescription", {}).get("value", "человеческие какашки.")
            desc = re.sub(r'<[^>]+>', '', desc)  # 去 HTML

            clean_title = title.replace("File:", "")
            return image_url, clean_title, desc

    except Exception as e:
        print(f"Ошибка получения фото: {e}")

    return None, None, None


def main():
    image_url, title, desc = get_random_butterfly()

    if not image_url:
        print("Не удалось найти какашку. Попробуйте позже.")
        return

    if len(desc) > 500:
        desc = desc[:500] + "..."

    caption = f'💩<b>{title}</b>\n\n{desc}'

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML"
    }

    resp = requests.post(url, json=payload, timeout=30)

    if resp.ok:
        print(f"Успешно опубликовано: {title}")
    else:
        print(f"Ошибка Telegram: {resp.text}")


if __name__ == "__main__":
    main()
