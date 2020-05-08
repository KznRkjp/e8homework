import requests
from bs4 import BeautifulSoup
from string import punctuation

#URL = 'https://www.freecodecamp.org/news/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe/'
#WORD = 'python'

def test_func(url, word):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    try:
        page_code = requests.get(url,headers=headers)
    except Exception as e:
        return {'total':0, 'http_status':404}
    bs_soup = BeautifulSoup(page_code.content, features="html.parser")
    symbs = ['p','a','h1','h2','h3','h4','th','td','span','li']
    total = 0
    for symb in symbs:
        total+=count(bs_soup,symb,word)
    print("result send")
    return {'total':total, 'http_status':page_code.status_code}

def clean_list(list):
    clean_list =[]
    symbols = '!@#$%^&*()_-+={[}]|\;:"<>?/.,1234567890 '
    for word in list:
        for i in range (0, len(symbols)):
            word = word.replace(symbols[i], '')
        if len(word) > 0:
            clean_list.append(word)
    return(clean_list)

def count(bs,symb,word):
    text = (''.join(s.findAll(text=True))for s in bs.findAll(symb))
    count = (x.rstrip(punctuation).lower() for y in text for x in y.split())
    count = clean_list(count)
    return (count.count(word))
