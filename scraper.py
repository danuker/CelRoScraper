# Instructions: see bottom

import re
import urllib
from time import sleep
import sys

def get_urls(template, regex, num_pages=30):
    """
    :return: List of URLs of individual laptop page
    """

    files = [template.format(i) for i in range(1, num_pages+1)]
    urls = set()

    for f in files:
        sys.stderr.write(f + '\n')
        sys.stderr.flush()
        sleep(1)
        fi = urllib.urlopen(f).readlines()
        for line in fi:
            # Write-only regex follows
            links = re.findall(regex, line)
            if links:
                urls.update(links)
    for url in urls:
        print url
        sys.stdout.flush()
    return urls

def fetch_page(url):
    return urllib.urlopen(url).read()

def fetch_passmark_from_page(link):
    if link.strip() is '':
        return '-'
    try:
        page = fetch_page(link)
        rateline = page[page.find('<span style="font-family: Arial, Helvetica, sans-serif;font-size: 35px;	font-weight: bold; color: red;">'):].split('>')[1]
        rating = rateline.split('<')[0]

        if rating.strip() != '':
            return rating
        else:
            return '-'
    except IndexError:
        return '-'


def fetch_passmark(item):
    if item is '':
        return '-'

    item = item.strip()

    bench_scores = {}

    # List of "known_item\tscore"
    with open('passmark.txt') as f:
        for line in f:
            read_item, score = line.strip().split('\t')
            bench_scores[read_item] = score

    if item in bench_scores:
        return bench_scores[item]
    else:
        passmark_search_url = 'https://www.passmark.com/search/zoomsearch.php?zoom_sort=0&zoom_xml=0&zoom_query={}+performance&zoom_per_page=10&zoom_and=1&zoom_cat[]=5'
        passmark_search_url = passmark_search_url.format(item.replace(' ', '+'))
        page = fetch_page(passmark_search_url)
        results = page[page.find('class="result_title'):]
        first = results[results.find('http'):]
        link = first.split('"')[0]
        bench_scores[item] = fetch_passmark_from_page(link)

    with open('passmark.txt', 'w') as f:
        for i in bench_scores:
            f.write('{}\t{}\n'.format(i, bench_scores[i]))

    return bench_scores[item]


def content_after_text_td(page, text):
    try:
        if text == 'Pret':
            # text = page[page.find('"price"'):].split('>')[1].split('<')[0]
            text = page[page.find('itemprop="price"'):].split('>')[1].split('<')[0]
        else:
            next_td = page[page.find(text):].split('>')[2].split('<')[0]
            text = next_td\
                .lower()\
                .replace('&reg;', '')\
                .replace('&trade;', '')\
                .replace('tm', '')\
                .replace('tb', '000gb')\
                .replace('gb', '')\
                .replace('processor', '')\
                .replace('procesor', '')\
                .replace('graphics', '')\
                .replace('graphics', '')\
                .replace('amd ', '')\
                .replace('ati ', '')\
                .replace('nvidia ', '')\
                .replace('-', ' ')\
                .replace('integrated ', '')\
                .replace('quad core ', '')\
                .replace('dual core ', '')\
                .replace('geforce ', '')\
                .replace('radeon ', '')\
                .replace('dual ', '')\

    except IndexError:
        text = ''

    return text

def laptop_specs(page, cols):
    finder = lambda text: content_after_text_td(page, text)
    return map(finder, cols[1:])

def scrape_contents_from_urls(filename, cols):
    with open(filename) as urls:
        print '\t'.join(cols)

        for url in urls:
            url = url.strip()
            page = fetch_page(url)
            specs = laptop_specs(page, cols)

            if filename == 'laptops.txt':
                # Laptop version
                specs[cols.index('CPUMark') - 1] = fetch_passmark(specs[cols.index('Model Procesor:') - 1])
                sleep(1)
                specs[cols.index('GPUMark') - 1] = fetch_passmark(specs[cols.index('Chipset video:') - 1])
                print url + '\t' + '\t'.join(specs)

            else:
                # Desktop version
                specs[cols.index('CPUMark') - 1] = fetch_passmark(specs[cols.index('Tip procesor:') - 1])
                sleep(1)
                v1 = specs[cols.index('Chipset video:') - 1]
                v2 = specs[cols.index('Video:') - 1]
                video_field = v1 if len(v1) > len(v2) else v2
                specs[cols.index('GPUMark') - 1] = fetch_passmark(video_field)
                print url + '\t' + '\t'.join(specs)
            sleep(1)

            sys.stdout.flush()

cols = {
    'laptop': [
        'URL',
        'Pret',
        'Model Procesor:',
        'Chipset video:',
        'CPUMark',
        'GPUMark',
        'Capacitate HDD:',
        'Tip unitate stocare:',
        'Memorie standard:',
        'Diagonala LCD',
        'Rezolutie optima:',
        'Greutate (Kg):',
        'Sistem de operare:',
    ],
    'desktop': [
        'URL',
        'Pret',
        'Tip procesor:',
        'Chipset video:',
        'Video:',
        'CPUMark',
        'GPUMark',
        'Capacitate HDD:',
        'Numar HDD:',
        'Memorie:',
        'Greutate (Kg):',
        'Sistem de operare:',
    ]
}

if __name__ == '__main__':
    """
    Instructions:

    1. Run the script with the "get_urls" part, and save the output in either
        "laptops.txt"
        or
        "desktops.txt"

        python scraper.py > laptops.txt

    2. Comment out the "get_urls" part, and run the scrape_contents_from_urls part
        The script will output a TSV file, which may be opened in Excel or so.

        python scraper.py > laptops_2016_05_15.tsv

    Sadly, detecting the exact amount of SSD capacity isn't good especially for laptops.
    """


    # Laptops

    get_urls(
        'http://www.cel.ro/laptop-laptopuri/2a_{}',
        'http://www\.cel\.ro/laptop\-laptopuri/laptop-(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    # scrape_contents_from_urls('laptops.txt', cols['laptop'])

    # Desktops

    # get_urls(
    #     'http://www.cel.ro/Calculatoare-Desktop/2a_{}',
    #     'http://www\.cel\.ro/calculatoare-desktop/[^0-9"](?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    #     num_pages=17
    # )
    # scrape_contents_from_urls('desktops.txt', cols['desktop'])


