#!/usr/bin/env python3
from ui import colors, menu, yesno, notice, header, put, bar, W, N, G, Y, B
from users import do_users
from package import do_packages
from timezone import do_timezone
from config import write_config
import os, curses, re

os.environ.setdefault("ESCDELAY", "10")
# ^^^ Unless you, contributor. Know a better way to fix the esc key delay, please do not change this. It is set to 10ms to make the UI more responsive. If you set it to 0 or a very low value, it might cause issues with certain terminals where the escape key is used as a prefix for other keys (like arrow keys). Setting it to 10ms is a good balance that should work well in most cases. - Kenraali

MENU = [
    ("packages", "Select packages"),
    ("users", "Manage users"),
    ("timezone", "Select timezone"),
    ("install", "Review and install"),
    ("quit", "Quit"),
]
# Adding just a menu here won't give you much else than a option inside of the main menu. Won't send you anywhere if you don't also make it function.


def do_install(s, selected):
    if not selected:
        notice(
            s,
            [
                "No packages selected.",
                "Go back and pick something.",
                "",
                "press any key...",
            ],
        )
        return
    pkgs = sorted(selected)
    items = ["  " + p for p in pkgs] + ["", "  -> begin installation"]
    while True:
        choice = menu(s, f"Ready to install  ({len(pkgs)} packages)", items)
        if choice == -1:
            return
        if choice == len(pkgs) + 1:
            run_install(s, pkgs)
            return


def run_install(s, pkgs, users, tz):
    write_config(pkgs, users, tz)
    h, _ = s.getmaxyx()
    s.erase()
    header(s)
    put(s, 2, 2, "Installing...", W | curses.A_BOLD)
    put(s, 3, 0, "-" * (_ - 1), N)
    s.refresh()
    for i, p in enumerate(pkgs):
        row = 4 + i
        if row >= h - 2:
            break
        put(s, row, 4, p, W | curses.A_DIM)
        s.refresh()
        curses.napms(80)
        put(s, row, 2, "ok", G | curses.A_BOLD)
        s.refresh()
    put(s, min(4 + len(pkgs) + 1, h - 2), 2, "Done.  Press any key.", N | curses.A_BOLD)
    s.refresh()
    s.getch()


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
        if choice == -1:
            continue
        action = MENU[choice][0]
        if action == "packages":
            do_packages(s, selected)
        elif action == "users":
            do_users(s, users)
        elif action == "timezone":
            do_timezone(s, tz)
        elif action == "install":
            do_install(s, selected)
        elif action == "quit":
            if yesno(s, "Quit? Nothing has been written to disk."):
                break


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass
print("\nStainless-Installer exited. No changes made.\n")