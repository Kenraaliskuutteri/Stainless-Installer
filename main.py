#!/usr/bin/env python3

import curses
import ctypes

_lib = None

def c_install_packages(packages):
    return 0

def c_begin_install():
    return 0


PACKAGE_GROUPS = {
    "Base System": [
        {"name": "base",           "desc": "Minimal base packages"},
        {"name": "base-devel",     "desc": "gcc, make, binutils..."},
        {"name": "linux",          "desc": "The Linux kernel"},
        {"name": "linux-firmware", "desc": "Firmware for common hardware"},
        {"name": "linux-headers",  "desc": "Kernel headers"},
    ],
    "Desktop Environment": [
        {"name": "xfce4",          "desc": "Lightweight XFCE"},
        {"name": "i3-wm",          "desc": "Tiling window manager"},
    ],
    "Network Tools": [
        {"name": "networkmanager", "desc": "Manages network connections"},
        {"name": "openssh",        "desc": "SSH client and server"},
        {"name": "wget",           "desc": "Download files from the web"},
        {"name": "curl",           "desc": "Transfer data via URL"},
        {"name": "nftables",       "desc": "Firewall / packet filter"},
    ],
    "Filesystem Tools": [
        {"name": "btrfs-progs",    "desc": "Btrfs utilities"},
        {"name": "e2fsprogs",      "desc": "ext2/3/4 tools"},
        {"name": "dosfstools",     "desc": "FAT filesystem tools"},
        {"name": "exfatprogs",     "desc": "exFAT support"},
    ],
    "Bootloader": [
        {"name": "grub",           "desc": "GNU GRUB bootloader"},
    ],
    "Multimedia": [
        {"name": "pipewire",       "desc": "Audio/video server"},
        {"name": "wireplumber",    "desc": "PipeWire session manager"},
        {"name": "ffmpeg",         "desc": "Audio and video tools"},
        {"name": "vlc",            "desc": "Media player"},
    ],
    "Browsers": [
        {"name": "firefox",    "desc": "An Open-source webbrowser"},
        {"name": "librewolf",    "desc": "An Privacy focused webbrowser based on Firefox"},
    ],
    "Tools": [
        {"name": "Kitty",    "desc": "A Lightweight terminal emulator"},
    ],
}

TOP_MENU = [
    {"label": "Select packages",    "action": "packages"},
    {"label": "Disk Partitioner", "action": "disk"},
    {"label": "Review and install", "action": "install"},
    {"label": "Quit",               "action": "quit"},
]

