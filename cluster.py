from sentence_transformers import SentenceTransformer
from newspaper import Article
import hdbscan
import json
import requests
from elasticsearch import Elasticsearch, helpers
import os
import re
import time


client = Elasticsearch("http://es:9200/")

allArticles = []
getAll = client.search(index="*",size =10000)['hits']['hits']
print(f"CLUSTERING {len(getAll)} ARTICLES FOUND IN ELASTIC SEARCH")


for x in range(len(getAll)):
    allArticles.append(getAll.pop(0))
    getAll.append(allArticles[-1]['_source']['content'])
    
# SentenceTransformer embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(getAll, show_progress_bar=True)
print("\n\n\n\n")
print("Vector Encoding: \n")
print(embeddings)
print("\n\n\n\n")


# HDBSCAN clustering
clusterer = hdbscan.HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True,
    gen_min_span_tree=True, leaf_size=40,
    metric='euclidean', min_cluster_size=2, min_samples=None, p=None)
labels = clusterer.fit_predict(embeddings)
print("\n\n\n\n")
print("Label with Cluster IDs: \n")
print(labels)
print("\n\n\n\n")


# Group articles by cluster

# clustered_articles = {}
# for i, label in enumerate(labels):
#     clustered_articles.setdefault(int(label), []).append({
#         "content": getAll[i][:40]
#     })

# print(clustered_articles)


# client.indices.delete(index="newsgroup")

# print(allArticles[0])
# for x in range(len(allArticles)):
#     allArticles[x]["_source"]["event_cluster"].append({'id': labels[x], 'name': ''})
#     client.index(index="newsgroup", id = allArticles[x]["_id"], body = allArticles[x]["_source"])
#     print(f"Document {x} updated successfully!")


for x in range(len(allArticles)):
    allArticles[x]["_source"]["event_cluster"] = str(labels[x])
    client.index(index="newsgroup", id = allArticles[x]["_id"], body = allArticles[x]["_source"])
    print(f"Document {x} updated successfully!")
    
    
# print(f"ELASTIC SEARCH LOAD STATUS: {helpers.bulk(client, allArticles)}")







