import scrapy
import re
from urllib.parse import urljoin, urlparse, urlunparse, quote

class FilmSpider(scrapy.Spider):
    name = "film_spider"
    allowed_domains = ["ru.wikipedia.org", "omdbapi.com"]
    start_urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]

    def __init__(self, *args, **kwargs):
        super(FilmSpider, self).__init__(*args, **kwargs)
        self.visited_films = set()

    def normalize_url(self, url, base_url):
        absolute = urljoin(base_url, url)
        parsed = urlparse(absolute)

        normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))
        return normalized

    def parse(self, response):
        subcat_links = set(response.css("div#mw-subcategories a::attr(href)").getall())
        for subcat in subcat_links:
            yield response.follow(subcat, self.parse)
        

        film_links = response.css("div#mw-pages div.mw-category-group a::attr(href)").getall()
        for film_link in film_links:
            normalized_url = self.normalize_url(film_link, response.url)
            if normalized_url in self.visited_films:
                continue
            self.visited_films.add(normalized_url)
            yield response.follow(film_link, self.parse_film)


        next_page = response.xpath("//div[@id='mw-pages']//a[contains(text(), 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, self.parse)

        next_subcat = response.xpath("//div[@id='mw-subcategories']//a[contains(text(), 'Следующая страница')]/@href").get()
        if next_subcat:
            yield response.follow(next_subcat, self.parse)

    def parse_film(self, response):

        title = (response.css("h1#firstHeading .mw-page-title-main::text").get() or
                 response.css("h1#firstHeading::text").get())
        if not title:
            title = response.css("table.infobox th.infobox-above::text").get()
        title = title.strip() if title else None

        infobox = response.css("table.infobox")
        if not infobox:
            self.logger.warning("Нет инфобокса на странице: %s", response.url)


        genre = infobox.xpath(
            ".//tr[th[contains(translate(., 'ЖАНР', 'жанр'), 'жанр')]]/td//text()"
        ).getall()
        genre = ' '.join(genre).strip() if genre else None


        director = infobox.xpath(
            ".//tr[th[contains(translate(., 'РЕЖИССЕР', 'режиссер'), 'режиссер') or "
            "contains(translate(., 'РЕЖИССЁР', 'режиссёр'), 'режиссёр')]]/td//text()"
        ).getall()
        director = ' '.join(director).strip() if director else None


        country = infobox.xpath(
            ".//tr[th[contains(translate(., 'СТРАНА', 'страна'), 'страна')]]/td//text()"
        ).getall()
        country = ' '.join(country).strip() if country else None


        year_data = infobox.xpath(
            ".//tr[th[contains(translate(., 'ГОД', 'год'), 'год')]]/td//text()"
        ).getall()
        if not year_data:
            year_data = infobox.xpath(
                ".//tr[th[contains(text(), 'Дата выхода')]]/td//text()"
            ).getall()
        year_str = ' '.join(year_data).strip() if year_data else None
        if year_str:
            match = re.search(r'(\d{4})', year_str)
            year_str = match.group(1) if match else year_str


        film_data = {
            'Название': title,
            'Жанр': genre,
            'Режиссер': director,
            'Страна': country,
            'Год': year_str,
        }


        api_key = "9fac7b3f"
        if title:
            title_encoded = quote(title)
            omdb_url = f"http://www.omdbapi.com/?apikey={api_key}&t={title_encoded}"
            if year_str:
                omdb_url += f"&y={year_str}"
            yield scrapy.Request(omdb_url,
                                 callback=self.parse_imdb,
                                 meta={'film_data': film_data},
                                 dont_filter=True)
        else:
            film_data['IMDB Рейтинг'] = None
            yield film_data

    def parse_imdb(self, response):
        film_data = response.meta['film_data']
        try:
            json_data = response.json()
        except Exception as e:
            self.logger.error("Ошибка при разборе JSON из OMDb API: %s", e)
            json_data = {}

        if json_data.get("Response") == "True":
            imdb_rating = json_data.get("imdbRating", "N/A")
        else:
            imdb_rating = "N/A"
        film_data["IMDB Рейтинг"] = imdb_rating
        yield film_data
