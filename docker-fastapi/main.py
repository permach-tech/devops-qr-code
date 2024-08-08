from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv

# Loading Environment variable (Azure Storage Connection String)
load_dotenv()

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Blob Storage Configuration
connection_string = 'YOUR_AZURE_STORAGE_CONNECTION_STRING'  # Add your Azure Storage connection string here
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = 'YOUR_CONTAINER_NAME'  # Add your Azure Blob Storage container name here

@app.post("/generate-qr/")
async def generate_qr(url: str):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate file name for Azure Blob Storage
    file_name = f"qr_codes/{url.split('//')[-1]}.png"

    try:
        # Upload to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        blob_client.upload_blob(img_byte_arr, overwrite=True)

        # Generate the Azure Blob Storage URL
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{file_name}"
        return {"qr_code_url": blob_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
