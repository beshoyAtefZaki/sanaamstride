import  requests 
import json 


# get auth token 
url = "http://localhost:8000/api/method/"
method = "sanaamstride.api.auth.login"
def login():
    data = {
        "usr": "almosained@gmail.com" ,
        "pwd": "Sanaam@123456"
    }
    response = requests.post(url+method, data=data )
    print(response.json().get("auth_token"))
    # if response.status_code == 200:
    #     auth_token = response.json().get('message').get('access_token')
    #     return auth_token
    # else:   
    #     print(f"Failed to get auth token: {response.status_code} - {response.text}")
    #     exit(1)

def test_login() :
    auth_token ="Basic NTVjNTRjZjljYmUzMDc1Ojc4ZmM1MTI5ZjU5M2U3YQ=="
    headers = { "Authorization" : auth_token }
    method = "sanaamstride.api.project.get_all"
    response = requests.get(url+method, headers=headers)
    if response.status_code == 200:
        print("Login successful")
        print(response.json())
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
login()