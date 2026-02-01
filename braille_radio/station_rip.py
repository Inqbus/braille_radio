import threading

import pexpect

from braille_radio.base import Screen
from braille_radio.config import NUM_SCOLLER_LINES, RIPPER_OUT_DIR

from braille_radio.log import logger

class Scroller:
    def __init__(self, screen):
        logger.debug('Creating scroller')
        self.screen = screen
        self.current_line = 0
        self.line_starty = 2
        self.clear()

    def clear(self):
        logger.debug('scroller: clear')
        self.lines = [''] * NUM_SCOLLER_LINES
        self.draw_all_lines()

    def draw_line_at(self, line, y):
        logger.debug(f'scroller: draw line at {y}')
        self.screen.move(y, 0)
        self.screen.clrtoeol()
        self.screen.addstr(y, 0, line)

    def draw_all_lines(self):
        logger.debug('scroller: draw all lines')
        for y, line in enumerate(self.lines):
            self.draw_line_at(line, self.line_starty + y)
        self.screen.refresh()

    def append_line(self, line):
        logger.debug(f'scroller: append line: curr: {self.current_line}')
        # If we are at the end of scroller
        if self.current_line == NUM_SCOLLER_LINES - 1:
            logger.debug('scroller: at end of scroller, moving lines up')
            # move all lines up and append line
            self.lines = self.lines[1:] + [line]
            self.draw_all_lines()
        else:
            logger.debug('scroller: appending line')
            self.current_line += 1
            self.lines[self.current_line] = line
            self.draw_line_at(line, self.line_starty + self.current_line)
            self.screen.refresh()

    def refresh_line(self, line):
        logger.debug('scroller: Refresh line')
        if line.strip() == '':
            return
        self.lines[self.current_line] = line
        self.draw_line_at(line, self.line_starty + self.current_line)
        self.screen.refresh()


def ripper_worker(uri, screen, stop_event):
    logger.debug('Spawning streamripper')
    child = pexpect.spawn(f'streamripper  {uri} -d {RIPPER_OUT_DIR} -o never')
    logger.debug('streamripper spawned.')

    scroller = Scroller(screen)

    try:
        while not stop_event.is_set():
            logger.debug('Pexcpecting loop')

            # Sucht nach dem nächsten \r ODER \n
            # Index 0 entspricht \r, Index 1 entspricht \n
            index = child.expect(['\r', '\n'])

            # Alles, was vor dem Steuerzeichen kam, ist Textinhalt
            raw_content = child.before
            if isinstance(raw_content, bytes):
                new_content = raw_content.decode('utf-8', errors='ignore')
            else:
                new_content = raw_content

            if index == 0:
                # FALL \r: Zeile "refreshen"
                scroller.refresh_line(new_content)

            elif index == 1:
                # FALL \n: Neue Zeile anfangen
                scroller.append_line(new_content)

        logger.debug('stop_event stopped loop')

        child.close(force=True)
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

        self.stop_event = threading.Event()

        self.ripper_thread = threading.Thread(
            target=ripper_worker,
            args=(uri, self.screen, self.stop_event ),
            daemon=True
        )
        self.ripper_thread.start()

    def exit(self):
        logger.debug('sending stop_event')
        self.stop_event.set()
        logger.debug('stop_event sent')

        if self.ripper_thread and self.ripper_thread.is_alive():
            logger.debug('joining thread')
            self.ripper_thread.join(timeout=0.5)  # BLOCKIERT bis tot!
            logger.debug('thread finished')

        logger.debug('move(0,0)')
        self.screen.move(0, 0)
        logger.debug('return to parent')
        return self.parent

    def notify(self, key):
        pass
