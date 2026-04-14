#include <stdio.h>
#include <stdlib.h>

#define MOUNT "/mnt"
#define MAX 512

int main(void)
 run_in_chroot(const char *cmd) {
    printf(" >> %s\n", cmd);
    if (system(cmd) != 0) {
        fprintf(stderr, "failed: %s\n", cmd);
    }
}

void chrun(const char *cmd) {
    char buf [MAX];
    snprintf(buf, sizeof(buf), "m") // finishing this later. This is so that the installer moves all necessary files from the ISO to the installed system, ex: kernel.
}

void chrun(const char *cmd) {
    char buf[MAX];
    snprintf(buf, sizeof(buf), "chroot" MOUNT " /bin/sh -c \"%s\"", cmd);
    run (buf);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "usage: stainless-backend <config>\n")
        return 1;
    }

    FILE *f = fopen(argv[1], "r");
    if (!f) {
        fprintf(stderr, "cannot open %s\n");
        return 1;
    }

    char pkgs[4096] = "";
    char timezone[64] = "UTC";
    char line[MAX];

    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = 0;
        char type[32], val[MAX];
        if (sscanf(line, "%31s %[^\n]", type, val) < 2) continue;

        if (strcmp(type, "package") == 0) {
            strcat(pkgs, val);
            strcat(pkgs, " ");
        } else if (strcmp(type, "timezone") == 0) {
            strncpy(timezone, val, sizeof(timezone) - 1);
        }
    }
    rewind(f);

    // fstab
    run("genfstab -U " MOUNT " >> " MOUNT "/etc/fstab");

    // timezone
    snprintf(cmd, sizeof(cmd),
        "ln -sf /usr/share/zoneinfo/%s /etc/localtime && hwclock --systohc", timezone);
    chrun(cmd);

    // locale
    chrun("echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen");
    chrun("echo 'LANG=en_US.UTF-8' > /etc/locale.conf");

    // users
    rewind(f);
    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = 0;
        char type[32], name[64], role[16], password[128];
        if (sscanf(line, "%31s %63s %15s %127s", type, name, role, password) < 4) continue;
        if (strcmp(type, "user") != 0) continue;

        snprintf(cmd, sizeof(cmd), "useradd -m %s", name);
        chrun(cmd);

        snprintf(cmd, sizeof(cmd), "echo '%s:%s' | chpasswd", name, password);
        chrun(cmd);

        if (strcmp(role, "root") == 0) {
            snprintf(cmd, sizeof(cmd), "usermod -aG wheel %s", name);
            chrun(cmd);
        }
    }

    // bootloader
    chrun("grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB");
    chrun("grub-mkconfig -o /boot/grub/grub.cfg");

    fclose(f);
    printf("\nInstallation complete.\n");
    return 0;
}