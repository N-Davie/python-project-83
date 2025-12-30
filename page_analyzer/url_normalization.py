from urllib.parse import urlparse
import validators

def normalize_url(url):
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'

def validate_url(url):
    errors = []
    if not validators.url(url):
        errors.append('Некорректный URL')
    if len(url) > 255:
        errors.append('URL слишком длинный')
    return errors
