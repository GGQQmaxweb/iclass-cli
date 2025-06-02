# iclass-cli

(WIP)View the to-do list, submit your homework, and achieve more in your terminal!

---

## Installation

### Prerequisites

- Python 3.10 or newer

### Environment variables set up

add `.env` to the project folder

```bash
USERNAMEID="YOURSTUDENTID"
PASSWORD="YOURSSOPASSWORD"
```

how to build to a exe

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller main.py --onefile --name iclassCLI --add-data '.env:.'
```

---

## UI version still on WIP
```bash
pip install -r requirements.txt
pip install windows-curses #Might need if you using windows
pip install pyinstaller
pyinstaller mainUI.py --onefile --name iclassCLIUI --add-data '.env:.'
```
