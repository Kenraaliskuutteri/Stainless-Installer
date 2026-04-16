import re
from ui import menu, yesno, header, input_box, notice, B

def do_users(s, users):
    while True:
        items = [
            f"{'[root]' if u['root'] else '      '}  {u['name']}" for u in users
        ] + ["  + add user"]
        descs = ["password set" if u["password"] else "no password" for u in users] + [
            ""
        ]
        choice = menu(s, "User accounts", items, descs)
        if choice == -1:
            return
        if choice == len(users):
            add_user(s, users)
        else:
            edit_user(s, users, choice)


def add_user(s, users):
    name = input_box(s, "Username:")
    if not name:
        return
    if not re.match(r"^[a-z_][a-z0-9_-]*$", name):
        notice(
            s,
            [
                "Invalid username.",
                "Use lowercase letters, digits, _ or -",
                "",
                "press any key...",
            ],
            B,
        )
        return
    if any(u["name"] == name for u in users):
        notice(s, [f"'{name}' already exists.", "", "press any key..."], B)
        return
    pw1 = input_box(s, f"Password for {name}:", secret=True)
    if pw1 is None:
        return
    pw2 = input_box(s, "Confirm password:", secret=True)
    if pw2 is None:
        return
    if pw1 != pw2:
        notice(s, ["Passwords do not match.", "", "press any key..."], B)
        return
    root = yesno(s, f"Give {name} sudo / root access?")
    users.append({"name": name, "password": pw1, "root": root})


def edit_user(s, users, idx):
    u = users[idx]
    choice = menu(
        s, f"Edit: {u['name']}", ["Change password", "Toggle root", "Delete user"]
    )
    if choice == -1:
        return
    if choice == 0:
        pw1 = input_box(s, "New password:", secret=True)
        if pw1 is None:
            return
        pw2 = input_box(s, "Confirm password:", secret=True)
        if pw2 is None:
            return
        if pw1 != pw2:
            notice(s, ["Passwords do not match.", "", "press any key..."], B)
            return
        u["password"] = pw1
    elif choice == 1:
        u["root"] = not u["root"]
    elif choice == 2:
        if yesno(s, f"Delete '{u['name']}'?"):
            users.pop(idx)