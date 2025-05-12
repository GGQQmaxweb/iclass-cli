# main.py
import asyncio
from api.auth_module import Authenticator
from api.iclass_api import TronClassAPI
from api.ilife_api import IifeAPI
from texttable import Texttable
from bs4 import BeautifulSoup

async def main():
    print("🔐 Logging in...")
    auth = Authenticator()
    session = auth.perform_auth()

    api = TronClassAPI(session)

    while True:
        print("\n📚 iClass TKU API Menu")
        print("1. Get Todos")
        print("2. Get Bulletins")
        print("3. Get Courses")
        print("4. Get Activities")
        print("5. Upload File")
        print("6. Download File")
        print("7. Submit Homework")
        print("8. Exit")

        choice = input("Select an option (1-7): ")

        if choice == "1":
            result = await api.get_todos()
            formatText = str(result).replace(',', ',\n') 
            print("\n✅ Todos:")
            print(formatText)

        elif choice == "2":
            result = await api.get_bulletins()
            t = Texttable()
            t.set_cols_width([25, 15, 25, 60,10])
            # Add header row
            t.add_row(['Title', 'CreatedBy','Created At','Content',"files"])

            # Filter data and add to table
            for bulletin in result['bulletins']:
                title = bulletin.get('title', '')
                created_by_name = bulletin['created_by'].get('name', '')
                html_content = bulletin.get('content', '')
                created_at = bulletin.get('created_at', '')    
                soup = BeautifulSoup(html_content, 'html.parser')
                content = soup.get_text(separator='\n')
                
                #This is for Big-5 font size is lager then other english text 
                if len(title) > (25 / 2):
                    title = title[:int(25/2)] + "\n" + title[int(25/2):]
                contentList = content.split("\n")
                contentText = ""
                for text in contentList:
                    if len(text) > (60 / 2):
                        text = text[:int(60/2)] + "\n" + text[int(60/2):]
                    contentText+=text+"\n"
                
                #get the file_reference_id
                file_references = []
                uploads = bulletin.get('uploads')
                for fileMetaData in uploads:
                    file_references.append(fileMetaData['reference_id'])
                t.add_row([title, created_by_name,created_at,contentText,file_references])
            print("\n📢 Bulletins:")
            print(t.draw())

        elif choice == "3":
            result = await api.get_courses()
            print("\n🎓 Courses:")
            table = Texttable()
            table.header(['ID', '名稱', '學分', '教師'])

            # Loop through the courses and extract the needed fields
            for course in result.get('courses', []):
                course_id = course.get('id')
                course_name = course.get('name')
                credit = course.get('credit')
                instructors = ', '.join(instr.get('name') for instr in course.get('instructors', []))
                table.add_row([course_id, course_name, credit, instructors])
            print(table.draw())

        elif choice == "4":
            course_id = input("Enter the course ID: ").strip()
            response = await api.get_activities(course_id)
            table = Texttable()
            table.set_cols_align(["l", "l", "l", "l", "l", "l"])
            table.set_cols_width([10, 10, 20, 20, 10, 60])  # Adjust column widths for better wrapping
            table.header(["ID", "Type", "Deadline", "File Name", "File ID", "Description"])

            for activity in response["activities"]:
                raw_description = activity["data"].get("description", "")
                soup = BeautifulSoup(raw_description, 'html.parser')
                description = soup.get_text(separator='\n').strip()

                # Optionally wrap long lines for better fit in table
                wrapped_description = ""
                for line in description.splitlines():
                    while len(line) > 60:
                        wrapped_description += line[:60] + "\n"
                        line = line[60:]
                    wrapped_description += line + "\n"
                wrapped_description = wrapped_description.strip()

                deadline = activity.get("deadline", "")
                activity_id = activity.get("id", "")
                activity_type = activity.get("type", "")

                uploads = activity.get("uploads", [])
                if uploads:
                    for upload in uploads:
                        upload_name = upload.get("name", "")
                        upload_ref_id = upload.get("reference_id", "")
                        table.add_row([
                            activity_id, activity_type, deadline,
                            upload_name, upload_ref_id, wrapped_description
                        ])
                else:
                    table.add_row([
                        activity_id, activity_type, deadline,
                        "", "", wrapped_description
                    ])

            print(table.draw())
        elif choice == "5":
            file_paths = input("Enter the file path to upload: ").split(",")
            upload_ids = []
            for filePath in file_paths:
                print(f"📁Uploading {filePath.strip()}")
                upload_id = await api.upload_file(filePath.strip())
                upload_ids.append(upload_id)
            print(f"\n📁 Uploaded file ID: {upload_ids}")

        elif choice == "6":
            file_references_id = input("Enter the file id to download: ").strip()
            fileName = await api.download(file_references_id)
            print(f"\n📁 Saved as {fileName}")

        elif choice == "7":
            try:
                activity_id = int(input("Enter activity ID: "))
                upload_ids = input("Enter upload file IDs (comma-separated): ")
                upload_ids = [int(i.strip()) for i in upload_ids.split(",") if i.strip()]
                result = await api.submit_homework(activity_id, upload_ids)
                print("\n📨 Submission Result:")
                print(result)
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
        elif choice == "file":
            try:
                print("My files")
                page = input("page")
                numOf = input("numOf")
                result = await api.get_my_files(numOf,page)
                print(result)
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
        elif choice == "dla":
            downloadIdList = []
            try:
                course_id = input("Enter the course ID: ").strip()
                response = await api.get_activities(course_id)
                for activity in response["activities"]:
                    uploads = activity.get("uploads", [])
                    if uploads:
                        for upload in uploads:
                            upload_name = upload.get("name", "")
                            upload_ref_id = upload.get("reference_id", "")
                            downloadIdList.append(upload_ref_id)
            except:
                print("Error")
            print("Start Downloading File",downloadIdList)
            for file in downloadIdList:
                fileName = await api.download(file)
                print(f"\n📁 Saved as {fileName}")

        elif choice == "class":
            classApi = IifeAPI()
            try:
                await classApi.displayStuClass()
            except:
                print("Do you enter genkey?")
        elif choice == "8" or "exit":
            print("👋 Exiting...")
            break

        else:
            print("❌ Invalid option.")

if __name__ == '__main__':
    asyncio.run(main())
