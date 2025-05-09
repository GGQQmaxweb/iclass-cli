import json
import os
import requests
import urllib.parse
import re
from datetime import date
from dateutil.relativedelta import relativedelta

class TronClassAPI:
    def __init__(self, session):
        self.session = session

    async def get_todos(self):
        todos_url = "https://iclass.tku.edu.tw/api/todos"
        try:
            response = self.session.get(todos_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching todos: {str(e)}"}

    async def get_bulletins(self):
        base_url = 'https://iclass.tku.edu.tw/api/course-bulletins'
        today = date.today()
        one_month_ago = today - relativedelta(months=1)
        conditions = {
        "start_date": one_month_ago.isoformat(),
        "end_date": today.isoformat(),
        "keyword": ""
        }
        query_string = urllib.parse.urlencode({
            "conditions": json.dumps(conditions)
        })

        url = f"{base_url}?{query_string}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching bulletins: {str(e)}"}

    async def download(self,reference_id):
        url = f"https://iclass.tku.edu.tw/api/uploads/reference/{reference_id}/blob"
        response = self.session.get(url, stream=True)

        # Get filename from Content-Disposition (RFC 5987 format)
        cd = response.headers.get('Content-Disposition')
        filename = 'downloaded_file'  # fallback

        if cd and "filename*=" in cd:
            encoded_filename = cd.split("filename*=UTF-8''")[-1]
            filename = urllib.parse.unquote(encoded_filename)

        # Save file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return filename

    async def get_courses(self):
        url = 'https://iclass.tku.edu.tw/api/my-courses?conditions={"status":["ongoing"]}'
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}
    
    async def get_activities(self,course_id):
        url = f'https://iclass.tku.edu.tw/api/courses/{course_id}/activities?sub_course_id=0'
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}

    async def submit_homework(self, activity_id:int, upload_ids:list):
        url = f'https://iclass.tku.edu.tw/api/course/activities/{activity_id}/submissions'

        headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://iclass.tku.edu.tw',
        }

        payload = {
            "comment": "",
            "uploads": upload_ids,  # List of uploaded file IDs
            "slides": [],
            "is_draft": False,
            "mode": "normal",
            "other_resources": [],
            "uploads_in_rich_text": []
        }

        response = self.session.post(url, headers=headers, data=json.dumps(payload))

        if response.ok:
            return {"Submission successful":response.status_code}
        else:
            return {"Submission failed", response.status_code, response.text}

    async def get_my_files(self,numberOfRequest,page):
        url = "https://iclass.tku.edu.tw/api/user/resources?conditions={%22keyword%22:%22%22,%22includeSlides%22:false,%22limitTypes%22:[%22file%22,%22video%22,%22document%22,%22image%22,%22audio%22,%22scorm%22,%22evercam%22,%22swf%22,%22wmpkg%22,%22link%22],%22fileType%22:%22all%22,%22parentId%22:0,%22sourceType%22:%22MyResourcesFile%22,%22no-intercept%22:true}&page="+str(page)+"&page_size="+str(numberOfRequest)
        try:
            self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}


    async def upload_file(self,file_path:str):
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
        except:
            return "unable to find file"
        
        metadata_url = "https://iclass.tku.edu.tw/api/uploads"

        headers_metadata = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://iclass.tku.edu.tw",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)..."
        }

        metadata_payload = {
            "name": file_name,
            "size": file_size,
            "parent_type": None,
            "parent_id": 0,
            "is_scorm": False,
            "is_wmpkg": False,
            "source": "",
            "is_marked_attachment": False,
            "embed_material_type": ""
        }
        response_metadata = self.session.post(
            metadata_url,
            headers=headers_metadata,
            data=json.dumps(metadata_payload)
        )

        if response_metadata.status_code != 201:
            print("❌ Failed to get upload URL")
            print(response_metadata.status_code, response_metadata.text)
            return {"error":f"Failed to get upload URL, status_code:{response_metadata.status_code}"}

        upload_info = response_metadata.json()
        upload_url = upload_info["upload_url"]
        upload_file_name = upload_info["name"]
        upload_file_id = upload_info["id"]
        upload_file_type = upload_info["type"]

        print(f"✅ Got upload URL:\n{upload_url}")

        with open(file_path, 'rb') as f:
            files = {
                'file': (upload_file_name, f, upload_file_type)
            }
            headers_upload = {
                "Origin": "https://iclass.tku.edu.tw",
                "Referer": "https://iclass.tku.edu.tw/",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)..."
            }

            upload_response = self.session.put(upload_url, files=files, headers=headers_upload)

            print(f"📤 Upload response: {upload_response.status_code}")
            print(upload_response.text)
            print(f"Upload file id {upload_file_id}")
        return upload_file_id
