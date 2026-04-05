def write_config(selected, users, tz):
    with open("install.conf", "w") as f:
        f.write("packages=" + ",".join(sorted(selected)) + "\n")
        f.write("timezone=" + (tz[0] if tz else "") + "\n")
        for u in users:
            f.write(f"user={u['name']},root={'1' if u['root'] else '0'}\n")