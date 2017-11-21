from os import path
import logging
import time

try:
    import pigpio
    pi = pigpio.pi()
except ModuleNotFoundError:
    logging.error('No pigpio, are you running on a Pi?')
    class Pi:
        def callback(*args, **kwargs):
            pass
    class pigpio:
        FALLING_EDGE = None
    pi = Pi()

from vlc import VLC

class NoPinException(Exception):
    pass

class NoVideoException(Exception):
    pass

class Player:
    def __init__(self, pin_map):
        self.vlc = VLC()
        time.sleep(1)
        self.load(pin_map)
        
        for bcm, video in self.pins.items():
            pi.set_mode(bcm, pigpio.INPUT)
            pi.set_pull_up_down(bcm, pigpio.PUD_UP)
            pi.callback(bcm, pigpio.FALLING_EDGE, self.__gpio_change)

    def load(self, pin_map):
        self.pins = {}
        
        for e in pin_map:
            if 'bcm' in e:
                bcm = e['bcm']
            elif 'gpio' in e:
                bcm = gpio2bcm(e['gpio'])
            else:
                raise NoPinException('Error in pin map, either specify a bcm or gpio pin')

            try:
                self.pins[bcm] = path.basename(e['video'])
                self.vlc.add(e['video'])
            except AttributeError:
                raise NoVideoException('Specify a video!')

        
    def __gpio_change(self, bcm, level, t):
        if hasattr(self, 'last_update'):
            if time.time() - self.last_update < 1:
                return
        
        if bcm in self.pins:
            self.vlc.play(self.pins[bcm])
            self.last_update = time.time()
