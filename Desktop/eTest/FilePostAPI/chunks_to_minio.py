from elasticsearch import Elasticsearch
import os
from PyPDF2 import PdfReader, PdfWriter
import boto3 
from io import BytesIO
from elasticsearch.helpers import bulk



es = Elasticsearch({"scheme": "http", "host": "localhost", "port": 9200})
print(es.ping())
idx='minio_files_index'

# Initialize AWS S3 client (boto3) to access MinIO
s3_client = boto3.client('s3',
                         endpoint_url='http://127.0.0.1:9000',
                         aws_access_key_id='minioadmin',
                         aws_secret_access_key='minioadmin',
                         verify=False)
bucket_name = 'chunkingfiles'



def split_pdf_folder(folder_name):
    # Create a directory to store the output files
    output_dir = folder_name + '_split'
    os.makedirs(output_dir, exist_ok=True)

    # Get a list of PDF files in the input folder
    pdf_files = [file for file in os.listdir(folder_name) if file.lower().endswith('.pdf')]

    # Split each PDF file into chunks
    for pdf_file in pdf_files:
        filename = os.path.join(folder_name, pdf_file)
        with open(filename, 'rb') as file:
            pdf = PdfReader(file)
            total_pages = len(pdf.pages)

            # Determine the number of chunks
            num_chunks = total_pages // 2
            if total_pages % 1 != 0:
                num_chunks += 1

            # Split the PDF into chunks
            for i in range(num_chunks):
                start_page = i * 1
                end_page = min((i + 1) * 1, total_pages)
                output_pdf = PdfWriter()

                # Add pages to the output PDF
                for page_num in range(start_page, end_page):
                    output_pdf.add_page(pdf.pages[page_num])

                # Save the output PDF as a new file
                    output_filename = os.path.join(output_dir, f'{os.path.splitext(pdf_file)[0]}_{i+1}.pdf')
                    with open(output_filename, 'wb') as output_file:
                        output_pdf.write(output_file)

    return os.path.abspath(output_dir)

# Usage example
folder_name = r'C:\updated_summarization_code\attachments'
output_folder = split_pdf_folder(folder_name)
print(f'Successfully split PDF files in folder "{folder_name}" into chunks. Output folder: {output_folder}')



def folder_to_minio(local_folder,minio_bucket):
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_file_path, local_folder)
            s3_client.upload_file(local_file_path, minio_bucket, s3_key)
folder_to_minio(r"C:\updated_summarization_code\attachments_split","chunkingfiles")





def index_file_content_to_es(bucket_name):
    try:
        # List all objects in the bucket
        objects = s3_client.list_objects(Bucket=bucket_name)
        actions = []
        for obj in objects['Contents']:
            object_name = obj['Key']
            
            # Check if a document with the same file_name exists in Elasticsearch
            if document_already_exists(object_name):
                print(f"Document '{object_name}' already exists in Elasticsearch. Skipping.")
                continue
            
            content = s3_client.get_object(Bucket=bucket_name, Key=object_name)
            file_content = content['Body'].read()  # Read the PDF content as binary data

            # Extract text from the PDF content
            pdf_text = extract_text_from_pdf(file_content)

            # Get the MinIO file link
            file_link = get_minio_file_link(bucket_name, object_name)

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

        # Use Elasticsearch bulk indexing to efficiently index the documents
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


def get_minio_file_link(bucket_name, object_name):
    # Construct the MinIO file link
    minio_file_link = f"http://127.0.0.1:9000/{bucket_name}/{object_name}"
    return minio_file_link

# Call the function to read files from MinIO, extract text, and index the content into Elasticsearch
index_file_content_to_es(bucket_name)

