# 数据库表结构

**表scenic_spot（id，adress，href，name）**

adress为城市名

href为链接

name为景点名

**表review（id，date，is_tran，zan，photo，visit_date，content，user_name，user_id，scenic_id，score）**

date：评论日期

is_tran：该评论是否由翻译而来（0为中文评论，1为翻译而来的评论）

zan：该评论的点赞数

photo：评论的图片（没有图片为空，多张图片以英文逗号分隔，其中data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==这种格式的值为爬虫爬取错误，说明爬虫在图片未加载的情况下爬取了该图片的链接）

visit_date：游玩日期，（没写日期为空，格式为"体验日期：2020年7月"，需进一步处理）

content：评论内容

user_name：用户名（用户的主页是由用户名拼接而成，可用这个拼接去爬用户主页的一些东西。。）

user_id：全为空，以后爬了用户信息，可以给加上外键

scenic_id：景点id，scenic_spot表的外键

score：该评论给出的评分



# 爬虫介绍

**景点地址爬虫**

用requests库和beautifulsoup写的，从上到下写的。。。这个就不建议使用

**评论爬虫**_**运行班**

运行过的版本。用selenium写的，用的是Chrome的driver，爬取的内容是上面那些，直接写入了mysql数据库。

**评论爬虫_修改版**

没跑过，但应该没啥问题，改了之后感觉也没啥差别，但代码没那么乱了。

# 存在的问题

1.虽然说共有1650个北京市的景点，但大概只有前200个评论数比较多，500之后的评论基本都是几条甚至没有评论。

2.爬取数据过程中，产生了部分冗余数据（两条数据一模一样），需要进一步处理

3.爬取的图片链接，有很大一部分没有加载出来，，，还需完善

# 文件介绍

xxx.sql为转储的sql文件，内包含数据

xxx.py为爬虫文件