CP_NORMAL    = 1
CP_HIGHLIGHT = 2
CP_CYAN      = 3
CP_GREEN     = 4
CP_BAR       = 5


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(CP_NORMAL,    curses.COLOR_WHITE, -1)
    curses.init_pair(CP_HIGHLIGHT, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(CP_CYAN,      curses.COLOR_CYAN,  -1)
    curses.init_pair(CP_GREEN,     curses.COLOR_GREEN, -1)
    curses.init_pair(CP_BAR,       curses.COLOR_BLACK, curses.COLOR_CYAN)


def put(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0:
        return
    try:
        win.addstr(y, x, text[:max(0, w - x - 1)], attr)
    except curses.error:
        pass


def hline(win, y):
    h, w = win.getmaxyx()
    if 0 <= y < h:
        put(win, y, 0, "-" * (w - 1), curses.color_pair(CP_CYAN))


def header(stdscr):
    put(stdscr, 0, 2, "Welcome to the Stainless-Installer!                                                                                      Version 0.1                                                                                Latest version made on 1/4/26",
        curses.color_pair(CP_CYAN) | curses.A_BOLD)
    hline(stdscr, 1)


def status(stdscr, text):
    h, w = stdscr.getmaxyx()
    bar = (" " + text).ljust(w - 1)
    try:
        stdscr.addstr(h - 1, 0, bar[:w - 1], curses.color_pair(CP_BAR))
    except curses.error:
        pass


def list_menu(stdscr, title, items, descriptions=None,
              checked=None, toggle_mode=False):
    curses.curs_set(0)
    stdscr.keypad(True)

    local_checked = set(checked) if checked else set()
    selected = 0
    scroll   = 0

    while True:
        h, w = stdscr.getmaxyx()
        list_top  = 4
        list_rows = h - list_top - 2

        stdscr.erase()
        header(stdscr)
        put(stdscr, 2, 2, title, curses.color_pair(CP_NORMAL) | curses.A_BOLD)
        hline(stdscr, 3)

        for i in range(list_rows):
            idx = scroll + i
            if idx >= len(items):
                break

            y = list_top + i

            if toggle_mode:
                mark = "[*] " if idx in local_checked else "[ ] "
            else:
                mark = ""

            left = mark + items[idx]

            if idx == selected:
                line = (" " + left).ljust(w - 1)
                put(stdscr, y, 0, line,
                    curses.color_pair(CP_HIGHLIGHT) | curses.A_BOLD)
            else:
                put(stdscr, y, 2, left, curses.color_pair(CP_NORMAL))
                if descriptions and idx < len(descriptions) and descriptions[idx]:
                    right = descriptions[idx]
                    desc_x = min(w - len(right) - 3, 40)
                    if desc_x > len(left) + 6:
                        put(stdscr, y, desc_x, right,
                            curses.color_pair(CP_CYAN) | curses.A_DIM)

        if toggle_mode:
            status(stdscr,
                f"↑up/down↓  space/enter=toggle  esc=back"
                f"  ({len(local_checked)} selected)")
        else:
            status(stdscr, "↑up/down↓  ↳ enter=select  esc=back")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
            if selected < scroll:
                scroll -= 1

        elif key == curses.KEY_DOWN and selected < len(items) - 1:
            selected += 1
            if selected >= scroll + list_rows:
                scroll += 1

        elif key == curses.KEY_HOME:
            selected = 0
            scroll   = 0

        elif key == curses.KEY_END:
            selected = len(items) - 1
            scroll   = max(0, selected - list_rows + 1)

        elif key in (ord(' '), curses.KEY_ENTER, ord('\n'), ord('\r')) and toggle_mode:
            if selected in local_checked:
                local_checked.discard(selected)
            else:
                local_checked.add(selected)

        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            return selected

        elif key == 27:
            if toggle_mode and checked is not None:
                checked.clear()
                checked.update(local_checked)
            return -1


def screen_packages(stdscr, selected_packages):
    groups = list(PACKAGE_GROUPS.keys())

    while True:
        descs  = [f"{len(PACKAGE_GROUPS[g])} packages" for g in groups]
        choice = list_menu(stdscr, "Package groups", groups, descs)

        if choice == -1:
            return

        group_name = groups[choice]
        pkgs       = PACKAGE_GROUPS[group_name]
        pkg_names  = [p["name"] for p in pkgs]
        pkg_descs  = [p["desc"]  for p in pkgs]

        checked_idx = {
            i for i, n in enumerate(pkg_names) if n in selected_packages
        }

        list_menu(stdscr, group_name, pkg_names, pkg_descs,
                  checked=checked_idx, toggle_mode=True)

        for i, name in enumerate(pkg_names):
            if i in checked_idx:
                selected_packages.add(name)
            else:
                selected_packages.discard(name)


def screen_install(stdscr, selected_packages):
    h, w = stdscr.getmaxyx()

    if not selected_packages:
        dh, dw = 7, 50
        dy = (h - dh) // 2
        dx = (w - dw) // 2
        win = curses.newwin(dh, dw, dy, dx)
        win.box()
        put(win, 0, 2, " notice ", curses.color_pair(CP_CYAN) | curses.A_BOLD)
        put(win, 2, 2, "No packages selected.",      curses.color_pair(CP_NORMAL))
        put(win, 3, 2, "Go back and pick something.", curses.color_pair(CP_NORMAL))
        put(win, 5, 2, "press any key...",            curses.color_pair(CP_CYAN) | curses.A_DIM)
        win.refresh()
        stdscr.getch()
        return

    pkg_list  = sorted(selected_packages)
    all_items = ["  " + p for p in pkg_list] + ["", "  -> begin installation"]

    while True:
        choice = list_menu(
            stdscr,
            f"Ready to install  ({len(pkg_list)} packages)",
            all_items,
        )

        if choice == -1:
            return

        if choice == len(pkg_list) + 1:
            run_install(stdscr, pkg_list)
            return


def run_install(stdscr, packages):
    h, w = stdscr.getmaxyx()
    stdscr.erase()
    header(stdscr)
    put(stdscr, 2, 2, "Installing packages...",
        curses.color_pair(CP_NORMAL) | curses.A_BOLD)
    hline(stdscr, 3)
    stdscr.refresh()

    for i, pkg in enumerate(packages):
        row = 4 + i
        if row >= h - 2:
            break

        put(stdscr, row, 4, pkg, curses.color_pair(CP_NORMAL) | curses.A_DIM)
        stdscr.refresh()
        curses.napms(80)

        # ret = c_install_packages([pkg])

        put(stdscr, row, 2, "ok", curses.color_pair(CP_GREEN) | curses.A_BOLD)
        stdscr.refresh()

    done_row = min(4 + len(packages) + 1, h - 2)
    put(stdscr, done_row, 2, "Done.  Press any key to continue.",
        curses.color_pair(CP_CYAN) | curses.A_BOLD)
    stdscr.refresh()
    stdscr.getch()


def confirm_quit(stdscr):
    h, w = stdscr.getmaxyx()
    dh, dw = 6, 42
    dy = (h - dh) // 2
    dx = (w - dw) // 2
    win = curses.newwin(dh, dw, dy, dx)
    win.box()
    put(win, 0, 2, " quit? ", curses.color_pair(CP_CYAN) | curses.A_BOLD)
    put(win, 2, 2, "Nothing has been written to disk.", curses.color_pair(CP_NORMAL))
    put(win, 4, 2, "y = yes   n / esc = go back",
        curses.color_pair(CP_NORMAL) | curses.A_DIM)
    win.refresh()
    while True:
        key = stdscr.getch()
        if key in (ord('y'), ord('Y')):
            return True
        if key in (ord('n'), ord('N'), 27):
            return False


def main_menu(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.keypad(True)

    selected_packages = set()

    while True:
        labels = [m["label"] for m in TOP_MENU]
        descs  = [
            f"{len(selected_packages)} packages selected",
            "Partition your disk",
            "Review your selection and start the install",
            "Exit without doing anything",
        ]

        choice = list_menu(stdscr, "Main menu", labels, descs)

        if choice == -1:
            continue

        action = TOP_MENU[choice]["action"]

        if action == "packages":
            screen_packages(stdscr, selected_packages)
        elif action == "disk":
            screen_packages(stdscr, selected_packages)
        elif action == "install":
            screen_install(stdscr, selected_packages)
        elif action == "quit":
            if confirm_quit(stdscr):
                break


def main():
    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt:
        pass
    print("\nStainless-Installer exited.\n")


if __name__ == "__main__":
    main()