import requests

url = 'http://127.0.0.1:8000/query-with-langchain-gpt4'
params = {
    'uuid_number': '42d4634a-09c9-11ee-b47a-0d5cda16a4a6',
    'query_string': 'why QuML'
}
headers = {
    'Accept': 'text/plain'
}

# Send the GET request with the specified parameters and headers
response = requests.get(url, params=params, headers=headers, stream=True)

# Process the streamed response
buffer = b""  # Buffer to accumulate chunks

for chunk in response.iter_content(chunk_size=None):
    buffer += chunk

    # Process the buffer once a certain threshold is reached
    if len(buffer) >= 1024:  # Adjust the threshold as needed
        print(buffer.decode('utf-8'))  # Process the buffer as needed
        buffer = b""  # Clear the buffer

# Process any remaining data in the buffer
if buffer:
    print(buffer.decode('utf-8'))  # Process the remaining data in the buffer
