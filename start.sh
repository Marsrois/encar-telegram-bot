#!/bin/bash
# Указываем, на каком порту будет работать приложение
export PORT=8000
python3 encar_bot.py
chmod +x start.sh
git add start.sh
git commit -m "Make start.sh executable"
git push
