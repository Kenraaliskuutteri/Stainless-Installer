from ui import menu, yesno, header, input_box, notice
import curses, re


TIMEZONES = [
    "UTC-12",
    "UTC-11",
    "UTC-10",
    "UTC-9",
    "UTC-8",
    "UTC-7",
    "UTC-6",
    "UTC-5",
    "UTC-4",
    "UTC-3",
    "UTC-2",
    "UTC-1",
    "UTC+0",
    "UTC+1",
    "UTC+2",
    "UTC+3",
    "UTC+4",
    "UTC+5",
    "UTC+5:30",
    "UTC+6",
    "UTC+7",
    "UTC+8",
    "UTC+9",
    "UTC+10",
    "UTC+11",
    "UTC+12",
]
# I am sure that this should be pretty self explained. If you are going to contribute and add forexample countries to the next of the timezone. Do: "UTC+(time), (country)"

W = N = H = G = Y = B = 0


def colors():
    global W, N, H, G, Y, B
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(5, curses.COLOR_YELLOW, -1)
    curses.init_pair(6, curses.COLOR_RED, -1)
    W = curses.color_pair(1)
    H = curses.color_pair(2) | curses.A_BOLD
    N = curses.color_pair(3)
    G = curses.color_pair(4)
    Y = curses.color_pair(5)
    B = curses.color_pair(6)


def put(w, y, x, t, a=0):
    mh, mw = w.getmaxyx()
    if 0 <= y < mh and 0 <= x < mw:
        try:
            w.addstr(y, x, t[: mw - x - 1], a)
        except curses.error:
            pass


def bar(s, txt):
    h, w = s.getmaxyx()
    try:
        s.addstr(h - 1, 0, (" " + txt).ljust(w - 1)[: w - 1], curses.color_pair(2))
    except curses.error:
        pass

def do_timezone(s, tz):
    chk = {TIMEZONES.index(tz[0])} if tz else set()
    sel, scroll = (TIMEZONES.index(tz[0]) if tz else 0), 0

    while True:
        h, w = s.getmaxyx()
        rows = h - 6
        s.erase()
        header(s)
        put(s, 2, 2, "Select timezone", W | curses.A_BOLD)
        put(s, 3, 0, "-" * (w - 1), N)

        for i in range(rows):
            idx = scroll + i
            if idx >= len(TIMEZONES):
                break
            mark = "[*] " if idx in chk else "[ ] "
            line = mark + TIMEZONES[idx]
            if idx == sel:
                put(s, 4 + i, 0, (" " + line).ljust(w - 1), H)
            else:
                put(s, 4 + i, 2, line, G if idx in chk else W)

        bar(s, "↑up/down↓  ↳ enter=select  esc=back  (1 max)")
        s.refresh()
        k = s.getch()

        if k == curses.KEY_UP and sel > 0:
            sel -= 1
            if sel < scroll:
                scroll -= 1
        elif k == curses.KEY_DOWN and sel < len(TIMEZONES) - 1:
            sel += 1
            if sel >= scroll + rows:
                scroll += 1
        elif k in (ord(" "), 10, 13, curses.KEY_ENTER):
            chk = {sel}
            tz.clear()
            tz.append(TIMEZONES[sel])
        elif k == 27:
            return