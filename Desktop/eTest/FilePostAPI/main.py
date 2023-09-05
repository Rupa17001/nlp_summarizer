from fastapi import FastAPI, UploadFile, File
import os
import shutil
from typing import List
import uvicorn

import filleInMinio
import elastic
import chunkingFile
from cors import middleware

app = FastAPI()
app.add_middleware(middleware)


bucket_name = 'elasticfiles'

@app.post("/upload-process/")
async def upload_process(files: List[UploadFile] = File(...)):
    minio_cl = filleInMinio.minio_client
    try:
        temp_folder = "temp_folder"
        os.makedirs(temp_folder, exist_ok=True)
        
        for file in files:
            with open(os.path.join(temp_folder, file.filename), "wb") as f:
                f.write(file.file.read())
                
        output_folder = chunkingFile.split_pdf_folder(temp_folder)
        minio_cl.folder_to_minio(output_folder, bucket_name)
        elastic.index_file_content_to_es(bucket_name)

        shutil.rmtree(os.path.abspath(temp_folder))
        shutil.rmtree(os.path.abspath(output_folder))

        return {"message": "Files uploaded and processed successfully."}

    except Exception as e:
        return {"message": f"Error: {e}"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
