from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import date
from calendar import monthrange
import pandas as pd
import numpy as np
import pickle
import sqlite3
TODAYis = '20170921'
save_path = 'E:/BioJobs/%s_bric_recruit.pkl' % TODAYis
data_header = ['NO', 'Employer', 'Qualification', 'Due', 'Viewed']
data_header_mod = ['NO', 'Employer', 'Qualification', 'Min_salary', 'Max_salary', 'Due', 'Viewed', 'Link']
def Paging():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-pop')
    driver = webdriver.Chrome(executable_path="C:/Users/qwerty/chromedriver.exe", chrome_options=chrome_options)
    #driver.set_window_size(1920, 1080)
    driver.maximize_window()
    driver.implicitly_wait(3)
    driver.get('http://www.ibric.org/myboard/list.php?Board=job_recruit&Page=1&selflevel=-1')


    pages = ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']    

    DF_list = []

    (driver, soup, DF) = html_scrapping(driver)
    DF_list.append(DF)

    #pages_tag = soup.find('table', attrs={'border': '0', 'cellspacing': '0', 'cellpadding': '0', 'width': '100%', 'class': 'tab','bgcolor': 'f7f7f7'})
    #pages = pages_tag.find_all('a')

    for page in pages:
        driver.implicitly_wait(3)
        if page=='11' or page=='21':
            cmd = driver.find_element_by_xpath('//a[img/@src="/images/public/btn_say_next.gif"]')
        else:
            cmd = driver.find_element_by_link_text(page)
        location = cmd.location["y"] - 100
        driver.execute_script("window.scrollTo(0, %d);" % location)
        cmd.click()

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
    titles = table.find_all("a", class_="abase")

    board_link = []

    for tt in titles:
        link = tt['href']
        board_link.append("http://www.ibric.org/myboard/" + link)

    Link = pd.Series(data=board_link, name="Link")

    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        #col_link = "http://www.ibric.org/myboard/" + col_link['href']
        cols = [ele.text.strip() for ele in cols]
        if len(cols) == 5:
            # data.append([ele for ele in cols])
            data.append([ele for ele in cols if ele])  # Get rid of empty values


    data = data[1:]
    DF = pd.DataFrame(data=data, columns=data_header)
    DF = pd.concat([DF, Link], axis=1)



    driver.implicitly_wait(3)
    return (driver, soup, DF)


class To_SQLite(object):
    def create_SQLite_from_DataFrame(self, DB, TABLE_NAME, DF):
        with sqlite3.connect(DB) as conn:
            DF.to_sql(TABLE_NAME, conn, if_exists='replace')

    def fetching_Data_from_Pickle(self):
        savefile = open(save_path, 'rb')
        DF = pickle.load(savefile)
        Due_date = []
        for i in DF.Due:
            TODAY = date.today()
            Month = int(i.split(".")[0])
            if Month < TODAY.month:
                Year = TODAY.year+1
            else:
                Year = TODAY.year

            Day = int(i.split(".")[-1])
            (Weekday, LastDay) = monthrange(Year, Month)
            try:
                dates = date(year=Year, month=Month, day=Day)

            except ValueError as val:
                dates = date(year=Year, month=Month, day=LastDay)
            Due_date.append(dates)
        Due_date = pd.Series(Due_date, name='Due')
        Qualify = []
        Salary_Max = []
        Salary_Min = []
        for j in DF.Qualification:
            BinaryCut = j.split("\xa0\xa0")
            Qualify.append(BinaryCut[0])
            min_value = int(BinaryCut[1][0:4])
            max_value = int(BinaryCut[1].split("~")[1][1:5])
            Salary_Min.append(min_value)
            if min_value >= max_value:
                Salary_Max.append(max_value*10)
            else:
                Salary_Max.append(max_value)

        DF = DF.drop('Due', 1)
        DF = DF.drop('Qualification', 1)
        Qualify = pd.Series(Qualify, name='Qualification')
        #Salary = pd.DataFrame(data=[Salary_Min, Salary_Max], columns=['Min_Salary', 'Max_Salary'])
        Salary_Max = pd.Series(Salary_Max, name='Max_Salary')
        Salary_Min = pd.Series(Salary_Min, name='Min_Salary')

        DF = pd.concat([DF.NO, DF.Employer, Qualify, Salary_Min, Salary_Max, Due_date, DF.Viewed, DF.Link], axis=1, join_axes=[DF.index])
        DF.to_csv('E:/BioJobs/%s_bric_recruit.csv' % TODAYis, ',')

        return DF

    def fetching_Data_from_SQLite(self, DB, TABLE_NAME):
        with sqlite3.connect("%s" %DB) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM "+ TABLE_NAME + " WHERE Qualification LIKE '%석사%' OR Qualification LIKE '%학사%'" )
            #cur.execute("SELECT * FROM " + TABLE_NAME + " WHERE Qualification LIKE '%박사%' AND Employer LIKE '%난치암%'")
            #cur.execute("SELECT * FROM " + TABLE_NAME + " WHERE Qualification LIKE '%박사%'")
            #cur.execute("SELECT * FROM " + TABLE_NAME )
            searchResult = cur.fetchall()
            conn.commit()
            for i in range(0, len(searchResult)):
                searchResult[i] = searchResult[i][1:]
            searchDF = pd.DataFrame(data=searchResult, columns=data_header_mod)
            searchDF.to_csv('E:/BioJobs/%s_bric_MSc_recruit.csv' % TODAYis, ',')


if __name__== "__main__":
    Paging()
