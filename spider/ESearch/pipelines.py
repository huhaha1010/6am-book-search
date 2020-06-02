# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class EsearchPipeline(object):
    def process_item(self, item, spider):
        # print item
        return item
#为了代码的清晰度，将es数据类型定义、格式转换和es的连接放到models/es_types.py
from models.es_types import CommonbookType


class ElasticsearchPipeline(object):

    def process_item(self, item, spider):
        print item
        job = CommonbookType(item)# 将item转换为es所需格式
        # 将数据传入es
        # jobType继承自DocType，所以DocType有的函数，它都有。
        # save就是DocType定义的将类中的各成员变量打包成数据插入操作，进行数据插入的函数
        job.save()

        #仍返回item，使得运行窗口能看到爬到的数据
        return item