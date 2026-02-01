import queue
import threading

import pexpect

from braille_radio.base import Screen
from braille_radio.config import NUM_SCOLLER_LINES, RIPPER_OUT_DIR


class Scroller:
    def __init__(self, screen):
        self.screen = screen
        self.current_line = 0
        self.line_starty = 2
        self.clear()

    def clear(self):
        self.lines = [''] * NUM_SCOLLER_LINES
        self.draw_all_lines()

    def draw_line_at(self, line, y):
        self.screen.move(y, 0)
        self.screen.clrtoeol()
        self.screen.addstr(y, 0, line)

    def draw_all_lines(self):
        for y, line in enumerate(self.lines):
            self.draw_line_at(line, self.line_starty + y)
        self.screen.refresh()

    def append_line(self, line):
        if line.strip() == '':
            return self.current_line
        # If we are at the end of scroller
        if self.current_line == NUM_SCOLLER_LINES -1:
            # move all lines up and append line
            self.lines = self.lines[1:] + [line]
            self.draw_all_lines()
        else:
            self.lines[self.current_line] = line
            self.draw_line_at(line, self.line_starty + self.current_line)
            self.screen.refresh()
            self.current_line += 1
        return self.current_line

    def refresh_line(self, line, line_num):
        self.lines[line_num] = line
        self.draw_line_at(line, self.line_starty + line_num)
        self.screen.refresh()
        return line_num

stop_event = threading.Event()

def ripper_worker(uri, scroller):
    child = pexpect.spawn(f'streamripper  {uri} -d {RIPPER_OUT_DIR} -o never')
    current_line = ''
    current_line_num = None
    try:
        while not stop_event.is_set():

            # Sucht nach dem nächsten \r ODER \n
            # Index 0 entspricht \r, Index 1 entspricht \n
            index = child.expect(['\r', '\n'])

            # Alles, was vor dem Steuerzeichen kam, ist Textinhalt
            raw_content = child.before
            if isinstance(raw_content, bytes):
                new_content = raw_content.decode('utf-8', errors='ignore')
            else:
                new_content = raw_content

            current_line += new_content

            if index == 0:
                # FALL \r: Zeile "refreshen"
                # Wir geben den Text aus und springen zum Anfang der Zeile (\r)
                # 'end=""' verhindert, dass Python von sich aus ein \n anhängt
                if current_line_num is None:
                    current_line_num = scroller.append_line(current_line)
                else:
                    current_line_num = scroller.refresh_line(current_line, current_line_num)


                # Wichtig: Für die Logik "Zeile löschen" leeren wir den String
                current_line = ""

            elif index == 1:
                # FALL \n: Neue Zeile anfangen
                current_line_num = scroller.append_line(current_line)
                current_line = ""
        child.close(force=True)
        scroller.clear()
    except pexpect.EOF:
        pass


class StationRip(Screen):
    """
    Rip a certain station
    """
    station = None
    p = None

    def tune_to(self, station):
        self.station = station


    def payload(self):
        self.screen.addstr(0, 0, 'Ripping: %s' % self.station['name'])
        uri = self.station['url_resolved']
        self.screen.addstr(1, 0, 'Ripping URI: %s' % self.station['url_resolved'])
        self.screen.refresh()

        self.scroller = Scroller(self.screen)

        t = threading.Thread(target=ripper_worker, args=(uri, self.scroller), daemon=True)
        t.start()

    def exit(self):
        stop_event.set()
        del self.scroller
        self.screen.move(0, 0)
        return self.parent

    def notify(self, key):
        pass



