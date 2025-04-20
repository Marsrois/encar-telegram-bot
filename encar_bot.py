import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
import schedule
import json
import re

# --- НАСТРОЙКИ ---
TOKEN = "7621721259:AAE62m89bKsowjY-XG84fIhXuo5ifK-BGvk"
CHANNEL_ID = "@automarsel"
ENCAR_URL = "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.(C.CarType.Y._.(C.Manufacturer.%EB%A5%B4%EB%85%B8%EC%BD%94%EB%A6%AC%EC%95%84(%EC%82%BC%EC%84%B1_)._.(C.ModelGroup.QM6._.Model.%EB%8D%94%20%EB%89%B4%20QM6.)))_.Year.range(202009..).)%22%2C%22title%22%3A%22%EB%A5%B4%EB%85%B8%EC%BD%94%EB%A6%AC%EC%95%84(%EC%82%BC%EC%84%B1)%20%EB%8D%94%20%EB%89%B4%20QM6(19%EB%85%84~%ED%98%84%EC%9E%AC)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D"

bot = Bot(token=TOKEN)
seen_ids = set()

def get_usd_to_rub():
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    if response.ok:
        data = response.json()
        return data["Valute"]["USD"]["Value"]
    return 90.0  # fallback

def parse_encar():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(ENCAR_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all("script")
    data_script = next((s for s in scripts if 'window.__INITIAL_STATE__=' in s.text), None)
    
    if not data_script:
        print("❌ Не найден JSON с объявлениями")
        return []

    json_text = data_script.text.strip().split("window.__INITIAL_STATE__=")[-1].rsplit(";</script>", 1)[0]
    data = json.loads(json_text)

    cars = data.get("carSearch", {}).get("cars", [])
    return cars

def format_and_send(cars):
    global seen_ids
    usd_to_rub = get_usd_to_rub()
    krw_to_usd = 1370  # можно настроить

    for car in cars:
        car_id = car.get("carId")
        if car_id in seen_ids:
            continue

        seen_ids.add(car_id)

        title = car.get("model", "Без названия")
        year = f"{car.get('year')}.{str(car.get('regDate'))[:2]}"
        mileage = f"{car.get('mileage', 0):,} км".replace(",", " ")
        fuel = car.get("fuelName", "")
        engine = f"{car.get('engineSize', 0):.1f} л. {fuel} {car.get('power', 0)} л.с."
        transmission = f"{car.get('transmission', '')}, {car.get('drive', '')}"
        trim = car.get("trimName", "—")
        price_krw = car.get("price", 0)
        price_usd = price_krw / krw_to_usd
        price_rub = int(price_usd * usd_to_rub)

        image_url = car.get("imgUrl", "").replace("//", "https://")
        link = f"https://www.encar.com/dc/dc_cardetailview.do?carid={car_id}"

        message = f"""Доступен к заказу из Кореи 🇰🇷

Renault Samsung QM6

- {year} год
- пробег: {mileage}
- двигатель: {engine}
- коробка: {transmission}
- комплектация: {trim}

💲Цена в Москве ~ {price_rub:,}₽ с таможней и утилем

Бесплатная консультация по заказу авто 🇰🇷🇨🇳 - напишите МЕНЕДЖЕРУ 🧑🏼‍💼  
Сотни просчитанных предложений авто из Кореи и Китая до РФ, консультация БЕСПЛАТНО в нашем АКТИВНОМ ЧАТЕ 🚘  

#кроссовердо4млн_мрс

{link}
""".replace(",", " ")

        try:
            bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode="HTML")
            print(f"✅ Опубликовано: {title}")
        except Exception as e:
            print(f"❌ Ошибка при отправке: {e}")

def job():
    try:
        cars = parse_encar()
        format_and_send(cars)
    except Exception as e:
        print(f"❌ Ошибка в основном цикле: {e}")

# Запуск каждые 15 минут
schedule.every(15).minutes.do(job)

print("🤖 Бот запущен. Ожидаем новые объявления...")

while True:
    schedule.run_pending()
    time.sleep(5)
