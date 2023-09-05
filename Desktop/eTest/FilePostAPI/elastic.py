from filleInMinio import minio_client
from PyPDF2 import PdfReader, PdfWriter
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from io import BytesIO


es = Elasticsearch({"scheme": "http", "host": "localhost", "port": 9200})
idx = 'minio_files_index'


def index_file_content_to_es(bucket_name):
    s3_client = minio_client.config()
    try:
        # List all objects in the bucket
        objects = s3_client.list_objects(Bucket=bucket_name)
        actions = []
        existing_documents = set()  # To store existing document names

        # Fetch existing document names from Elasticsearch
        query = {
            "size": 10000,  # Adjust as needed
            "query": {
                "match_all": {}
            }
        }
        result = es.search(index=idx, body=query)
        for hit in result['hits']['hits']:
            existing_documents.add(hit["_source"]["file_name"])

        for obj in objects['Contents']:
            object_name = obj['Key']

            # Check if the document already exists in Elasticsearch
            if object_name in existing_documents:
                print(f"Document '{object_name}' already exists in Elasticsearch. Skipping.")
                continue

            content = s3_client.get_object(Bucket=bucket_name, Key=object_name)
            file_content = content['Body'].read()  # Read the PDF content as binary data

            # Extract text from the PDF content
            pdf_text = extract_text_from_pdf(file_content)

            # Get the MinIO file link
            file_link = minio_client.get_minio_file_link(bucket_name, object_name)

            doc = {
                "file_name": object_name,
                "content": pdf_text,
                "file_link": file_link
            }

            action = {
                "_index": "minio_files_index",
                "_source": doc
            }

            actions.append(action)

        # Use Elasticsearch bulk indexing to efficiently index the new documents
        bulk(es, actions)

    except Exception as e:
        print(f"Error: {e}")
def extract_text_from_pdf(pdf_data):
    # Create a PdfReader object to extract text from the PDF
    pdf_reader = PdfReader(BytesIO(pdf_data))

    # Extract text from all pages of the PDF
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    return pdf_text


def document_already_exists(file_name):
    # Check if a document with the same file_name exists in Elasticsearch
    query = {
        "query": {
            "match": {
                "file_name": file_name
            }
        }
    }
    result = es.search(index=idx, body=query)
    return result['hits']['total']['value'] > 0