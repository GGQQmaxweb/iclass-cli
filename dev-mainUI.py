# mainUI.py
import asyncio
import curses
from api.auth_module import Authenticator
from api.iclass_api import TronClassAPI

def draw_menu(stdscr, selected_idx, options, title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, w//2 - len(title)//2, title, curses.A_BOLD | curses.A_UNDERLINE)

    for idx, option in enumerate(options):
        x = w // 2 - 30
        y = 3 + idx
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, option)
    stdscr.refresh()

async def curses_main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    stdscr.addstr(0, 0, "🔐 Logging in...", curses.A_BOLD)
    stdscr.refresh()
    #handle api
    auth = Authenticator()
    session = auth.perform_auth()
    api = TronClassAPI(session)
    
    selected_idx = 0
    menu_options = ["To Do List","My Class","My Files"]
    while True:
        draw_menu(stdscr, selected_idx, menu_options + ["Exit"], "Select a Option")
        
        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(menu_options):
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n')]:
            if selected_idx == len(menu_options):
                break
            if(selected_idx==0):
                await getMyToDoList(stdscr,api)
                pass
            elif(selected_idx==1):
                await mycurses(stdscr,api)
                pass
            elif(selected_idx==2):

                pass

    pass
async def mycurses(stdscr,api):
    result = await api.get_courses()
    courses = result.get("courses", [])
    course_options = [f"{c['id']} - {c['name']}" for c in courses]

    selected_idx = 0
    while True:
        draw_menu(stdscr, selected_idx, course_options + ["Exit"], "🎓 Select a Course")
        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(course_options):
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n')]:
            if selected_idx == len(course_options):
                break
            selected_course = courses[selected_idx]
            await handle_course_actions(stdscr, api, selected_course["id"])

async def handle_course_actions(stdscr, api, course_id):
    result = await api.get_activities(course_id)
    mystr = result["activities"]
    activities = []
    selected = 0

    while True:
        draw_menu(stdscr, selected, activities, f"Course ID: {course_id} - Actions")
        key = stdscr.getch()
        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(activities) - 1:
            selected += 1
        elif key in [curses.KEY_ENTER, ord("\n")]:
            action = activities[selected]
            
            if action == "Back":
                break

if __name__ == '__main__':
    curses.wrapper(lambda stdscr: asyncio.run(curses_main(stdscr)))