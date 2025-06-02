# auth_module.py
import os
import requests
import re
from dotenv import load_dotenv
requests.packages.urllib3.disable_warnings()

class Authenticator:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('USERNAMEID')
        self.password = os.getenv('PASSWORD')
        if not self.username or not self.password:
            raise ValueError("請在 .env 檔案中設定 USERNAMEID 與 PASSWORD 環境變數。")
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'Referer': 'https://iclass.tku.edu.tw/'})
        self.auth_url = (
            "https://sso.tku.edu.tw/auth/realms/TKU/protocol/openid-connect/auth"
            "?client_id=pdsiclass&response_type=code&redirect_uri=https%3A//iclass.tku.edu.tw/login"
            "&state=L2lwb3J0YWw=&scope=openid,public_profile,email"
        )

    def check_login_success(self,response):
        content = response.text
        match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)

        if match and match.group(1) == "淡江大學單一登入(SSO)":
            print("login fail")
            return False
        else:
            print("login pass")
            return True

    def perform_auth(self):
        self.session.get("https://iclass.tku.edu.tw/login?next=/iportal&locale=zh_TW")
        self.session.get(self.auth_url)
        login_page_url = f"https://sso.tku.edu.tw/NEAI/logineb.jsp?myurl={self.auth_url}"
        login_page = self.session.get(login_page_url)
        jsessionid = login_page.cookies.get("AMWEBJCT!%2FNEAI!JSESSIONID")
        if not jsessionid:
            raise ValueError("無法取得 JSESSIONID")

        image_headers = {
            'Referer': 'https://sso.tku.edu.tw/NEAI/logineb.jsp',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
        }
        self.session.get("https://sso.tku.edu.tw/NEAI/ImageValidate", headers=image_headers)
        post_headers = {
            'Origin': 'https://sso.tku.edu.tw',
            'Referer': 'https://sso.tku.edu.tw/NEAI/logineb.jsp'
        }
        body = {'outType': '2'}
        response = self.session.post("https://sso.tku.edu.tw/NEAI/ImageValidate", headers=post_headers, data=body)
        vidcode = response.text.strip()

        payload = {
            "myurl": self.auth_url,
            "ln": "zh_TW",
            "embed": "No",
            "vkb": "No",
            "logintype": "logineb",
            "username": self.username,
            "password": self.password,
            "vidcode": vidcode,
            "loginbtn": "登入"
        }
        login_url = f"https://sso.tku.edu.tw/NEAI/login2.do;jsessionid={jsessionid}?action=EAI"
        
        response = self.session.post(login_url, data=payload)
        
        if self.check_login_success(response) != True:
            return {"erorr":"user name or password maybe not currect on the os level"}
        headers = {'Referer': login_url, 'Upgrade-Insecure-Requests': '1'}
        user_redirect_url = (
            f"https://sso.tku.edu.tw/NEAI/eaido.jsp?"
            f"am-eai-user-id={self.username}&am-eai-redir-url={self.auth_url}"
        )
        self.session.get(user_redirect_url, headers=headers)

        return self.session
