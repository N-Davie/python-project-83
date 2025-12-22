import os

from flask import Flask
from dotenv import load_dotenv  #позволяет загружать переменные окружения (конфигурацию, ключи API, URL-адреса) 


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return 'Hello, world!'