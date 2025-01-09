import requests 
header_payload= {
    "Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNzM2NDE1NDY1LCJqdGkiOiIzMDA2YzM2Ny00NmFmLTQ4YWUtYWZkMi1jYWFiMTcyNTllNDYiLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoxLCJuYmYiOjE3MzY0MTU0NjUsImV4cCI6MTczNjQxNjM2NX0.t7QPwiFECMFk7TYfCGgRgNGNWqUPreFXpKa3Be4yzo4"
}
data = requests.get("http://localhost:8088/api/v1/explore/?slice_id=662",headers= header_payload )
print(data.text)