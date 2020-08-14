from pymysql import connect
from selenium import webdriver
import time


class Review:
    # 评论日期
    date = ''
    # 评论内容
    content = ''
    # 评论是否为翻译而来，是为0，不是为1
    is_tran = ''
    # 评论点赞数
    zan = ''
    # 评论照片，多张照片之间用,分隔
    photo = ''
    # 评分
    score = ''
    # 餐馆日期
    visit_date = ''
    # 用户名
    user_name = ''
    # 评论的景点id
    scenic_id = ''


def connectDB():
    """
    数据库连接的相关信息在此修改
    """
    host = '127.0.0.1'
    user_name = 'root'
    password = '123456'
    database = 'tripadvisor'
    db = connect(host=host, user=user_name, password=password, db=database)
    return db


def getData(browser, scenic_id):
    """
        :param browser: WebDriver对象
        :param scenic_id: 景点id
        :return: 一个Review的list
    """

    # 获取 "更多" 按钮，触发其点击事件 （点击更多使得评论内容完整）
    try:
        review_more_tag = browser.find_element_by_css_selector('.taLnk.ulBlueLinks')
        review_more_tag.click()
    except:
        print("无 更多按钮")

    # 获取包裹评论的大div
    reviews = browser.find_element_by_css_selector("#REVIEWS")

    ##此处可以优化，，，什么显示等待啥玩意的，看不懂，先不管了
    # 歇3秒，等下边图片和内容加载加载
    time.sleep(3)
    # 获取头像
    # user_head_images = []
    # user_head_images_tags = reviews.find_elements_by_css_selector(".basicImg")
    # for user_head_images_tag in user_head_images_tags:
    #     user_head_images.append(user_head_images_tag.get_attribute('src'))

    # 获取评论内容
    review_contents = []
    review_content_tags = reviews.find_elements_by_css_selector(".partial_entry")
    for review_content_tag in review_content_tags:
        review_contents.append(review_content_tag.text)

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
            review_is_trans_parent_tag.find_element_by_css_selector(".headers")
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
    # 获取评论评分
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


def transform_datas(data_lists):
    """
    把每页的数据集合拼成一个大集合
    """
    reviews = []
    for data_list in data_lists:
        reviews.extend(data_list)
    return reviews


def write_to_db(db, reviews):
    """
        将数据写入数据库
    """
    cursor = db.cursor()
    sql = "INSERT INTO review(date,content,is_tran,zan,photo,score,visit_date,user_name,scenic_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    for review in reviews:
        cursor.execute(sql, [review.date, review.content, review.is_tran, review.zan, review.photo, review.score,
                             review.visit_date, review.user_name, review.scenic_id])
    db.commit()


def crawl_save_review(url, scenic_id):
    """
        爬取并且存储数据
    """
    db = connectDB()
    browser = webdriver.Chrome()
    browser.get(url)

    data_lists = []
    # 第几页
    count = 0
    while True:
        count += 1
        print(count)
        try:
            list = getData(browser, scenic_id)
            data_lists.append(list)
            # 该景点无中文评论，则页面上显示的是英文评论，会出异常，直接break爬取下一个
        except IndexError:
            print("页面非中文或ip被禁用")
            break
        # 请求超时,则记录当前url重新请求
        except Exception:
            print("请求超时")
            current_url = browser.current_url
            browser.quit()
            browser = webdriver.Chrome()
            browser.get(current_url)




        # 如果找不到第一页，则说明该页面连分页条都没有，不用翻页，直接爬取下一个
        try:
            browser.find_element_by_css_selector(".pageNum.first")
        except:
            print("这个景点就一页")
            break

        # 获取下一页的按钮，点击
        next_page = browser.find_element_by_css_selector(".nav.next")
        if next_page.get_attribute("href") is None:
            break
        else:
            next_page.click()

    reviews = transform_datas(data_lists)
    write_to_db(db, reviews)
    browser.quit()
    db.close()


if __name__ == "__main__":
    db = connectDB()
    cursor = db.cursor()

    sql = "SELECT id,href FROM scenic_spot WHERE adress= %s"

    cursor.execute(sql, ["北京"])

    results = cursor.fetchall()
    for i in range(len(results)):
        url = "https://www.tripadvisor.cn" + results[i][1]
        crawl_save_review(url, results[i][0])
