# -*- coding: utf-8 -*-
__author__ = 'jiechao'

from elasticsearch_dsl import Document, Date, analyzer,Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
es = connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class CommonbookType(Document):
    class Index:
        name = "booksearch"
        # index建立索引的时候不能用大写
        doc_type = "_doc"

    suggest = Completion(analyzer=ik_analyzer)
    book_name = Text(analyzer="ik_max_word")
    book_author = Text(analyzer="ik_max_word")
    book_content = Text(analyzer="ik_max_word")
    book_type = Keyword()
    book_format = Keyword()
    book_time = Text()
    book_url = Keyword()
    book_downl_url = Keyword()
    book_source = Keyword()
    book_intro = Text(analyzer="ik_max_word")
    book_zip_pwd = Keyword()
    book_id = Keyword()
    book_chinese = Keyword()
    book_size = Text()
    kindle_name = Text(analyzer="ik_max_word")
    kindle_author = Text(analyzer="ik_max_word")
    kindle_score = Keyword()
    kindle_intro = Text(analyzer="ik_max_word")
    kindle_url = Keyword()
    kindle_type = Keyword()
    kindle_id = Keyword()

    # class Meta:
    #     index = "comeearch"
    #     # index建立索引的时候不能用大写
    #     doc_type = "_doc"



    def assignment(self, item):
        # TODO：给没爬到的字段赋默认值：空串
        # keys = ['url', 'job_name', 'salary', 'company', 'job_position', 'experience', 'education', 'number_of_people',
        #         'published_time', 'position_detail', 'position_type', 'location', 'company_detail']
        keys = ['book_name', 'book_author', 'book_content', 'book_type', 'book_format', 'book_time', 'book_url',
                'book_downl_url', 'book_source', 'book_intro', 'book_zip_pwd', 'book_id', 'book_chinese', 'book_size',
                'kindle_name', 'kindle_author', 'kindle_score', 'kindle_intro', 'kindle_url', 'kindle_type',
                'kindle_id']
        # for key in keys:
        #     try:
        #         item[key]
        #     except:
        #         item[key] = ''
        # TODO：将字段值转换为es的数据
        # 虽然只是将原来的item值赋给了成员变量，但这个过程中会执行数据格式转换操作，比如url本来在item是python的字符串类型，转换后变为es的keyword类型
        # self.url = item['url']
        self.book_name = item['book_name']
        self.book_author = item['book_author']
        # self.book_content = item['book_content']
        self.book_type = item['book_type']
        # self.book_format = item['book_format']
        # self.book_time = item['book_time']
        self.book_url = item['book_url']
        # self.book_down_url = item['book_downl_url']
        self.book_source = item['book_source']
        self.book_intro = item['book_intro']
        self.suggest = self.gen_suggests(((self.book_name, 10), (self.book_author, 7)))
        # self.book_zip_pwd = item['book_zip_pwd']
        # self.book_id = item['book_id']
        # self.book_chinese = item['book_chinese']
        # self.book_size = item['book_size']
        # self.kindle_name = item['kindle_name']
        # self.kindle_author = item['kindle_author']
        # self.kindle_score = item['kindle_score']
        # self.kindle_intro = item['kindle_intro']
        # self.kindle_url = item['kindle_url']
        # self.kindle_type = item['kindle_type']
        # self.kindle_id = item['kindle_id']

    def __init__(self,item):
        super(CommonbookType, self).__init__()#调一下父类的init，避免init重写导致一些init操作没执行
        self.assignment(item)

    def gen_suggests(self, info_tuple):
        # 根据字符串生成搜索建议数组
        used_words = set()  # set为去重功能
        suggests = []
        for text, weight in info_tuple:
            if text:
                # 字符串不为空时，调用elasticsearch的analyze接口分析字符串（分词、大小写转换）
                words = es.indices.analyze(body={'text': text, 'analyzer': "ik_max_word"})
                print ("words = ")
                print (words)
                # anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
                analyzed_words = []
                for r in words["tokens"]:
                    if len(r["token"]) > 1:
                        analyzed_words.append(r["token"])
                anylyzed_words = set(analyzed_words)

                new_words = anylyzed_words - used_words
            else:
                new_words = set()

            if new_words:
                suggests.append({'input': list(new_words), 'weight': weight})
        return suggests


if __name__ == "__main__":
    CommonbookType.init()


