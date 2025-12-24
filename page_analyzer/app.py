import os
from urllib.parse import urlparse
from datetime import datetime

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

# Загружаем переменные окружения из .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_create():
    url = request.form.get('url', '').strip()
    errors = []

    # Валидация URL
    if not validators.url(url):
        errors.append('Некорректный URL')
    if len(url) > 255:
        errors.append('URL слишком длинный')

    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('index.html', url=url), 422

    # Нормализация URL
    parsed_url = urlparse(url)
    normalized_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

    # Работа с БД
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем, есть ли уже такой URL
            cur.execute(
                'SELECT id FROM urls WHERE name = %s;',
                (normalized_url,)
            )
            existing = cur.fetchone()

            if existing:
                flash('Страница уже существует', 'info')
                return redirect(url_for('show_url', id=existing[0]))

            # Вставка нового URL
            cur.execute(
                'INSERT INTO urls (name, created_at) '
                'VALUES (%s, %s) '
                'RETURNING id;',
                (normalized_url, datetime.now())
            )
            url_id = cur.fetchone()[0]
            conn.commit()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))


@app.get('/urls/<int:id>')
def show_url(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Получаем информацию о сайте
            cur.execute(
                'SELECT id, name, created_at FROM urls WHERE id = %s;',
                (id,)
            )
            url = cur.fetchone()

            if not url:
                return 'Not found', 404

            # Получаем список проверок для этого URL
            cur.execute(
                'SELECT * FROM url_checks WHERE url_id = %s '
                'ORDER BY created_at DESC;',
                (id,)
            )
            checks = cur.fetchall()

    # Передаём и url, и проверки в шаблон
    return render_template('url.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def url_checks_create(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO url_checks (url_id, created_at) '
                'VALUES (%s, NOW()) RETURNING id;',
                (id,)
            )
            conn.commit()

    flash('Проверка успешно добавлена', 'success')
    return redirect(url_for('show_url', id=id))


@app.get('/urls')
def urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Получаем список сайтов
            cur.execute(
                'SELECT id, name '
                'FROM urls '
                'ORDER BY created_at DESC;'
            )
            urls_data = cur.fetchall()

            urls_with_last_check = []

            # 2. Для каждого сайта берём последнюю проверку
            for url in urls_data:
                cur.execute(
                    'SELECT created_at, status_code '
                    'FROM url_checks '
                    'WHERE url_id = %s '
                    'ORDER BY created_at DESC '
                    'LIMIT 1;',
                    (url[0],)
                )
                row = cur.fetchone()

                last_check_date = row[0] if row else None
                status_code = row[1] if row else None

                urls_with_last_check.append(
                    (url[0], url[1], last_check_date, status_code)
                )

    return render_template('urls.html', urls=urls_with_last_check)


if __name__ == '__main__':
    app.run(debug=True)
