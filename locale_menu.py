from ui import header, put, bar, W, N, H, G

LOCALES = [
    "en_US", "en_GB", "fi_FI", "sv_SE", "de_DE", "fr_FR",
    "es_ES", "it_IT", "pt_BR", "pt_PT", "nl_NL", "pl_PL",
    "ru_RU", "uk_UA", "cs_CZ", "sk_SK", "hu_HU", "ro_RO",
    "bg_BG", "hr_HR", "sr_RS", "sl_SI", "lt_LT", "lv_LV",
    "et_EE", "el_GR", "tr_TR", "ar_SA", "he_IL", "fa_IR",
    "zh_CN", "zh_TW", "ja_JP", "ko_KR", "th_TH", "vi_VN",
    "id_ID", "ms_MY", "hi_IN", "bn_IN", "ta_IN", "ur_PK",
    "af_ZA", "sw_KE", "zu_ZA", "is_IS", "nb_NO", "da_DK",
    "ca_ES", "eu_ES", "gl_ES", "cy_GB", "ga_IE", "mk_MK",
]

def do_locale(s, locale):
    chk = {LOCALES.index(locale[0].replace(".UTF-8", ""))} if locale else set()
    sel  = LOCALES.index(locale[0].replace(".UTF-8", "")) if locale else 0
    scroll = 0

    while True:
        import curses
        h, w = s.getmaxyx()
        rows = h - 6
        s.erase()
        header(s)
        put(s, 2, 2, "Select locale", W | curses.A_BOLD)
        put(s, 3, 0, "-" * (w - 1), N)

        for i in range(rows):
            idx = scroll + i
            if idx >= len(LOCALES): break
            mark = "[*] " if idx in chk else "[ ] "
            line = mark + LOCALES[idx] + ".UTF-8"
            if idx == sel:
                put(s, 4 + i, 0, (" " + line).ljust(w - 1), H)
            else:
                put(s, 4 + i, 2, line, G if idx in chk else W)

        bar(s, "↑up/down↓  enter/space=select  esc=back  (pick one)")
        s.refresh()
        k = s.getch()

        if k == curses.KEY_UP and sel > 0:
            sel -= 1
            if sel < scroll: scroll -= 1
        elif k == curses.KEY_DOWN and sel < len(LOCALES) - 1:
            sel += 1
            if sel >= scroll + rows: scroll += 1
        elif k in (ord(' '), 10, 13, curses.KEY_ENTER):
            chk = {sel}
            locale.clear()
            locale.append(LOCALES[sel] + ".UTF-8")
        elif k == 27:
            return