
import json
from django.shortcuts import render
from django.views.generic.base import View
from .models import CommonbookType

from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()

class IndexView(View):
    # 首页
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = [item.decode('utf8') for item in topn_search]
        return render(request, "index.html", {"topn_search": topn_search})

class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s','')
        re_datas = []
        if key_words:
            s = CommonbookType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field":"suggest", "fuzzy":{
                    "fuzziness":2
                },
                "size": 10
            })
            print (s.to_dict())
            suggestions = s.execute().suggest
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["book_name"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")

class SearchView(View):

    def get(self,request):
        response = client.search(
            index="booksearch",
            body={
            }
        )
        redis_cli.set("total", response['hits']['total']['value'])
        # 获取搜索关键字
        key_words = request.GET.get("q", "")
        # 获取当前选择搜索的范围
        s_type = request.GET.get("s_type", "")

        redis_cli.zincrby("search_keywords_set", 1, key_words)  # 该key_words的搜索记录+1

        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = [item.decode('utf8') for item in topn_search]

        # key_words = request.GET.get('q','')
        page = request.GET.get('p','')
        try:
            page = int(page)
        except:
            page = 0

        start_time = datetime.now()
        response = client.search(
            index = "booksearch",
            body = {
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["book_name","book_intro","book_type"]
                    }
                },
                "from":page*10,
                "size":10,
                "highlight":{
                    "pre_tags" : ["<span class='keyWord'>"],
                    "post_tags":["</span>"],
                    "fields":{
                        "book_name":{},
                        "book_intro":{},
                        "book_type":{},
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()

        total_nums = response["hits"]["total"]["value"]
        if (page%10) > 0:
            page_nums = total_nums/10 +1
        else:
            page_nums = total_nums/10
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            print (hit)
            if "book_name" in hit["highlight"]:
                hit_dict["book_name"] =''.join(hit["highlight"]["book_name"])
            else:
                hit_dict['book_name'] =''.join(hit["_source"]["book_name"])
            if "content" in hit["highlight"]:
                hit_dict["book_intro"] =''.join(hit["highlight"]["book_intro"][:200])
            else:
                hit_dict["book_intro"] =''.join(hit["_source"]["book_intro"][:200])
            if "book_type" in hit["highlight"]:
                hit_dict["book_type"] =''.join(hit["highlight"]["book_type"])
            else:
                hit_dict["book_type"] =''.join(hit["_source"]["book_type"])

            hit_dict["book_author"] = hit["_source"]["book_author"]
            # hit_dict["book_format"] = hit["_source"]["book_format"]
            # hit_dict["book_time"] = hit["_source"]["book_time"]
            hit_dict["book_url"] = hit["_source"]["book_url"]
            # hit_dict["book_downl_url"] = hit["_source"]["book_downl_url"]
            hit_dict["book_source"] = hit["_source"]["book_source"]
            # hit_dict["book_zip_pwd"] = hit["_source"]["book_zip_pwd"]
            # hit_dict["book_id"] = hit["_source"]["book_id"]
            # hit_dict["book_chinese"] = hit["_source"]["book_chinese"]
            # hit_dict["book_size"] = hit["_source"]["book_size"]
            # hit_dict["kindle_name"] = hit["_source"]["kindle_name"]
            # hit_dict["kindle_author"] = hit["_source"]["kindle_author"]
            # hit_dict["kindle_score"] = hit["_source"]["kindle_score"]
            # hit_dict["kindle_intro"] = hit["_source"]["kindle_intro"]
            # hit_dict["kindle_url"] = hit["_source"]["kindle_url"]
            # hit_dict["kindle_type"] = hit["_source"]["kindle_type"]
            # hit_dict["kindle_id"] = hit["_source"]["kindle_id"]

            hit_list.append(hit_dict)

        return render(request,"result.html",{"page":page,
                                             "all_hits":hit_list,
                                             "key_words":key_words,
                                             "total_nums":total_nums,
                                             "page_nums":page_nums,
                                             "last_seconds":last_seconds,
                                             "topn_search": topn_search
                                             })

