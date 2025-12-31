from bs4 import BeautifulSoup


def parse_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    h1 = soup.h1.text.strip() if soup.h1 else None
    title = soup.title.text.strip() if soup.title else None

    description = None
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description and meta_description.get('content'):
        description = meta_description['content'].strip()

    return h1, title, description
