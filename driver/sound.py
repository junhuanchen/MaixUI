
from es8374 import ES8374
from machine import I2C
from Maix import I2S, GPIO
from fpioa_manager import *
import audio, time
# from machine import Timer

class CubeAudio:

    i2c, i2s, dev = I2C(I2C.I2C1, freq=100*1000), I2S(I2S.DEVICE_0, pll2=262144000, mclk=31), None

    # tim = Timer(Timer.TIMER0, Timer.CHANNEL0, start=False, mode=Timer.MODE_PERIODIC, period=15, callback=lambda:None)

    def check():
      return ES8374._ES8374_I2CADDR_DEFAULT in CubeAudio.i2c.scan()

    player, is_load, is_ready = None, False, False

    def ready(is_record=False, volume=100):
      CubeAudio.is_ready = CubeAudio.is_load = False
      if CubeAudio.check():
        if CubeAudio.dev != None:
            CubeAudio.dev.stop(0x02)
        CubeAudio.dev = ES8374()
        CubeAudio.dev.setVoiceVolume(volume)
        CubeAudio.dev.start(0x03)
        if is_record:
            CubeAudio.i2s.channel_config(I2S.CHANNEL_0, I2S.RECEIVER, resolution=I2S.RESOLUTION_16_BIT,
                cycles=I2S.SCLK_CYCLES_32, align_mode=I2S.STANDARD_MODE)
        else:
            CubeAudio.i2s.channel_config(I2S.CHANNEL_2, I2S.TRANSMITTER, resolution=I2S.RESOLUTION_16_BIT,
                cycles=I2S.SCLK_CYCLES_32, align_mode=I2S.STANDARD_MODE)
        CubeAudio.is_ready = True
      return CubeAudio.is_ready

    def load(path, volume=100):
        if CubeAudio.player != None:
            CubeAudio.player.finish()
            # CubeAudio.tim.stop()
        CubeAudio.player = audio.Audio(path=path)
        CubeAudio.player.volume(volume)
        wav_info = CubeAudio.player.play_process(CubeAudio.i2s)
        CubeAudio.i2s.set_sample_rate(int(wav_info[1]))

        CubeAudio.is_load = True
        # CubeAudio.tim.callback(CubeAudio.event)
        # CubeAudio.tim.start()
        #time.sleep_ms(1000)

    def event(arg=None):
        if CubeAudio.is_load:
            ret = CubeAudio.player.play()
            if ret == None or ret == 0:
                CubeAudio.player.finish()
                time.sleep_ms(50)
                # CubeAudio.tim.stop()
                CubeAudio.is_load = False
            return True
        return False

if __name__ == "__main__":
    fm.register(24, fm.fpioa.I2C1_SCLK, force=True)
    fm.register(27, fm.fpioa.I2C1_SDA, force=True)
    #fm.register(30,fm.fpioa.I2C1_SCLK, force=True)
    #fm.register(31,fm.fpioa.I2C1_SDA, force=True)
    tmp = CubeAudio.check()
    print(tmp)
    if (tmp):

        CubeAudio.ready()

        #fm.register(19,fm.fpioa.I2S0_MCLK, force=True)
        #fm.register(35,fm.fpioa.I2S0_SCLK, force=True)
        #fm.register(33,fm.fpioa.I2S0_WS, force=True)
        #fm.register(34,fm.fpioa.I2S0_IN_D0, force=True)
        #fm.register(18,fm.fpioa.I2S0_OUT_D2, force=True)
        fm.register(13,fm.fpioa.I2S0_MCLK, force=True)
        fm.register(21,fm.fpioa.I2S0_SCLK, force=True)
        fm.register(18,fm.fpioa.I2S0_WS, force=True)
        fm.register(35,fm.fpioa.I2S0_IN_D0, force=True)
        fm.register(34,fm.fpioa.I2S0_OUT_D2, force=True)

        while True:
            CubeAudio.load("/flash/res/sound/loop.wav", 80)
            while CubeAudio.is_load:
                #time.sleep_ms(20)
                CubeAudio.event()
                print(time.ticks_ms())

        CubeAudio.ready()
        player = audio.Audio(path="/sd/record_5.wav")
        player.volume(100)
        # read audio info
        wav_info = player.play_process(CubeAudio.i2s)
        print("wav file head information: ", wav_info)
        CubeAudio.i2s.set_sample_rate(int(wav_info[1] / 2))
        print('loop to play audio')
        while True:
          ret = player.play()
          if ret == None:
              print("format error")
              break
          elif ret == 0:
              break
        player.finish()

        # record to wav
        print('record to wav')
        CubeAudio.ready(True)
        CubeAudio.i2s.set_sample_rate(22050)

        # init audio
        player = audio.Audio(path="/sd/record_5.wav",
                             is_create=True, samplerate=22050)
        queue = []
        for i in range(400):
          tmp = CubeAudio.i2s.record(1024)
          if len(queue) > 0:
              print(time.ticks())
              ret = player.record(queue[0])
              queue.pop(0)
          CubeAudio.i2s.wait_record()
          queue.append(tmp)
        player.finish()
