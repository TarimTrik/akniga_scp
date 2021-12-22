

import requests
import lxml
from bs4 import BeautifulSoup
import json
import time








URL = 'https://akniga.org/'

HEADERS = {
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43"
}

DATA_BLOKS = {}

def get_data(URL, HEADERS):

    '''
    This func search pagination, search book-blok, create dict <book_links>
    and append all link to dict(name_book:href_link)
    func return <dict>
    '''
    
    global DATA_BLOKS
    

    resp = requests.get(url=URL, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'lxml')

    # find all_page_number
    pagination = int(soup.find('div', class_='paging').find('div', class_='page__nav').find_all('a', class_='page__nav--standart', recursive=False)[-1].text)
    count = 0
    
    for page in range(0,pagination):
        
        link_href = URL + f'index/page{page}/'
        resp = requests.get(url=link_href, headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        count_blok = 0

        data_blokss = soup.find_all('div', class_='content__main__articles--item')
        for data_blok in data_blokss:
            data_dict = {}
            

            selection_title = data_blok.find('a', class_='section__title').contents[-1] # [жанр] обрізати пробіли до і після причому всюди
            selection_title = selection_title.replace(' ','')
            selection_title = selection_title.replace('\n', '')

            content_book = data_blok.find('a', class_='content__article-main-link') # назва автора та книги, та короткий опис
            name_book_and_author = content_book.contents[1].text
            name_book_and_author = name_book_and_author.replace(' ' , '_')
            name_book_and_author = name_book_and_author.replace('\n' , '')

            description_book = content_book.contents[3].text
            description_book = description_book.replace(' ','_')
            description_book = description_book.replace('\n','')

            info_blok = data_blok.find('div', class_='oneline') # автор, хто читає, час запису, і перевіряє чи є серії книг
            svg_icon = info_blok.find_all('use')

            author = None
            performer = None
            time_read = None
            series = None
            for item in svg_icon:
                item_attr= str(item.get_attribute_list('xlink:href')[0])
                
                if item_attr == '#author':
                    author = item.parent.parent.text
                    author = author.replace('\n', '')
                elif item_attr == '#performer':
                    performer = item.parent.parent.text         
                    performer = performer.replace('\n', '')    
                elif item_attr == '#clock':
                    time_read = item.parent.parent.text               
                    time_read = time_read.replace('\n', '')          
                elif item_attr == '#series':
                    series = item.parent.parent.text
                    series = series.replace('\n', '')
                else:
                    print('error in to svg_icon' )
                
            data_dict['name_book_and_author'] = name_book_and_author
            data_dict['series_books'] = series
            data_dict['description_book'] = description_book
            data_dict['selection_title'] = selection_title
            data_dict['time_read_book'] = time_read
            data_dict['reader_book'] = performer
            count_blok = count_blok + 1

            DATA_BLOKS[f'{author}, {count_blok}, page{count}'] = data_dict
        count = count + 1
        
        print(f'Response == {resp}\n',f'{page} Number of {pagination}  // DONE //\n')

    return DATA_BLOKS


def json_data (DATA_BLOKS):
    
    with open('akniga.org/data.json', 'w', encoding='utf8') as file:
        json.dump(DATA_BLOKS, file, ensure_ascii=False, indent=4)



def main():
    get_data(URL, HEADERS)
    json_data(DATA_BLOKS)

if __name__ == '__main__':  
    main()