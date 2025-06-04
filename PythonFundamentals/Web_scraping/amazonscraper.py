import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.00"
chrome_options.add_argument(f"--user-agent={my_user_agent}")

driver = webdriver.Chrome(options=chrome_options)

try:
    for i in range (1,10):
        url = 'https://www.amazon.in/s?k=laptop+under+35000&page=2&xpid=8HIkV5eDE2GAB&crid=203J9G073XKKR&qid=1747914457&sprefix=lapt%2Caps%2C513&ref=sr_pg_'+str(i)
        driver.get(url)

        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        cards = soup.find_all('div', class_ = 'sg-col-inner')
        for card in cards:
            text = card.find_all('h2')
            for t1 in text:
                t = t1.find('span')
                if t is not None:
                    print("Product name is : " + t.getText())
finally:
    driver.quit()
