import json
import requests
from elasticsearch import Elasticsearch, helpers
import os
import re
import time


client = Elasticsearch("http://es:9200/")

def ESfetch():
    query = input("Search News: ")
    start_time = time.time()
    resp = client.search(index="newsgroup", body={"query": {"match": {"content": query }})
    print("Got {} hits ".format(resp["hits"]["total"]["value"]) + "in --- %s seconds ---:\n\n\n" % (time.time() - start_time))

    data = {"nArticles" : ""}
    counter = 1

    clustercover = []
    for doc in resp["hits"]["hits"]:
        clustercover.append(doc['_source']['content'])

    for doc in resp["hits"]["hits"]:
        data['nArticles'] += f"Article {counter}: " + doc['_source']['content'] + "\n\n\n\n"
        # print(doc)
        counter += 1

    return data


cont = True

while cont:
    data = ESfetch()

    #USE GEMINI API
    start_time = time.time()
    # Sending requests to the running backend
    response = requests.post("http://localhost:8000/rag-gemini-test", json=data)
    if not response.status_code == 200:
        #USE DREESE API
        print(response)
        print("[SERVER ERROR]: Gemini API Call failed, defaulting to Dreese Server. . .")
        start_time = time.time()
        response = requests.post("http://localhost:8000/rag-dreese-test", json=data)
        if not response.status_code == 200:
            #RUN OLLAMA
            print(response)
            print("[SERVER ERROR]: Dreese API Call failed, defaulting to local Ollama. . .")
            start_time = time.time()
            response = requests.post("http://localhost:8000/rag-ollama-test", json=data)
            if not response.status_code == 200:
                print(response)
                print("[SERVER ERROR]: Local Ollama Call failed, tough luck :(")
            else:
                print("[OLLAMA(llama3.2)] Neutral Summary in --- %s seconds ---:\n\n\n" % (time.time() - start_time))
                print(response.json()["summary"])
        else:
            print("[OLLAMA(llama3.2)] Neutral Summary in --- %s seconds ---:\n\n\n" % (time.time() - start_time))
            print(response.json()["summary"])
    else:
        print("[GEMINI] Neutral Summary in --- %s seconds ---:\n\n\n" % (time.time() - start_time))
        for part in response.json()["summary"]:
            print(part['text'])

    
    if input("Continue?(Y/N): ") == "N":
        cont = False


