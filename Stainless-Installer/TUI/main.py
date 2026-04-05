#!/usr/bin/env python3
from config import write_config
import os, curses, re
os.environ.setdefault("ESCDELAY", "10")

PACKAGES = {
    "Base System":        ["base", "base-devel", "linux", "linux-firmware", "linux-headers"],
    "Desktop":            ["xfce4", "i3-wm"],
    "Network":            ["networkmanager", "openssh", "wget", "curl", "nftables", "connman"],
    "Filesystem Tools":   ["btrfs-progs", "e2fsprogs", "dosfstools", "exfatprogs"],
    "Bootloader":         ["grub"],
    "Multimedia":         ["pipewire", "wireplumber", "ffmpeg", "vlc"],
    "Browsers":           ["firefox", "librewolf"],
    "Tools":              ["emacs", "vim", "vscodium"],
}

TIMEZONES = [
    "UTC-12", "UTC-11", "UTC-10", "UTC-9",  "UTC-8",  "UTC-7",  "UTC-6",
    "UTC-5",  "UTC-4",  "UTC-3",  "UTC-2",  "UTC-1",  "UTC+0",  "UTC+1",
    "UTC+2",  "UTC+3",  "UTC+4",  "UTC+5",  "UTC+5:30","UTC+6", "UTC+7",
    "UTC+8",  "UTC+9",  "UTC+10", "UTC+11", "UTC+12",
]

MENU = [
    ("packages",  "Select packages"),
    ("users",     "Manage users"),
    ("timezone",  "Select timezone"),
    ("install",   "Review and install"),
    ("quit",      "Quit"),
]

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

        hint = "↑up/down↓  ↳ enter=select  esc=back  (1 max)" if toggle else "↑up/down↓  ↳ enter=select  esc=back"
        bar(s, hint)
        s.refresh()
        k = s.getch()

        if k == curses.KEY_UP and sel > 0:
            sel -= 1
            if sel < scroll: scroll -= 1
        elif k == curses.KEY_DOWN and sel < len(items) - 1:
            sel += 1
            if sel >= scroll + rows: scroll += 1
        elif k == curses.KEY_HOME:
            sel = scroll = 0
        elif k == curses.KEY_END:
            sel = len(items) - 1
            scroll = max(0, sel - rows + 1)
        elif k in (ord(' '), 10, 13, curses.KEY_ENTER) and toggle:
            if sel in chk: chk.discard(sel)
            else: chk.add(sel)
            if checked is not None:
                checked.clear(); checked.update(chk)
        elif k in (10, 13, curses.KEY_ENTER):
            return sel
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


def do_packages(s, selected):
    groups = list(PACKAGES.keys())
    while True:
        choice = menu(s, "Package groups", groups, [f"{len(PACKAGES[g])} packages" for g in groups])
        if choice == -1: return
        g = groups[choice]
        pkgs = PACKAGES[g]
        chk = {i for i, p in enumerate(pkgs) if p in selected}
        menu(s, g, pkgs, toggle=True, checked=chk)
        for i, p in enumerate(pkgs):
            if i in chk: selected.add(p)
            else: selected.discard(p)


def do_users(s, users):
    while True:
        items = [f"{'[root]' if u['root'] else '      '}  {u['name']}" for u in users] + ["  + add user"]
        descs = ["password set" if u["password"] else "no password" for u in users] + [""]
        choice = menu(s, "User accounts", items, descs)
        if choice == -1: return
        if choice == len(users): add_user(s, users)
        else: edit_user(s, users, choice)


def add_user(s, users):
    name = input_box(s, "Username:")
    if not name: return
    if not re.match(r'^[a-z_][a-z0-9_-]*$', name):
        notice(s, ["Invalid username.", "Use lowercase letters, digits, _ or -", "", "press any key..."], B); return
    if any(u["name"] == name for u in users):
        notice(s, [f"'{name}' already exists.", "", "press any key..."], B); return
    pw1 = input_box(s, f"Password for {name}:", secret=True)
    if pw1 is None: return
    pw2 = input_box(s, "Confirm password:", secret=True)
    if pw2 is None: return
    if pw1 != pw2:
        notice(s, ["Passwords do not match.", "", "press any key..."], B); return
    root = yesno(s, f"Give {name} sudo / root access?")
    users.append({"name": name, "password": pw1, "root": root})


