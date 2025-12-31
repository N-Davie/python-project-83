from flask import Flask, flash, redirect, render_template, request, url_for
import requests

from page_analyzer.config import Config
from page_analyzer.database import (
    insert_url, get_urls_with_last_check, insert_url_check, get_url
)
from page_analyzer.parser import parse_html
from page_analyzer.url_normalization import normalize_url, validate_url


app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_create():
    url = request.form.get('url', '').strip()
    errors = validate_url(url)

    if errors:
        for e in errors:
            flash(e, 'danger')
        return render_template('index.html', url=url), 422

    normalized_url = normalize_url(url)

    url_id, created = insert_url(normalized_url)

    if not created:
        flash('Страница уже существует', 'info')
    else:
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=url_id))


@app.post('/urls/<int:id>/checks')
def url_checks_create(id):
    result = get_url(id)
    if result is None:
        flash('Сайт не найден', 'danger')
        return redirect(url_for('urls'))

    url, _ = result
    site_url = url[1]

    try:
        response = requests.get(site_url, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))

    status_code = response.status_code
    h1, title, description = parse_html(response.text)

    insert_url_check(id, status_code, h1, title, description)
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))


@app.get('/urls')
def urls():
    urls_with_last_check = get_urls_with_last_check()
    return render_template('urls.html', urls=urls_with_last_check)


@app.get('/urls/<int:id>')
def show_url(id):
    result = get_url(id)
    if result is None:
        return 'Not found', 404

    url, checks = result
    return render_template('url.html', url=url, checks=checks)


if __name__ == '__main__':
    app.run(debug=True)
