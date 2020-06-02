# 6am-book-search书籍搜索引擎

## 1. 运行环境

python2.7(python2都可以吧)，可以先百度下安装anaconda配置一个python2的环境，装好了之后进入anaconda终端，看项目里哪些包没有，直接pip安装就好，不需要自己设置那些包的版本

## 2. 运行项目流程

### ES配置

执行命令

PUT booksearch
{
  "mappings": {
    "properties": {
      "suggest": {
        "type": "completion"
      },
      "book_name": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "book_author": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "book_content": {
        "type": "text"
      },
      "book_type": {
        "type": "keyword"
      },
      "book_url": {
        "type": "keyword"
      },
      "book_source": {
        "type": "keyword"
      },
      "book_intro": {
        "type": "text"
      }
    }
  }
}





### spider(爬虫部分)

目前项目的数据来源有两个网站，分别为e书吧http://eshuba.com/book/和好读网http://haodoo.net/，因此在spider/ESearch/spiders中ESearch.py和Haodoo.py为可用的爬虫

先进入该层目录spider/ESearch/spiders，然后敲入命令scrapy crawl ESearch和scrapy crawl Haodoo，可以一个一个执行



## Django

进入EsearchDjango目录，终端执行命令

python manage.py runserver

再找到templates/index.html，直接点击谷歌浏览器标志即可