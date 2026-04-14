from main import menu, yesno, header, input_box, notice
import curses, re

# Color pair constants
W = curses.COLOR_WHITE
N = curses.COLOR_WHITE
H = curses.A_REVERSE
G = curses.COLOR_GREEN

def header(s):
    """Display header at the top of the screen."""
    pass

def put(s, y, x, text, attr=0):
    """Put text at position (y, x) with given attributes."""
    try:
        s.addstr(y, x, text, attr)
    except curses.error:
        pass

def bar(s, text):
    """Display a status bar at the bottom of the screen."""
    h, w = s.getmaxyx()
    try:
        s.addstr(h - 1, 0, text.ljust(w - 1), curses.A_REVERSE)
    except curses.error:
        pass



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