from elasticsearch import Elasticsearch, helpers
import os
import json
import re

client = Elasticsearch("http://es:9200/")

getAll = client.search(index="*", size =10000)['hits']['hits']
if len(getAll):
    resp = input(f"ELASTIC SEARCH IS NOT EMPTY, FOUND {len(getAll)} ARTICLES INDEXED. STILL PROCEED?(Y/N): ")
    if resp == "N":
        exit(0)
    else:
        resp = input(f"KEEP EXISTING ARTICLES (POTENTIALLY INDEX DUPLICATES)?(Y/N): ")
        if resp != "Y":
            client.indices.delete(index="newsgroup")

with open("data/articles.json") as file:
    docs = json.loads(file.read())
    # print(docs)
    print(f"ELASTIC SEARCH LOAD STATUS: {helpers.bulk(client, docs)}")
            


    




