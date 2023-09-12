import requests

response = requests.get("https://www.naver.com")
data = response.text
print(data)