# this is the client
import requests
import sys

def file_uploader(filepath):

    url = "http://localhost:8000/upload"
    
    with open(filepath, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        print("Extracted Text: ", response.json().get('extracted_text', 'No text found.'))
    else:
        print(f"Failed to upload file. Status code: {response.status_code}")
        print("Error:", response.json().get('error', 'Unknown error'))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test.py <filename>")
    else:
        file_uploader(sys.argv[1])