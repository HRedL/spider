import requests
import json
from pymysql import connect

from bs4 import BeautifulSoup
def getHTMLText(url):
    try:

        response = requests.get(url)
        return response.text
    except:
        return "产生异常"


def write_to_file(content,filename):
    with open(filename, 'a') as f:
        f.write(json.dumps(content) + '\n')
        f.close()


def connectDB():
    db = connect('127.0.0.1', 'root', '123456', 'tripadvisor')
    return db



def generate_sql(adress,href,name):
    sql = "INSERT INTO scenic_spot(adress,href,name) VALUES(%s,%s,%s)"
    sql = "INSERT INTO scenic_spot(adress,href,name)"+ "VALUES(" + "'"+str(adress) + "','"+str(href)+ "','"+ str(name) + "')"
    return sql


if __name__ == "__main__":
    # url = "https://www.tripadvisor.cn/Attraction_Review-g294212-d325811-Reviews-or40-Mutianyu_Great_Wall-Beijing.html"
    # text = getHTMLText(url)
    # soup = BeautifulSoup(text, 'html.parser')
    # content = soup.find(id="taplc_location_reviews_list_resp_ar_responsive_0")

    db = connectDB()
    cursor = db.cursor()

    adress = "上海"

    hrefs = []

    names = []

    url = "https://www.tripadvisor.cn/Attractions-g308272-Activities-Shanghai.html#ATTRACTION_SORT_WRAPPER"

    text = getHTMLText(url)

    soup = BeautifulSoup(text, 'html.parser')
    content = soup.find(id="FILTERED_LIST")

    parents = content.find_all(attrs={"class": "listing_title"})
    for parent in parents:
        a_tag = parent.find("a")
        h2_tag = parent.find("h2")
        hrefs.append(a_tag.get("href"))
        names.append(h2_tag.string)
    count = 44
    for i in range(count):

        url = "https://www.tripadvisor.cn/Attractions-g308272-Activities-oa"+  str(i*30) +"-Shanghai.html#FILTERED_LIST"
        text = getHTMLText(url)
        soup =BeautifulSoup(text,'html.parser')
        content =soup.find(id="FILTERED_LIST")
        parents = content.find_all(attrs={"class":"listing_title"})
        for parent in parents:
            a_tag = parent.find("a")
            h2_tag = parent.find("h2")
            hrefs.append(a_tag.get("href"))
            names.append(h2_tag.string)

    for i in range(len(hrefs)):
        sql = sql = "INSERT INTO scenic_spot(adress,href,name) VALUES(%s,%s,%s)"
        cursor.execute(sql,[adress,hrefs[i],names[i]])
        print("写入数据库结束")
    db.commit()
    db.close()


