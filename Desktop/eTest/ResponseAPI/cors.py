# cors.py

from fastapi.middleware.cors import CORSMiddleware

# Configure CORS settings
origins = [
    "http://localhost",           # Add your frontend domain or IP address here
    "http://localhost:3000",      # Example: If your frontend runs on port 3000
    "https://yourfrontenddomain.com",
]

middleware = CORSMiddleware(
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # You can restrict HTTP methods if needed
    allow_headers=["*"],   # You can restrict HTTP headers if needed
)
