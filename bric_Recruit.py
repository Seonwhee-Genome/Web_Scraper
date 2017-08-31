from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import pickle
TODAYis = '20170831'
save_path = 'E:/BioJobs/%s_bric_recruit.pkl' % TODAYis

def Paging():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-pop')
    driver = webdriver.Chrome(executable_path="C:/Users/qwerty/chromedriver.exe", chrome_options=chrome_options)
    driver.implicitly_wait(3)
    driver.get('http://www.ibric.org/myboard/list.php?Board=job_recruit&Page=1&selflevel=-1')
    pages = ['02', '03', '04', '05', '06', '07']

    DF_list = []
    (driver, soup, DF) = html_scrapping(driver)
    DF_list.append(DF)

    #pages_tag = soup.find('table', attrs={'border': '0', 'cellspacing': '0', 'cellpadding': '0', 'width': '100%', 'class': 'tab','bgcolor': 'f7f7f7'})
    #pages = pages_tag.find_all('a')
    for page in pages:
        driver.find_element_by_link_text(page).click()
        (driver, soup, DF) = html_scrapping(driver)
        DF_list.append(DF)

    Final_DF = pd.concat(DF_list)
    Final_DF.to_pickle(save_path)
    driver.implicitly_wait(3)


def html_scrapping(driver):

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    table = soup.find('table', attrs={'style': 'BORDER-COLLAPSE: collapse', 'border': '0', 'cellspacing': '0', 'cellpadding': '0', 'width': '672', 'align': 'center'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        if len(cols) == 5:
            # data.append([ele for ele in cols])
            data.append([ele for ele in cols if ele])  # Get rid of empty values

    data_header = data[0]
    data = data[1:]
    DF = pd.DataFrame(data=data, columns=data_header)
    print(DF)

    driver.implicitly_wait(3)
    return (driver, soup, DF)


def processing_Data():
    savefile = open(save_path, 'rb')
    DF = pickle.load(savefile)
    DF.to_csv('E:/BioJobs/%s_bric_recruit.csv' % TODAYis, ',')



if __name__== "__main__":
    Paging()
    processing_Data()
