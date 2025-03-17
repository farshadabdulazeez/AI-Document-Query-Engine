
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Debugging: Print all environment variables
print("Environment Variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Access specific variables
project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Debugging: Print the loaded variables
print(f"GOOGLE_CLOUD_PROJECT_ID: {project_id}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")

if not project_id or not credentials_path:
    print("Error: Required environment variables are missing.")
else:
    print("Environment variables loaded successfully.")