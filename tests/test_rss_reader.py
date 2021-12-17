import pytest
from rss_reader.rss_reader import *
import logging
import os.path

source = 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss'
limit = 1
article_list = [{'title': 'Роспотребнадзор выявил нарушения мер профилактики COVID-19 в театре МДМ',
                }]


def test_get_link():
    soup = get_link(source)
    r = requests.get(source)
    assert r.status_code == 200
    assert type(soup) == BeautifulSoup


def test_find_feeds3(capfd):
    source = 'https://yandex.by/'
    soup = get_link(source)
    find_feeds(soup, limit, source)

    out, err = capfd.readouterr()
    assert out == "Parsing failed. No needed tags on your page. Maybe it's not an RSS link\n"


def test_parser_arguments():
    source = 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss'
    result = parser_arguments()
    assert type(result) is dict
    assert result == {'LIMIT': 400, 'date': False, 'html': False, 'json': False, 'pdf': False, 'source': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'verbose': False}


def test_find_feeds2():
    soup = get_link(source)
    article_list = find_feeds(soup, limit, source)
    assert type(article_list) == list
    

def test_json_format():
    soup = get_link(source)
    article_list = find_feeds(soup, limit, source)
    json_string = json_format(article_list)
    assert type(json_string) == str


def test_parser(capfd):
    parser(article_list)  
    out, err = capfd.readouterr()
    assert len(out) > 0


def test_all_above1():
    result = {'source': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'verbose': False, 'version': True,
              'LIMIT': 400, 'date': False, 'pdf': False, 'html': False, 'json': False}
    all_above(result)
    assert 'Version of the rss_parser: 3.0.0'


def test_all_above2():
    result = {'source': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'verbose': False, 'version': False,
              'LIMIT': 400, 'date': False, 'pdf': True, 'html': False, 'json': False}
    all_above(result)
    assert '(the completed PDF is stored at: {outpath})'


def test_all_above3():
    result = {'source': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'verbose': False, 'version': False,
              'LIMIT': 400, 'date': False, 'pdf': False, 'html': True, 'json': False}
    all_above(result)
    assert '(the completed HTML is stored at: {outpath})'


def test_all_above4():
    result = {'source': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'verbose': False, 'version': False,
              'LIMIT': 400, 'date': False, 'pdf': True, 'html': False, 'json': True}
    all_above(result)
    assert '(the completed PDF is stored at: {outpath})'


def test_all_above5():
    result = {'source': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'verbose': False, 'version': False,
              'LIMIT': 400, 'date': False, 'pdf': False, 'html': True, 'json': True}
    all_above(result)
    assert '(the completed HTML is stored at: {outpath})'


def test_parser_arguments_version(script_runner):
    ret = script_runner.run('rss_reader', '--version')
    assert ret.success
    assert ret.stdout == 'Version of the rss_parser: 2.0.0\n'
    assert ret.stderr == ''


def test_parser_arguments_help(script_runner):
    ret = script_runner.run('rss_reader', '-h')
    assert ret.success


def test_parser_arguments_source(script_runner):
    ret = script_runner.run('rss_reader', 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss')
    assert ret.success


def test_parser_arguments_limit(script_runner):
    ret = script_runner.run('rss_reader', 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', '--limit=1')
    assert ret.success


def test_parser_arguments_verbose(script_runner):
    ret = script_runner.run('rss_reader', 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss', '--limit=1', '--verbose')
    assert ret.success

