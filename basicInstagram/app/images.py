from dotenv import load_dotenv
from imagekitio import AsyncImageKit
import os

load_dotenv()

imagekit = AsyncImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)

url_endpoint=os.getenv("IMAGEKIT_URL")