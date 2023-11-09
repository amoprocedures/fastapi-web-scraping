from fastapi import FastAPI
from .scrapper import pages, feeds

app = FastAPI()


@app.get('/pages')
def home_pages(page: str | None = 'world'):
    data = pages(page)
    return data


@app.get('/news')
def news(page: str | None = 'world', category: str | None = 'africa'):
    data = feeds(page, category)
    return data
