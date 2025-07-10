import json
import requests
from elasticsearch import Elasticsearch, helpers
import os
import re
import time


client = Elasticsearch("http://es:9200/")

def ESfetchBy():
    searchBy = input("Search by:\n\tcontent: 0\n\ttitle: 1\n\tcluster#: 2\n\tpublisher: 3\n\n\nENTER(0|1|2|3):\t\t")
    query = input("\nSearch News:\t\t")
    start_time = time.time()

    if searchBy == '1':
        resp = client.search(index="newsgroup",size =10000, body={"query": {"match": {"title": {"query": query, "operator": "and"} }}})
    elif searchBy == '2':
        resp = client.search(index="newsgroup",size =10000, body={"query": {"match": {"event_cluster": {"query": query, "operator": "and"}}}})
    elif searchBy == '3':
        resp = client.search(index="newsgroup",size =10000, body={"query": {"match": {"source": {"query": query, "operator": "and"}}}})
    else:
        resp = client.search(index="newsgroup",size =10000, body={"query": {"match": {"content": {"query": query, "operator": "and"}}}})
    
    print("Got {} hits ".format(resp["hits"]["total"]["value"]) + "in --- %s seconds ---:\n\n\n" % (time.time() - start_time))

    data = {}

    for doc in resp["hits"]["hits"]:
        if doc['_source']['event_cluster'] in data:
            data[doc['_source']['event_cluster']].append(f"[Title]: {doc['_source']['title'][:100]}\n[Content]: {doc['_source']['content'][:100]} . . . \n[Score]: {doc['_score']}")
        else:
            data[doc['_source']['event_cluster']] = [f"[Title]: {doc['_source']['title'][:100]}\n[Content]: {doc['_source']['content'][:100]} . . . \n[Score]: {doc['_score']}"]


    return data



cont = True

while cont:
    data = ESfetchBy()

    # print(data)

    for cluster in data:
        print(f"CLUSTER: {cluster}\n\n")
        for hit in data[cluster]:
            print(hit + "\n")

    
    if input("Continue?(Y/N): ") == "N":
        cont = False


