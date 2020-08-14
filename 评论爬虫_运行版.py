from pymysql import connect
from selenium import webdriver
import time

class Review:
    date = ''
    content = ''
    is_tran = ''
    zan = ''
    photo = ''
    score = ''
    visit_date = ''
    user_name = ''
    scenic_id = ''


def connectDB():
    db = connect('127.0.0.1', 'root', '123456', 'tripadvisor')
    return db


def getData(browser,scenic_id):
    # 如果页面有更多按钮，就点一下更多
    try:
        review_more_tag = browser.find_element_by_css_selector('.taLnk.ulBlueLinks')

        review_more_tag.click()
    except:
        print("无 更多按钮")
    # 获取包裹评论的大div
    reviews = browser.find_element_by_css_selector("#REVIEWS")


##此处可以优化，，，什么显示等待啥玩意的，看不懂，先不管了
    time.sleep(5)
    # 获取评论内容
    review_contents = []
    review_content_tags = reviews.find_elements_by_css_selector(".partial_entry")
    for review_content_tag in review_content_tags:

        review_contents.append(review_content_tag.text)


    # 获取头像
    # user_head_images = []
    # user_head_images_tags = reviews.find_elements_by_css_selector(".basicImg")
    # for user_head_images_tag in user_head_images_tags:
    #     user_head_images.append(user_head_images_tag.get_attribute('src'))

    # 获取用户名和地址
    user_names = []
    user_adresses = []
    user_names_tags = reviews.find_elements_by_css_selector(".info_text.pointer_cursor")
    for user_names_tag in user_names_tags:
        temp = user_names_tag.find_elements_by_css_selector("div")
        user_names.append(temp[0].text)
        if len(temp) == 2:
            user_adresses.append(temp[1].text)
        else:
            user_adresses.append("")

    # 获取评论日期
    review_dates = []
    review_dates_tags = reviews.find_elements_by_css_selector(".ratingDate")
    for review_dates_tag in review_dates_tags:
        review_dates.append(review_dates_tag.get_attribute("title"))

    # 获取评论赞的个数
    review_zans = []
    review_zans_tags = reviews.find_elements_by_css_selector(".numHelp.emphasizeWithColor")
    for review_zans_tag in review_zans_tags:
        review_zans.append(review_zans_tag.text)

    # 获取当前评论是否是翻译，是翻译为1
    review_is_trans = []
    review_is_trans_parents_tags = reviews.find_elements_by_css_selector(".reviewSelector")
    for review_is_trans_parent_tag in review_is_trans_parents_tags:
        try:
            temp = review_is_trans_parent_tag.find_element_by_css_selector(".headers")
            review_is_trans.append(1)
        except:
            review_is_trans.append(0)

    # 获取评论照片
    review_photoes = []
    review_photoes_tags = reviews.find_elements_by_css_selector(".reviewSelector")
    for review_photoes_tag in review_photoes_tags:
        try:
            photoes_tags = review_photoes_tag.find_elements_by_css_selector(".photoContainer")
            temp = ""
            for photoes_tag in photoes_tags:
                temp += photoes_tag.find_element_by_css_selector(".centeredImg").get_attribute("src") + ","
            review_photoes.append(temp)
        except:
            review_photoes.append(None)

    # 获取游玩日期
    visit_dates = []
    visit_dates_tags = reviews.find_elements_by_css_selector(".reviewSelector")
    for visit_dates_tag in visit_dates_tags:
        try:
            dates_tag = visit_dates_tag.find_element_by_css_selector(".prw_rup.prw_reviews_stay_date_hsx")
            visit_dates.append(dates_tag.text)
        except:
            visit_dates.append("")
    #获取评论评分
    review_scores_tags = reviews.find_elements_by_css_selector(".ui_bubble_rating")
    review_scores = []
    for review_scores_tag in review_scores_tags:
        review_scores.append(review_scores_tag.get_attribute("class")[-2])

    list = []
    for i in range(len(user_names)):
        review = Review()
        review.user_name = user_names[i]
        review.date = review_dates[i]
        review.content = review_contents[i]
        review.is_tran = review_is_trans[i]
        review.zan = review_zans[i]
        review.photo = review_photoes[i]
        review.score = review_scores[i]
        review.visit_date = visit_dates[i]
        review.scenic_id = scenic_id
        list.append(review)

    return list


def get_datas(data_lists):
    reviews = []
    for data_list in data_lists:
        for data in data_list:
            reviews.append(data)
    return reviews


def write_to_db(db,datas):
    cursor = db.cursor()
    sql = "INSERT INTO review(date,content,is_tran,zan,photo,score,visit_date,user_name,scenic_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    for review in datas:
        cursor.execute(sql,[review.date,review.content,review.is_tran,review.zan,review.photo,review.score,review.visit_date,review.user_name,review.scenic_id])
    db.commit()


def main(url,scenic_id):
    db = connectDB()
    browser = webdriver.Chrome()
    browser.get(url)
    data_lists = []
    count = 0
    while (True):
        count +=1
        print(count)
        try:
            list = getData(browser,scenic_id)
            data_lists.append(list)
            next_page = None
            "抓取成功"
            # try:
            try:
                first = browser.find_element_by_css_selector(".pageNum.first")
            except:
                print("这个东西就一页")
                break


            next_page = browser.find_element_by_css_selector(".nav.next")
            if next_page.get_attribute("href") == None:
                break
            else:
                next_page.click()

            # except:
            #     print("无下一页")
            #     break
        except IndexError as ie:
            print(ie)
            print("页面非中文或ip被禁用")
            break
        except Exception as e:
            print(e)
            print("请求超时")
            currentUrl = browser.current_url
            browser.quit()
            browser = webdriver.Chrome()
            browser.get(currentUrl)
    reviews = get_datas(data_lists)
    write_to_db(db,reviews)
    browser.quit()
    db.close()


if __name__ == "__main__":
    db = connectDB()
    cursor = db.cursor()

    sql = "SELECT id,href FROM scenic_spot WHERE adress= %s"
    cursor.execute(sql,["北京"])

    results = cursor.fetchall()
    for i in range(len(results)):

        url = "https://www.tripadvisor.cn" + results[i][1]
        main(url,results[i][0])


