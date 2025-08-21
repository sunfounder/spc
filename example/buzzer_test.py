from spc.spc import SPC
import time

spc = SPC()

origin_volume = spc.get_buzzer_volume()
print("origin buzzer volume: ", origin_volume)

class Tone:
    C4 = 262
    D4 = 294
    E4 = 330
    F4 = 349
    G4 = 392
    A4 = 440
    B4 = 494
    C5 = 523
    D5 = 587
    E5 = 659
    F5 = 698
    G5 = 784
    A5 = 880
    B5 = 988
    C6 = 1047
    D6 = 1175
    E6 = 1319
    F6 = 1397
    G6 = 1568
    A6 = 1760
    B6 = 1976
    C7 = 2093
    D7 = 2349
    E7 = 2637
    F7 = 2794
    G7 = 3136
    A7 = 3520
    B7 = 3951

def warning():
    for i in range(5):
        spc.buzzer_play_tone(Tone.C4, 0.2)
        time.sleep(0.2)

def alarm():
    for i in range(5):
        spc.buzzer_play_tone(Tone.G4, 0.1)
        time.sleep(0.1)

def low_battery():
    spc.buzzer_play_tone(Tone.E4, 0.1)
    spc.buzzer_play_tone(Tone.D4, 0.1)
    spc.buzzer_play_tone(Tone.C4, 0.1)

def usb_inplugged():
    spc.buzzer_play_tone(Tone.E4, 0.1)
    spc.buzzer_play_tone(Tone.A4, 0.1)

def usb_unplugged():
    spc.buzzer_play_tone(Tone.A4, 0.1)
    spc.buzzer_play_tone(Tone.E4, 0.2)
    spc.buzzer_play_tone(Tone.C4, 0.1)

def main():
    while True:
        for i in range(1, 10):
            spc.set_buzzer_volume(i)
            spc.buzzer_play_tone(Tone.C4, 0.5)
            spc.buzzer_play_tone(Tone.D4, 0.5)
            spc.buzzer_play_tone(Tone.E4, 0.5)
            spc.buzzer_play_tone(Tone.F4, 0.5)
            spc.buzzer_play_tone(Tone.G4, 0.5)
            spc.buzzer_play_tone(Tone.A4, 0.5)
            spc.buzzer_play_tone(Tone.B4, 0.5)
            spc.buzzer_play_tone(Tone.C5, 0.5)

        time.sleep(1)
        warning()
        time.sleep(1)
        alarm()
        usb_inplugged()
        time.sleep(1)
        usb_unplugged()
        time.sleep(1)
        low_battery()
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        spc.set_buzzer_volume(origin_volume)
        spc.buzzer_play_tone(0, 0.5)