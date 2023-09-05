from elasticsearch import Elasticsearch


es = Elasticsearch({"scheme": "http", "host": "localhost", "port": 9200})

def search(query_text):
        query = {
            "bool": {
                "must": [{
                    "match": {
                        "content": {
                            "query": query_text,
                            "boost": 1
                        }
                    }
                }]
            }
        }

        fields = ["file_name","content","file_link"]
        index = "minio_files_index"
        resp = es.search(index=index,
                         query=query,
                         fields=fields,
                         size=5,
                         source=False)

        summarizations = []
        fdir = []

        for hit in resp['hits']['hits']:
            if 'file_link' in hit['fields']:
                file_link = hit['fields']['file_link'][0]
                fdir.append(file_link)

            if 'content' in hit['fields']:
                content = hit['fields']['content'][0]
                summarizations.append(content)

        return summarizations, fdir