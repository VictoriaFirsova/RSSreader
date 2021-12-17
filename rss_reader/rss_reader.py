import sys
from argparse import ArgumentParser
from sys import exit
from sqlite3 import OperationalError
from pathlib import Path
from yattag import Doc
import requests
from bs4 import BeautifulSoup, FeatureNotFound
from json import dumps, loads
import logging
from dateutil.parser import parse, ParserError
import pandas as pd
from re import sub, split
from requests.exceptions import MissingSchema
import sqlite3
from fpdf import FPDF



def parser_arguments():
    """Getting values from the command line"""

    parser = ArgumentParser(usage='rss_reader.py source [-h] [--version] [--json] '
                            '[--verbose] [--limit LIMIT] [--date] [--html] [--pdf]',
                            description='Pure Python command-line RSS reader.')
    parser.add_argument('source', nargs='?', help='Input just one your RSS-link hear. Your link have to start with "https://"')
    parser.add_argument('-v', '--verbose', action="store_true", help='Outputs verbose status messages')
    parser.add_argument('--limit', dest='LIMIT', type=int, default=400,
                        help='Limit news topics if this parameter provided')
    parser.add_argument('--date', type=int, default=False,
                        help='Input just one date in yyyymmdd format to output news from storage.'
                             ' For example: --date 20191020')
    parser.add_argument("--pdf", action="store_true", help="Conversion to pdf")
    parser.add_argument("--html", action="store_true", help="Conversion to html")
    parser.add_argument('--json', action="store_true", help='Print result as JSON in stdout')
    parser.add_argument('--version', action='version', version='Version of the rss_parser: 4.0.0')

    args = parser.parse_args()
    result = vars(args)
    return result


def get_link(source):
    """Parsing to xml"""
    try:
        logging.info('Check the request status')
        r = requests.get(source)
        logging.info("Request status: %d ", r.status_code)
        logging.info("Forming an xml")
        soup = BeautifulSoup(r.content, features='xml')
        logging.info("xml was formed successfully")
        return soup
    except FeatureNotFound as f:
        print('Parsing to xml has been failed.')
        logging.error(f"Parsing to xml has been failed. See exception: {f} ", exc_info=False)
        exit('Connection error')
    except MissingSchema:
        print('Invalid URL or no URL at all')
        exit()
    except ConnectionError as b:
        logging.error(f"Connection error. See exception: {b} ", exc_info=True)
        exit()


def find_feeds(soup, limit, source):
    """Parsing data from xml by tags and output of the result"""
    article_list = []

    try:
        logging.info("Forming a list of articles")
        articles = soup.findAll('item', limit=limit)
        logging.info("Sorting tags and appending an article to a list one by one")

        for a in articles:
            title = a.find('title').text
            link = a.find('link').text
            short_source = split(r'/', source)
            short_source = str(short_source[0]+'//' + short_source[2])
            if a.find('description'):
                description = a.find('description').text
                description = sub('<[A-Za-z\/][^>]*>', '', description)
            else:
                description = 'Empty'
            if a.find('pubDate'):
                published = a.find('pubDate').text
                published = parse(published)
                published = published.date()
                published = str(published.strftime('%Y-%m-%d'))

            else:
                published = 'Empty'
            if a.find('category'):
                category = a.find('category').text
            else:
                category = 'Empty'

            article = dict(title=title, link=link, short_source=short_source, published=published,
                           description=description, category=category)

            article_list.append(article)

        logging.info("Checking that everything went well")
        if len(article_list) < 1:
            raise ValueError("Parsing failed. No needed tags on your page. Maybe it's not an RSS link")
    except ValueError as e:
        print(e)
        logging.error(f"Parsing failed. No needed tags on your page. Maybe it's not an RSS link: {e} ", exc_info=True)

    return article_list


def parser(article_list):
    """Pure Python command-line RSS reader.

                positional arguments:\n
                source         RSS URL"""

    count = 1
    logging.info("Output articles to the console")
    for article in article_list[:]:
        print(f'{count}.')
        for k, v in article.items():
            print(f'{k}: {v} \n')
        count += 1


def to_db(json_string):
    """Saving articles to DB"""
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()
    logging.info("Creating DB")
    # Creating the table
    cursor.execute("""CREATE TABLE IF NOT EXISTS article_list
                      (title text, link text primary key, short_source text, 
                       published text, description text, category text)
                   """)
    logging.info("Adding articles in DB")
    # Adding articles to BD
    for article in loads(json_string):

        df = pd.DataFrame.from_dict([article])
        df.to_sql(name='temporary_table', con=conn, if_exists='append', index=False)
        insert_sql = 'INSERT OR IGNORE INTO article_list SELECT * FROM temporary_table'
        conn.execute(insert_sql)
        drop_temporary_table = 'DROP TABLE temporary_table'
        conn.execute(drop_temporary_table)
    cursor.close()


def json_format(article_list):
    """Convert to JSON"""
    logging.info("Output will be in JSON format")
    json_string = dumps(article_list[:], ensure_ascii=False, indent=4)

    return json_string


def verbose():
    """Turn on verbose"""
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("Parsing has been started with verbose status messages")


