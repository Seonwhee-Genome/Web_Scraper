from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import date
from calendar import monthrange
import pandas as pd
import pickle

TODAYis = "20170906"
def start_Chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-pop')
    driver = webdriver.Chrome(executable_path="C:/Users/qwerty/chromedriver.exe", chrome_options=chrome_options)
    return driver

class Domestic_Conferences(object):
    def STEP1(self):
        driver = start_Chrome()

        driver.maximize_window()
        driver.implicitly_wait(3)
        driver.get('http://www.ibric.org/bioschedule/list.php?bty=evt#half')

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        cmd = driver.find_element_by_xpath('//*[@id="Bsctd4"]')
        cmd.click()
        notices = soup.find("div", {"id": "contents_list_"})
        titles = notices.find_all("a", class_="abase")
        conference_name = []
        conference_link = []

        for tt in titles:
            link = tt['href']
            conference_link.append("http://www.ibric.org" + link)

            bname = tt.find_all('b')
            for name in bname:
                strname = name.text.strip()
                conference_name.append(strname)

        driver.close()
        return conference_link

    def STEP2(self, Links):
        driver = start_Chrome()
        driver.maximize_window()
        driver.implicitly_wait(3)

        columns = []
        for link in Links:
            dataList = []
            driver.get(link)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            data_header = ["Conference_Name", "Date", "Venue", "Organization", "URL", "Type", "Qualification", "Fee",
                           "Category"]
            table = soup.find('table', attrs={'width': '672'})

            table_body = table.find('tbody')
            urls = table_body.find_all('td', attrs={'style': 'word-break:break-all'})
            info = table_body.find_all('td', attrs={'style': 'word-break:break-all;font-size:14px;'})
            dates = table_body.find_all('td', attrs={'style': 'word-break:break-all;font-size:16px;font-weight:bold'})
            conf_name = table_body.find_all('td', attrs={'style': 'font-size:20px;padding:30px 0px'})
            inDetail = table_body.find_all('td', attrs={'style': 'word-break:break-all;font-size:14px'})

            self.text_scraping(conf_name, dataList)
            self.text_scraping(dates, dataList)
            self.text_scraping(info, dataList)
            self.text_scraping(urls, dataList)
            self.text_scraping(inDetail, dataList)
            columns.append(dataList)

        DF = pd.DataFrame(data=columns, columns=data_header)
        print(DF)

    def text_scraping(self, obj, List):
        for content in obj:
            str_content = content.text.strip()
            List.append(str_content)


class International_Conferences(object):

    def Scraping_range(self):
        Fields = ["systems-biology", "integrative-computational-biology-bioinformatics", "cancer-biology", "bio-engineering", "biophysics" ]
        ResultsList = []
        for field in Fields:
            results = self.Scraping_by_Field(field)
            ResultsList.append(results)
        DF = pd.concat(ResultsList)
        DF.to_csv('E:/BioJobs/%s_BioConference_international.csv' % TODAYis, ',')


    def Scraping_by_Field(self, Field):
        dataHead = ["Field", "Conference_Name", "Date", "URL", "Venue"]

        driver = start_Chrome()

        driver.maximize_window()
        driver.implicitly_wait(3)
        driver.get('http://integrativebiology.conferenceseries.com/events-list/'+Field)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        notices = soup.find_all("div", {"class": "conference-info"})
        columns = []
        for each_info in notices:
            dates = each_info.find_all("div", class_="dates")
            Date = self.text_scraping(dates)

            url = each_info.find_all("a")
            for i in url:
                Link = i["href"]
                Name = i["title"]

            venues = each_info.find_all("div", {"class": "cityCountry text-uppercase"})
            Venue = self.text_scraping(venues)
            dataList = [Field, Name, Date, Link, Venue]
            columns.append(dataList)

        driver.close()
        DF = pd.DataFrame(data=columns, columns=dataHead)
        return DF

    def text_scraping(self, obj):
        for content in obj:
            str_content = content.text.strip()
        return str_content



if __name__== "__main__":
    #domestics = Domestic_Conferences()
    #links = domestics.STEP1()
    #domestics.STEP2(links)
    international = International_Conferences()
    international.Scraping_range()
