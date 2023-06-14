import http.client

conn = http.client.HTTPConnection("127.0.0.1", 8000)
conn.request("GET", "/query-with-langchain-gpt4?uuid_number=42d4634a-09c9-11ee-b47a-0d5cda16a4a6&query_string=why%20QuML", headers={"Accept": "text/plain"})
response = conn.getresponse()

# Process the streamed response
while True:
    chunk = response.read(1024)  # Adjust the chunk size as needed
    if not chunk:
        break
    print(chunk.decode("utf-8"))

conn.close()
