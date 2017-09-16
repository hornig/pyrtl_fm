import numpy as np
import matplotlib.pylab as plt
import time

# inspired by https://github.com/osmocom/rtl-sdr/blob/master/src/rtl_fm.c


# loading in the .wav
signal = np.memmap("SDRSharp_20170830_073822Z_145825000Hz_IQ.wav", offset=44)

result = np.zeros(len(signal)//2, dtype=np.float)

downsample = 128


def low_pass(signal):
    # simple square window FIR

    lowpassed = signal[:]

    # needs to be go outside this function
    now_r = 0
    now_j = 0

    i=0
    i2=0

    prev_index = 0

    while (i < len(lowpassed)):
        now_r += lowpassed[i]
        now_j += lowpassed[i + 1]
        i += 2

        prev_index += 2

        if (prev_index < downsample):
            continue

        lowpassed[i2]     = now_r
        lowpassed[i2 + 1] = now_j
        prev_index = 0
        now_r = 0
        now_j = 0
        i2 += 2

    lp_len = i2

    return lowpassed

def multiply(ar, aj, br, bj):
    cr = ar * br - aj * bj
    cj = aj * br + ar * bj
    return cr, cj

def polar_discriminant(ar, aj, br, bj):
    cr , cj = multiply(ar, aj, br, -bj)
    #print(cr, cj)
    angle = np.arctan2(cj, cr)
    #print("angle", angle)
    # return (angle / np.pi * (1<<14))
    return (angle * 180.0 / np.pi)

def fm_demod(signal, result):
    pre_r = 0
    pre_j = 0

    i = 0
    pcm = 0

    lp_len = len(signal)

    # low-passing
    lp = low_pass(signal)
    #print(lp[0], lp[1], pre_r, pre_j)

    pcm = polar_discriminant(lp[0], lp[1], pre_r, pre_j)
    result[0] = pcm

    for i in range(2, lp_len-1, 2):
        # being lazy, only case 0 for now...

        # case 0
        pcm = polar_discriminant(lp[i], lp[i + 1], lp[i - 2], lp[i - 1])

        result[i // 2] = pcm

    pre_r = lp[lp_len - 2]
    pre_j = lp[lp_len - 1]
    result_len = lp_len // 2

    #return(result)


time1 = time.time()
signal = -127.5 + signal

fm_demod(signal, result)

print(time.time() - time1)

plt.plot(result[::10])
plt.show()