def edit_user(s, users, idx):
    u = users[idx]
    choice = menu(s, f"Edit: {u['name']}", ["Change password", "Toggle root", "Delete user"])
    if choice == -1: return
    if choice == 0:
        pw1 = input_box(s, "New password:", secret=True)
        if pw1 is None: return
        pw2 = input_box(s, "Confirm password:", secret=True)
        if pw2 is None: return
        if pw1 != pw2: notice(s, ["Passwords do not match.", "", "press any key..."], B); return
        u["password"] = pw1
    elif choice == 1:
        u["root"] = not u["root"]
    elif choice == 2:
        if yesno(s, f"Delete '{u['name']}'?"): users.pop(idx)


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
            if idx >= len(TIMEZONES): break
            mark = "[*] " if idx in chk else "[ ] "
            line = mark + TIMEZONES[idx]
            if idx == sel:
                put(s, 4 + i, 0, (" " + line).ljust(w - 1), H)
            else:
                put(s, 4 + i, 2, line, G if idx in chk else W)

        bar(s, "up/down  enter/space=select  esc=back  (pick one)")
        s.refresh()
        k = s.getch()

        if k == curses.KEY_UP and sel > 0:
            sel -= 1
            if sel < scroll: scroll -= 1
        elif k == curses.KEY_DOWN and sel < len(TIMEZONES) - 1:
            sel += 1
            if sel >= scroll + rows: scroll += 1
        elif k in (ord(' '), 10, 13, curses.KEY_ENTER):
            chk = {sel}
            tz.clear()
            tz.append(TIMEZONES[sel])
        elif k == 27:
            return


def do_install(s, selected):
    if not selected:
        notice(s, ["No packages selected.", "Go back and pick something.", "", "press any key..."]); return
    pkgs = sorted(selected)
    items = ["  " + p for p in pkgs] + ["", "  -> begin installation"]
    while True:
        choice = menu(s, f"Ready to install  ({len(pkgs)} packages)", items)
        if choice == -1: return
        if choice == len(pkgs) + 1:
            run_install(s, pkgs); return


def run_install(s, pkgs, users, tz):
    write_config(pkgs, users, tz)
    h, _ = s.getmaxyx()
    s.erase(); header(s)
    put(s, 2, 2, "Installing...", W | curses.A_BOLD)
    put(s, 3, 0, "-" * (_ - 1), N)
    s.refresh()
    for i, p in enumerate(pkgs):
        row = 4 + i
        if row >= h - 2: break
        put(s, row, 4, p, W | curses.A_DIM); s.refresh()
        curses.napms(80)
        put(s, row, 2, "ok", G | curses.A_BOLD); s.refresh()
    put(s, min(4 + len(pkgs) + 1, h - 2), 2, "Done.  Press any key.", N | curses.A_BOLD)
    s.refresh(); s.getch()


def main(s):
    colors()
    curses.curs_set(0)
    selected, users, tz = set(), [], []

    while True:
        descs = [
            f"{len(selected)} packages selected",
            ", ".join(u["name"] for u in users) or "no users added",
            tz[0] if tz else "not set",
            "Review and start the install",
            "Exit",
        ]
        choice = menu(s, "Main menu", [m[1] for m in MENU], descs)
        if choice == -1: continue
        action = MENU[choice][0]
        if action == "packages":   do_packages(s, selected)
        elif action == "users":    do_users(s, users)
        elif action == "timezone": do_timezone(s, tz)
        elif action == "install":  do_install(s, selected)
        elif action == "quit":
            if yesno(s, "Quit? Nothing has been written to disk."): break


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass
print("\nStainless-Installer exited.\n")
