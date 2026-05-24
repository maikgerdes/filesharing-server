import requests

# req = requests.get("http://localhost:8000/files", params={'filename':'kevin', 'size': 80})
# print(req.text)

file = {'file': open('../webserver/test.docx', 'rb')}
req2 = requests.post("http://localhost:8000/upload/docx/", files= file)
print(req2.text)

req3 = requests.get("http://localhost:8000/veranstalter/1/")
print(req3.text)