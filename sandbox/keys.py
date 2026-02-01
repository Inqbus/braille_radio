#!/usr/bin/env python3
import curses
import time


def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(False)
    stdscr.keypad(True)  # Enable F1-F12, arrows
    stdscr.clear()

    # Title
    stdscr.addstr(0, 0, "=== KEY PRESS DETECTOR (q=quit) ===", curses.A_BOLD)
    stdscr.addstr(2, 0, "Press any key (F1-F12, arrows, ESC, ALT+keys)...")

    # Key history area
    stdscr.addstr(4, 0, "Last keys: ")

    while True:
        key = stdscr.getkey()
        stdscr.addstr(10, 0, f"Last keys: {key}")
        # handle meta key
        if key == '\x1b':
            # Distinguish between ESC and ALT + key
            # If ESC then the next char is "\1b"
            stdscr.nodelay(True)
            next_key = stdscr.getch()
            stdscr.nodelay(False)
        #     if next_key == '\x1b' or next_key == -1:
        #         # We have the ESC key pressed
        #         page = self.page.exit()
        #         if page is None:
        #             break
        #         else:
        #             self.page = page
        #             self.page.render()
        #     else:
        #         # We have ALT + next_key pressed
        #         key = 'ALT+' + chr(next_key)
        # else:
        #     res = self.page.notify(key)
        #     if res is not None:
        #         self.page = res
        #         self.page.render()
        #     # else:




if __name__ == "__main__":
    curses.wrapper(main)
