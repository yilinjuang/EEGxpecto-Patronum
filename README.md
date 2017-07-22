# EEGxpecto-Patronum

    EEGxpecto-Patronum = EEG + Expecto Patronum

Use [Electroencephalography (EEG)](https://en.wikipedia.org/wiki/Electroencephalography) to simulate [Patronus Charm](https://www.pottermore.com/writing-by-jk-rowling/patronus-charm).

2017 Biomedical Engineering Final Project with S. T. Wu and Z. R. Wu.

## Description
> As a pure, protective magical concentration of happiness and hope (the recollection of a single talisman memory is essential in its creation). ---J.K. Rowling

According to Harry Potter, the Patronus is highly related to mental strength. Thus, we combined EEG signals with the spell and here we are.

**EEGxpecto-Patronum**.

Hotword detection is used to trigger the magic process when the spell is spoken, and also to determine who is spelling. Then, it takes EEG signals into account in order to measure the mental strength (attention). Finally, a speller-specific Patronus is shown variously depending on the mental strength.

![](https://images.pottermore.com/bxd3o8b291gf/3wLCdHOmLmAmKCCyia4AQ6/528dbdf658742466c8f0c9e48aa3f602/Expecto_Patronum.gif)

## Requirement
### EEG signals
Retrieved from EEG headset, for instance, [Mindwave Mobile](https://store.neurosky.com/pages/mindwave). Checkout [mindwave.ino](mindwave.ino) for collecting EEG signals from Mindwave Mobile thru bluetooth using arduino and HC-05 bluetooth module.

## Dependencies
- [snowboy](https://github.com/Kitt-AI/snowboy): DNN based hotword and wake word detection toolkit.
- [opencv3](https://github.com/opencv/opencv): Open Source Computer Vision Library.
- [pyserial](https://github.com/pyserial/pyserial): Python serial port access library.
- [scipy](https://github.com/scipy/scipy)
- [numpy](https://github.com/numpy/numpy)

## Usage
### [capture.js](capture.js)
1. Capture patronus videos from [pottermore](https://my.pottermore.com/patronus).
2. Convert video from format `.webm` to `.mp4`. For instance,
```
ffmpeg -i input.webm output.mp4
```
3. Place the `.mp4` video files under directory `video/`.

### [train_hotword.py](train_hotword.py)
1. Train your personal hotword, or **Expecto Patronum**, detection model. For detailed instructions, refer to [snowboy document](http://docs.kitt.ai/snowboy/#api-v1-train).
2. Place the `.pmdl` model file under directory `model/`.

### [main.py](main.py)
1. Set up EEG signals connection. [Here](main.py#L35-L46) we use `pyserial` to read EEG data from arduino. Feel free to replace it with other signal sources.
2. Shout out the spell **EXPECTO PATRONUM**!
3. Enjoy your magic trip~
