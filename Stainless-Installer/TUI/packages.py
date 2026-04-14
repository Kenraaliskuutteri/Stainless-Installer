from main import menu

PACKAGES = {
    "Base System": ["base", "base-devel", "linux", "linux-firmware", "linux-headers"],
    "Desktop": ["xfce4", "i3-wm"],
    "Network": ["networkmanager", "openssh", "wget", "curl", "nftables", "connman"],
    "Filesystem Tools": ["btrfs-progs", "e2fsprogs", "dosfstools", "exfatprogs"],
    "Bootloader": ["grub"],
    "Multimedia": ["pipewire", "wireplumber", "ffmpeg", "vlc"],
    "Browsers": ["firefox", "librewolf"],
    "Tools": ["emacs", "vim", "vscodium", "git"],
}

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