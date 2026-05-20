import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')


@app.get('/health/')
def health():
    return jsonify({'status': 'ok'})


@app.post('/send/')
def send_message():
    data = request.get_json(silent=True) or {}
    text = str(data.get('text', '')).strip()

    if not text:
        return jsonify({'success': False, 'message': 'Текст сообщения пустой.'}), 400

    # В учебном запуске токен можно не задавать: сервис всё равно покажет, что JSON получен.
    if not TOKEN or not CHAT_ID:
        return jsonify({'success': True, 'message': 'Сообщение принято, Telegram не настроен.'})

    response = requests.post(
        f'https://api.telegram.org/bot{TOKEN}/sendMessage',
        data={'chat_id': CHAT_ID, 'text': text},
        timeout=5,
    )

    if response.ok:
        return jsonify({'success': True, 'message': 'Сообщение отправлено.'})

    return jsonify({'success': False, 'message': 'Ошибка отправки в Telegram.'}), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
