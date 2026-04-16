import curses

W = N = H = G = Y = B = 0

def colors():
    global W, N, H, G, Y, B
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE,  -1)
    curses.init_pair(2, curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_CYAN,   -1)
    curses.init_pair(4, curses.COLOR_GREEN,  -1)
    curses.init_pair(5, curses.COLOR_YELLOW, -1)
    curses.init_pair(6, curses.COLOR_RED,    -1)
    W = curses.color_pair(1)
    H = curses.color_pair(2) | curses.A_BOLD
    N = curses.color_pair(3)
    G = curses.color_pair(4)
    Y = curses.color_pair(5)
    B = curses.color_pair(6)

def put(w, y, x, t, a=0):
    mh, mw = w.getmaxyx()
    if 0 <= y < mh and 0 <= x < mw:
        try: w.addstr(y, x, t[:mw - x - 1], a)
        except curses.error: pass

def bar(s, txt):
    h, w = s.getmaxyx()
    try: s.addstr(h-1, 0, (" " + txt).ljust(w-1)[:w-1], curses.color_pair(2))
    except curses.error: pass

def header(s):
    _, w = s.getmaxyx()
    put(s, 0, 2, "Stainless-Installer", N | curses.A_BOLD)
    put(s, 0, w - 12, "v0.1  1/4/26", N)
    put(s, 1, 0, "-" * (w - 1), N)

def menu(s, title, items, descs=None, toggle=False, checked=None):
    curses.curs_set(0)
    s.keypad(True)
    sel, scroll = 0, 0
    chk = set(checked) if checked else set()
    while True:
        h, w = s.getmaxyx()
        rows = h - 6
        s.erase()
        header(s)
        put(s, 2, 2, title, W | curses.A_BOLD)
        put(s, 3, 0, "-" * (w - 1), N)
        for i in range(rows):
            idx = scroll + i
            if idx >= len(items): break
            y = 4 + i
            mark = ("[*] " if idx in chk else "[ ] ") if toggle else ""
            line = mark + items[idx]
            if idx == sel:
                put(s, y, 0, (" " + line).ljust(w - 1), H)
            else:
                put(s, y, 2, line, G if (toggle and idx in chk) else W)
                if descs and idx < len(descs) and descs[idx]:
                    dx = min(w - len(descs[idx]) - 3, 40)
                    if dx > len(line) + 6:
                        put(s, y, dx, descs[idx], N | curses.A_DIM)
        hint = "↑up/down↓  space/enter=toggle  esc=back" if toggle else "↑up/down↓  ↳ enter=select  esc=back"
        bar(s, hint)
        s.refresh()
        k = s.getch()
        if k == curses.KEY_UP and sel > 0:
            sel -= 1
            if sel < scroll: scroll -= 1
        elif k == curses.KEY_DOWN and sel < len(items) - 1:
            sel += 1
            if sel >= scroll + rows: scroll += 1
        elif k == curses.KEY_HOME: sel = scroll = 0
        elif k == curses.KEY_END:
            sel = len(items) - 1
            scroll = max(0, sel - rows + 1)
        elif k in (ord(' '), 10, 13, curses.KEY_ENTER) and toggle:
            if sel in chk: chk.discard(sel)
            else: chk.add(sel)
            if checked is not None:
                checked.clear(); checked.update(chk)
        elif k in (10, 13, curses.KEY_ENTER): return sel
        elif k == 27:
            if toggle and checked is not None:
                checked.clear(); checked.update(chk)
            return -1

def input_box(s, prompt, secret=False):
    h, w = s.getmaxyx()
    dw = min(w - 4, 60)
    win = curses.newwin(5, dw, (h - 5) // 2, (w - dw) // 2)
    win.keypad(True)
    val = []
    while True:
        win.erase(); win.box()
        put(win, 0, 2, " input ", N | curses.A_BOLD)
        put(win, 2, 2, prompt, W | curses.A_BOLD)
        put(win, 3, 2, ("*" * len(val) if secret else "".join(val)) + " ", Y)
        win.refresh()
        curses.curs_set(1)
        k = win.getch()
        curses.curs_set(0)
        if k in (10, 13, curses.KEY_ENTER): return "".join(val)
        elif k == 27: return None
        elif k in (curses.KEY_BACKSPACE, 127, 8):
            if val: val.pop()
        elif 32 <= k <= 126: val.append(chr(k))

def yesno(s, question):
    h, w = s.getmaxyx()
    dw = min(w - 4, max(len(question) + 8, 36))
    win = curses.newwin(5, dw, (h - 5) // 2, (w - dw) // 2)
    win.box()
    put(win, 0, 2, " confirm ", N | curses.A_BOLD)
    put(win, 2, 2, question, W)
    put(win, 3, 2, "y = yes   n / esc = no", W | curses.A_DIM)
    win.refresh()
    while True:
        k = s.getch()
        if k in (ord('y'), ord('Y')): return True
        if k in (ord('n'), ord('N'), 27): return False

def notice(s, lines, color=None):
    h, w = s.getmaxyx()
    dw = min(w - 4, max((len(l) for l in lines), default=20) + 6)
    win = curses.newwin(len(lines) + 4, dw, (h - len(lines) - 4) // 2, (w - dw) // 2)
    win.box()
    put(win, 0, 2, " notice ", N | curses.A_BOLD)
    for i, l in enumerate(lines):
        put(win, i + 2, 2, l, color or W)
    win.refresh()
    s.getch()