import os
import random
import re
import time
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

def get_random_butterfly():
    api_url = "https://commons.wikimedia.org/w/api.php"
    # Обязательно укажите свой реальный email или никнейм в User-Agent
    headers = {'User-Agent': 'ButterflyBot/1.0 (your_email@example.com)'}

    # Шаг 1: Получаем список файлов из нужной категории
    list_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Human_feces",
        "cmtype": "file",
        "cmlimit": "50",
    }

    try:
        resp = requests.get(api_url, params=list_params, headers=headers, timeout=15)
        data = resp.json()
        members = data.get("query", {}).get("categorymembers", [])

        if not members:
            print("Категория пуста или не найдена.")
            return None, None, None

        # Выбираем случайный файл из списка
        chosen = random.choice(members)
        title = chosen["title"]

        # Шаг 2: Запрашиваем ссылку на картинку и описание
        info_params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 1024, # Ширина для отправки
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
            
            # Очищаем описание от HTML
            desc = re.sub(r'<[^>]+>', '', desc)

            clean_title = title.replace("File:", "")
            return image_url, clean_title, desc

    except Exception as e:
        print(f"Ошибка получения фото: {e}")

    return None, None, None


def main():
    # Запускаем цикл на 5 итераций
    for i in range(5):
        print(f"Попытка {i+1} из 5...")
        image_url, title, desc = get_random_butterfly()
        
        if not image_url:
            print("Не удалось найти картинку. Пропускаем этот раз.")
            continue

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
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            
            if resp.ok:
                print(f"Успешно опубликовано ({i+1}/5): {title}")
            else:
                print(f"Ошибка Telegram ({i+1}/5): {resp.text}")
                
        except Exception as e:
            print(f"Сетевая ошибка при отправке: {e}")
            
        # Задержка в 4 секунды, чтобы не получить бан от Telegram за флуд
        if i < 4: # Не делаем задержку после последней картинки
            time.sleep(4)

if __name__ == "__main__":
    main()
