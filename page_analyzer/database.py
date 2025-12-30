import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def insert_url(normalized_url):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id FROM urls WHERE name = %s;',
                (normalized_url,)
            )
            existing = cur.fetchone()
            if existing:
                return existing[0]

            cur.execute(
                'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;',
                (normalized_url, datetime.now())
            )
            url_id = cur.fetchone()[0]
            conn.commit()
            return url_id

def get_urls_with_last_check():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name FROM urls ORDER BY created_at DESC;')
            urls_data = cur.fetchall()

            urls_with_last_check = []
            for url in urls_data:
                cur.execute(
                    'SELECT created_at, status_code FROM url_checks WHERE url_id = %s '
                    'ORDER BY created_at DESC LIMIT 1;',
                    (url[0],)
                )
                row = cur.fetchone()
                last_check_date = row[0] if row else None
                status_code = row[1] if row else None
                urls_with_last_check.append((url[0], url[1], last_check_date, status_code))
    return urls_with_last_check

def insert_url_check(url_id, status_code, h1, title, description):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO url_checks '
                '(url_id, status_code, h1, title, description, created_at) '
                'VALUES (%s, %s, %s, %s, %s, NOW());',
                (url_id, status_code, h1, title, description)
            )
            conn.commit()

def get_url(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, created_at FROM urls WHERE id = %s;', (id,))
            url = cur.fetchone()
            if not url:
                return None

            cur.execute(
                'SELECT id, status_code, h1, title, description, created_at '
                'FROM url_checks WHERE url_id = %s ORDER BY created_at DESC;',
                (id,)
            )
            checks = cur.fetchall()
    return url, checks
