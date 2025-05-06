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
    #auth = Authenticator()
    #session = auth.perform_auth()
    #api = TronClassAPI(session)
    
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
                await getMyToDoList(api)
                pass
            elif(selected_idx==1):
                await mycurses(api)
                pass
            elif(selected_idx==2):
                pass

    pass

if __name__ == '__main__':
    curses.wrapper(lambda stdscr: asyncio.run(curses_main(stdscr)))