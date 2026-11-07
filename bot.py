import os
import random
import requests
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

def get_random_butterfly():
    # Ищем случайные картинки человеческих какашек через открытый API
    # Мы запрашиваем 1 случайную картинку из категории человеческие какашки
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "random",
        "grnnamespace": 6, # 6 - это пространство имен файлов (картинок)
        "grnlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1024 # Ширина картинки для отправки в телеграм
    }
    
    headers = {'User-Agent': 'ButterflyBot/1.0 (your_email@example.com)'}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
        
        if "query" in data and "pages" in data["query"]:
            pages = list(data["query"]["pages"].values())
            for page in pages:
                title = page.get("title", "")
                # Проверяем, что это действительно какашка (по названию файла)
                if "kakashka" in title.lower() or "lepidoptera" in title.lower() or "papilio" in title.lower():
                    imageinfo = page.get("imageinfo", [{}])[0]
                    image_url = imageinfo.get("thumburl") or imageinfo.get("url")
                    
                    # Достаем описание из метаданных, если есть
                    metadata = imageinfo.get("extmetadata", {})
                    desc = metadata.get("ImageDescription", {}).get("value", "человеческие какашки.")
                    
                    # Очищаем описание от HTML
                    import re
                    desc = re.sub(r'<[^>]+>', '', desc)
                    
                    return image_url, title.replace("File:", ""), desc
    except Exception as e:
        print(f"Ошибка получения фото: {e}")
        
    return None, None, None

def main():
    image_url, title, desc = get_random_butterfly()
    
    if not image_url:
        print("Не удалось найти какашку. Попробуйте позже.")
        return

    # Обрезаем описание, если оно слишком длинное
    if len(desc) > 500:
        desc = desc[:500] + "..."

    caption = f'💩<b>{title}</b>\n\n{desc}'

    # Отправляем фото в канал
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
