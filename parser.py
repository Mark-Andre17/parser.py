import json
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd


def get_html_page(n):
    for i in range(0, n + 1):
        i += 1
        url = f'https://www.zillow.com/homes/Chicago,-IL_rb/{i}_p/'
        driver = webdriver.Chrome()
        driver.maximize_window()
        try:
            driver.get(url)
            time.sleep(20)
            with open(f'{i}_page.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()


def get_info():
    df_list = []
    for i in range(1, 4):
        with open(f'{i}_page.html') as file:
            src = file.read()
            data = json.loads(re.search(r'!--(\{"queryState".*?)-->', src).group(1))
            cols = ['street Address', 'City', 'State', 'Zip', 'Sq ft', 'Bed', 'Bath', 'Link']
            for info in data['cat1']['searchResults']['listResults']:
                df_list.append([info["addressStreet"], info["addressCity"], info["addressState"],
                                info["addressZipcode"], info["area"], info["beds"],
                                info["baths"], info["detailUrl"]])
                if len(df_list) == 100:
                    break
    df = pd.DataFrame(df_list, columns=cols)
    return df


def get_build_year(func1):
    list_years = []
    for url in func1['Link']:
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url)
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        years = soup.find_all('span', class_='Text-c11n-8-63-0__sc-aiai24-0 dpf__sc-2arhs5-3 gbKiss btxEYg')[3]
        if 'Built in' in years.text:
            list_years.append(years.text)
        else:
            list_years.append(None)
    col = ['Year_built']
    df1 = pd.DataFrame(list_years, columns=col)
    return df1


def get_excel_file(func1, func2, filename):
    result_df = pd.concat([func1, func2], axis=1, join='outer', ignore_index=True)
    result_df.to_excel(f'{filename}.xlsx', index=False)


if __name__ == '__main__':
    get_html_page(4)
    get_excel_file(get_info(), get_build_year(get_info()), 'chicago')
