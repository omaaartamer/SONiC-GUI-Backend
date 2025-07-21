import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")
USERNAME = os.getenv("SONIC_USERNAME")
PASSWORD = os.getenv("SONIC_PASSWORD")

async def fetch_vlans():
    if not SONIC_BASE_URL:
        raise Exception("SONIC_BASE_URL not set in .env")

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(SONIC_BASE_URL, auth=(USERNAME, PASSWORD), headers={
            "Accept": "application/yang-data+json"
        })

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch VLANs: {response.status_code} - {response.text}")