def cashed_news(date, limit, source, json):
    """Searching news in DB"""

    try:
        conn = sqlite3.connect("articles.db")
        cursor = conn.cursor()
        logging.info("Connecting to DB")
        date = str(date)
        date = parse(date)
        date = str(date.strftime('%Y-%m-%d'))

        if source is not None:
            logging.info("Searching for articles from your source and date")
            short_source = split(r'/', source)
            short_source = str(short_source[0] + '//' + short_source[2])
            sqlite_select_query = "SELECT * FROM article_list WHERE published LIKE (?) AND short_source LIKE (?)"
            cursor.execute(sqlite_select_query, (date, short_source,))
        else:
            logging.info("Searching for articles from your date")
            sqlite_select_query = "SELECT * FROM article_list WHERE published LIKE (?)"
            cursor.execute(sqlite_select_query, (date,))
        records = cursor.fetchall()
        if len(records) > 1:
            article_list = []
            logging.info("Printing articles to stdout")
            for row in records[:limit]:
                article = {'title': row[0],
                           'link': row[1],
                           'short_source': row[2],
                           'published': row[3],
                           'description': row[4],
                           'category': row[5]
                           }
                article_list.append(article)

            if json:
                json_string = json_format(article_list)
                print(json_string)
            else:
                count = 1
                for article in article_list[:]:
                    print(f'{count}.')
                    for k, v in article.items():
                        print(f'{k}: {v} \n')
                    count += 1

        else:
            raise ValueError('There is no news according to your criteria', )

        cursor.close()
    except ParserError:
        logging.error(f"Not correct date format. Please, use 20191020(%Y%m%d)", exc_info=False)
    except ValueError as v:
        logging.error(f"{v}", exc_info=False)
        sys.exit()
    except OperationalError:
        logging.error(f"No any cashed news yet, sorry", exc_info=False)
    return article_list


def to_html(article_list):
    """Convert to HTML"""
    logging.info("Forming HTML")
    with open('article_list.html', "w") as file:
        doc, tag, text, line = Doc().ttl()
        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('body'):
                line('h3', 'List of your articles')
                with tag('ol', type="1"):
                    for article in article_list[:]:
                        with tag('li'):
                            for k, v in article.items():
                                if k == 'link' or k == 'short_source':
                                    text(k+':'+'   ')
                                    with tag('a', href=v):
                                        text(v)
                                        doc._append("<br/>")
                                else:
                                    text(k+':'+'   ')
                                    text(v)
                                    doc._append("<br/>")

            result = doc.getvalue()
        file.write(result)
        logging.info("HTML is ready")
        outpath = Path.cwd() / 'article_list.html'

    return outpath


def to_pdf(article_list):
    """Convert to PDF"""
    logging.info("Forming PDF")
    pdf = FPDF()
    pdf.add_page()
    my_file = Path('DejaVuSansCondensed.ttf')
    if not my_file.is_file():
        url = 'https://raw.githubusercontent.com/web-fonts/dejavu-sans-condensed/master/fonts/dejavu-sans-condensed-webfont.ttf'
        myfile = requests.get(url)
        with open('DejaVuSansCondensed.ttf', 'wb') as f:
            f.write(myfile.content)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('Dejavu', style='', size=11)
    count = 1
    logging.info("Output articles to the article_list.pdf")
    pdf.cell(180, 10, f'List of your articles', align='C', ln=1)
    for article in article_list[:]:
        pdf.set_font('Dejavu', style='', size=9)
        pdf.multi_cell(180, 10, f' {count}.')
        for k, v in article.items():
            if k == 'link':
                pdf.set_font('Dejavu', style='', size=9)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(10, 10, f'{k}:')
                pdf.set_font('Dejavu', style='U', size=9)
                pdf.set_text_color(93, 118, 203)
                pdf.cell(10, 10, f'{v}', link=f"{v}", ln=1)
            elif k == 'short_source':
                pass
            else:
                pdf.set_font('Dejavu', style='', size=9)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(180, 10, f'{k}: {v}')
        count += 1

    pdf.output('article_list.pdf', 'F')
    logging.info("PDF is ready")
    outpath = Path.cwd() / 'article_list.pdf'
    return outpath


def all_above(result):
    """func to to call all other functions in the right order"""

    if result['verbose']:
        verbose()
    limit = result['LIMIT']
    source = result['source']
    json = result['json']
    if result['date'] and result['html'] and result['pdf']:
        date = result['date']
        article_list = cashed_news(date, limit, source, json)
        outpath = to_html(article_list)
        print(f'(the completed HTML is stored at: {outpath})')
        outpath = to_pdf(article_list)
        print(f'(the completed PDF is stored at: {outpath})')
    elif result['date'] and result['html']:
        date = result['date']
        article_list = cashed_news(date, limit, source, json)
        outpath = to_html(article_list)
        print(f'(the completed HTML is stored at: {outpath})')
    elif result['date'] and result['pdf']:
        date = result['date']
        article_list = cashed_news(date, limit, source, json)
        outpath = to_pdf(article_list)
        print(f'(the completed PDF is stored at: {outpath})')
    elif result['date']:
        date = result['date']
        cashed_news(date, limit, source, json)
    else:
        soup = get_link(source)
        article_list = find_feeds(soup, limit, source)
        json_string = json_format(article_list)
        to_db(json_string)

        if result['json'] and result['html']:
            print(json_string)
            outpath = to_html(article_list)
            print(f'(the completed HTML is stored at: {outpath})')
        elif result['json'] and result['pdf']:
            print(json_string)
            outpath = to_pdf(article_list)
            print(f'(the completed PDF is stored at: {outpath})')
        elif result['json']:
            print(json_string)
        else:
            if result['html'] and result['pdf']:
                outpath = to_html(article_list)
                print(f'(the completed HTML is stored at: {outpath})')
                outpath = to_pdf(article_list)
                print(f'(the completed PDF is stored at: {outpath})')
            elif result['pdf']:
                outpath = to_pdf(article_list)
                print(f'(the completed PDF is stored at: {outpath})')
            elif result['html']:
                outpath = to_html(article_list)
                print(f'(the completed HTML is stored at: {outpath})')
            else:
                parser(article_list)


def entry():
    """entry point"""
    result = parser_arguments()
    all_above(result)


if __name__ == '__main__':
    entry()
