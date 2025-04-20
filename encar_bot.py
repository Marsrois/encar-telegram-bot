{\rtf1\ansi\ansicpg1251\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import requests\
from bs4 import BeautifulSoup\
from telegram import Bot\
import time\
import schedule\
import json\
import re\
\
# --- \uc0\u1053 \u1040 \u1057 \u1058 \u1056 \u1054 \u1049 \u1050 \u1048  ---\
TOKEN = "7621721259:AAE62m89bKsowjY-XG84fIhXuo5ifK-BGvk"\
CHANNEL_ID = "@automarsel"\
ENCAR_URL = "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.(C.CarType.Y._.(C.Manufacturer.%EB%A5%B4%EB%85%B8%EC%BD%94%EB%A6%AC%EC%95%84(%EC%82%BC%EC%84%B1_)._.(C.ModelGroup.QM6._.Model.%EB%8D%94%20%EB%89%B4%20QM6.)))_.Year.range(202009..).)%22%2C%22title%22%3A%22%EB%A5%B4%EB%85%B8%EC%BD%94%EB%A6%AC%EC%95%84(%EC%82%BC%EC%84%B1)%20%EB%8D%94%20%EB%89%B4%20QM6(19%EB%85%84~%ED%98%84%EC%9E%AC)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D"\
\
bot = Bot(token=TOKEN)\
seen_ids = set()\
\
def get_usd_to_rub():\
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")\
    if response.ok:\
        data = response.json()\
        return data["Valute"]["USD"]["Value"]\
    return 90.0  # fallback\
\
def parse_encar():\
    headers = \{'User-Agent': 'Mozilla/5.0'\}\
    response = requests.get(ENCAR_URL, headers=headers)\
    soup = BeautifulSoup(response.text, 'html.parser')\
\
    scripts = soup.find_all("script")\
    data_script = next((s for s in scripts if 'window.__INITIAL_STATE__=' in s.text), None)\
    \
    if not data_script:\
        print("\uc0\u10060  \u1053 \u1077  \u1085 \u1072 \u1081 \u1076 \u1077 \u1085  JSON \u1089  \u1086 \u1073 \u1098 \u1103 \u1074 \u1083 \u1077 \u1085 \u1080 \u1103 \u1084 \u1080 ")\
        return []\
\
    json_text = data_script.text.strip().split("window.__INITIAL_STATE__=")[-1].rsplit(";</script>", 1)[0]\
    data = json.loads(json_text)\
\
    cars = data.get("carSearch", \{\}).get("cars", [])\
    return cars\
\
def format_and_send(cars):\
    global seen_ids\
    usd_to_rub = get_usd_to_rub()\
    krw_to_usd = 1370  # \uc0\u1084 \u1086 \u1078 \u1085 \u1086  \u1085 \u1072 \u1089 \u1090 \u1088 \u1086 \u1080 \u1090 \u1100 \
\
    for car in cars:\
        car_id = car.get("carId")\
        if car_id in seen_ids:\
            continue\
\
        seen_ids.add(car_id)\
\
        title = car.get("model", "\uc0\u1041 \u1077 \u1079  \u1085 \u1072 \u1079 \u1074 \u1072 \u1085 \u1080 \u1103 ")\
        year = f"\{car.get('year')\}.\{str(car.get('regDate'))[:2]\}"\
        mileage = f"\{car.get('mileage', 0):,\} \uc0\u1082 \u1084 ".replace(",", " ")\
        fuel = car.get("fuelName", "")\
        engine = f"\{car.get('engineSize', 0):.1f\} \uc0\u1083 . \{fuel\} \{car.get('power', 0)\} \u1083 .\u1089 ."\
        transmission = f"\{car.get('transmission', '')\}, \{car.get('drive', '')\}"\
        trim = car.get("trimName", "\'97")\
        price_krw = car.get("price", 0)\
        price_usd = price_krw / krw_to_usd\
        price_rub = int(price_usd * usd_to_rub)\
\
        image_url = car.get("imgUrl", "").replace("//", "https://")\
        link = f"https://www.encar.com/dc/dc_cardetailview.do?carid=\{car_id\}"\
\
        message = f"""\uc0\u1044 \u1086 \u1089 \u1090 \u1091 \u1087 \u1077 \u1085  \u1082  \u1079 \u1072 \u1082 \u1072 \u1079 \u1091  \u1080 \u1079  \u1050 \u1086 \u1088 \u1077 \u1080  \u55356 \u56816 \u55356 \u56823 \
\
Renault Samsung QM6\
\
- \{year\} \uc0\u1075 \u1086 \u1076 \
- \uc0\u1087 \u1088 \u1086 \u1073 \u1077 \u1075 : \{mileage\}\
- \uc0\u1076 \u1074 \u1080 \u1075 \u1072 \u1090 \u1077 \u1083 \u1100 : \{engine\}\
- \uc0\u1082 \u1086 \u1088 \u1086 \u1073 \u1082 \u1072 : \{transmission\}\
- \uc0\u1082 \u1086 \u1084 \u1087 \u1083 \u1077 \u1082 \u1090 \u1072 \u1094 \u1080 \u1103 : \{trim\}\
\
\uc0\u55357 \u56498 \u1062 \u1077 \u1085 \u1072  \u1074  \u1052 \u1086 \u1089 \u1082 \u1074 \u1077  ~ \{price_rub:,\}\u8381  \u1089  \u1090 \u1072 \u1084 \u1086 \u1078 \u1085 \u1077 \u1081  \u1080  \u1091 \u1090 \u1080 \u1083 \u1077 \u1084 \
\
\uc0\u1041 \u1077 \u1089 \u1087 \u1083 \u1072 \u1090 \u1085 \u1072 \u1103  \u1082 \u1086 \u1085 \u1089 \u1091 \u1083 \u1100 \u1090 \u1072 \u1094 \u1080 \u1103  \u1087 \u1086  \u1079 \u1072 \u1082 \u1072 \u1079 \u1091  \u1072 \u1074 \u1090 \u1086  \u55356 \u56816 \u55356 \u56823 \u55356 \u56808 \u55356 \u56819  - \u1085 \u1072 \u1087 \u1080 \u1096 \u1080 \u1090 \u1077  \u1052 \u1045 \u1053 \u1045 \u1044 \u1046 \u1045 \u1056 \u1059  \u55358 \u56785 \u55356 \u57340 \u8205 \u55357 \u56508   \
\uc0\u1057 \u1086 \u1090 \u1085 \u1080  \u1087 \u1088 \u1086 \u1089 \u1095 \u1080 \u1090 \u1072 \u1085 \u1085 \u1099 \u1093  \u1087 \u1088 \u1077 \u1076 \u1083 \u1086 \u1078 \u1077 \u1085 \u1080 \u1081  \u1072 \u1074 \u1090 \u1086  \u1080 \u1079  \u1050 \u1086 \u1088 \u1077 \u1080  \u1080  \u1050 \u1080 \u1090 \u1072 \u1103  \u1076 \u1086  \u1056 \u1060 , \u1082 \u1086 \u1085 \u1089 \u1091 \u1083 \u1100 \u1090 \u1072 \u1094 \u1080 \u1103  \u1041 \u1045 \u1057 \u1055 \u1051 \u1040 \u1058 \u1053 \u1054  \u1074  \u1085 \u1072 \u1096 \u1077 \u1084  \u1040 \u1050 \u1058 \u1048 \u1042 \u1053 \u1054 \u1052  \u1063 \u1040 \u1058 \u1045  \u55357 \u56984   \
\
#\uc0\u1082 \u1088 \u1086 \u1089 \u1089 \u1086 \u1074 \u1077 \u1088 \u1076 \u1086 4\u1084 \u1083 \u1085 _\u1084 \u1088 \u1089 \
\
\{link\}\
""".replace(",", " ")\
\
        try:\
            bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode="HTML")\
            print(f"\uc0\u9989  \u1054 \u1087 \u1091 \u1073 \u1083 \u1080 \u1082 \u1086 \u1074 \u1072 \u1085 \u1086 : \{title\}")\
        except Exception as e:\
            print(f"\uc0\u10060  \u1054 \u1096 \u1080 \u1073 \u1082 \u1072  \u1087 \u1088 \u1080  \u1086 \u1090 \u1087 \u1088 \u1072 \u1074 \u1082 \u1077 : \{e\}")\
\
def job():\
    try:\
        cars = parse_encar()\
        format_and_send(cars)\
    except Exception as e:\
        print(f"\uc0\u10060  \u1054 \u1096 \u1080 \u1073 \u1082 \u1072  \u1074  \u1086 \u1089 \u1085 \u1086 \u1074 \u1085 \u1086 \u1084  \u1094 \u1080 \u1082 \u1083 \u1077 : \{e\}")\
\
# \uc0\u1047 \u1072 \u1087 \u1091 \u1089 \u1082  \u1082 \u1072 \u1078 \u1076 \u1099 \u1077  15 \u1084 \u1080 \u1085 \u1091 \u1090 \
schedule.every(15).minutes.do(job)\
\
print("\uc0\u55358 \u56598  \u1041 \u1086 \u1090  \u1079 \u1072 \u1087 \u1091 \u1097 \u1077 \u1085 . \u1054 \u1078 \u1080 \u1076 \u1072 \u1077 \u1084  \u1085 \u1086 \u1074 \u1099 \u1077  \u1086 \u1073 \u1098 \u1103 \u1074 \u1083 \u1077 \u1085 \u1080 \u1103 ...")\
\
while True:\
    schedule.run_pending()\
    time.sleep(5)\
}