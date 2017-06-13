import logging
import os
import pickle
import random
import threading

import snowboy.snowboydecoder as sd


class Hotword(object):
    """Manager to detect hotwords and control video player correspondingly.

    Call destroy() before destruction.

    """
    MODEL_PATH = "model/"
    VIDEO_PATH = "video/"
    MAP_FILE = os.path.join(MODEL_PATH, "patronum.map")

    def __init__(self, strikes, cb_queue):
        """

        Args:
            strikes (deque): current attention status.
            cb_queue (queue): callback queue for passing tasks between threads.

        """
        # Logging.
        logging.basicConfig()
        self.logger = logging.getLogger("hotword")
        self.logger.setLevel(logging.DEBUG)

        self.end_detector = False
        self.strikes = strikes
        self.cb_queue = cb_queue

        self.patronum_map = Hotword.load_map()
        self.videos, self.models = self.load_videos_models()
        self.update_map()

        # Create detector.
        sensitivities = [0.5] * len(self.models)
        self.detector = sd.HotwordDetector(list(self.models),
                                      resource="snowboy/common.res",
                                      sensitivity=sensitivities,
                                      audio_gain=1)

        # Create detect thread.
        callbacks = [self.gen_callbacks(self.patronum_map[m])
                for m in list(self.models)]
        hotword_kwargs = {"detected_callback": callbacks,
                          "interrupt_check": lambda: self.end_detector,
                          "sleep_time": 0.03}
        self.detect_thread = threading.Thread(target=self.detector.start,
                                     kwargs=hotword_kwargs)
        self.detect_thread.start()

    def destroy(self):
        """Release resources. Must be called before class destruction.

        Returns:

        """
        self.end_detector = True
        self.detect_thread.join()
        self.detector.terminate()

    def gen_callbacks(self, video):
        """Generate detector callbacks corresponding to detector models.

        Args:
            video (str): video path to be passed to main thread for playing.

        Note:
            The callback functions will not be called in main thread.

        Returns:
            obj: callback function.

        """
        def callback():
            level = self.strikes.count(False) / self.strikes.maxlen
            logger.debug("Callback: {}\t{}".format(video, level))
            self.cb_queue.put((video, level))
        return callback

    @staticmethod
    def load_map():
        """Load mapping of hotword model to patronum video.

        Returns:
            dict: map of models to videos.

        """
        if not os.path.isfile(Hotword.MAP_FILE): # Exist no map file.
            p_map = {'mapped_videos': set()}
        else:
            with open(Hotword.MAP_FILE, "rb") as f:
                p_map = pickle.load(f)
        return p_map

    def load_videos_models(self):
        """Load videos from VIDEO_PATH and models from MODEL_PATH.

        Videos must have extension mp4. Models must have extension pmdl.

        Returns:
            set: set of video paths found. Ex. "video/video.mp4".
            set: set of model paths found. Ex. "model/model.pmdl".

        """
        videos = set(v for v in os.listdir(Hotword.VIDEO_PATH)
                if os.path.splitext(v)[-1].lower() == ".mp4")
        models = set(m for m in os.listdir(Hotword.MODEL_PATH)
                if os.path.splitext(m)[-1].lower() == ".pmdl")
        self.logger.info("Videos: {}".format(", ".join(videos)))
        self.logger.info("Models: {}".format(", ".join(models)))
        videos = set(os.path.join(Hotword.VIDEO_PATH, v) for v in videos)
        models = set(os.path.join(Hotword.MODEL_PATH, m) for m in models)
        return videos, models

    def update_map(self):
        """Update `patronum_map`.

        Add new models in `models` to `patronum_map`. Remove models not listed
        in `models` from `patronum_map`.

        Returns:

        """
        # Add models.
        for model in self.models:
            if not model in self.patronum_map:
                unmapped_videos = list(
                        self.videos - self.patronum_map["mapped_videos"])
                if unmapped_videos:
                    picked_video = random.choice(unmapped_videos)
                    self.patronum_map["mapped_videos"].add(picked_video)
                else: # All videos are used. Renew a choosing round.
                    picked_video = random.choice(list(self.videos))
                    self.patronum_map["mapped_videos"] = set(picked_video)
                self.patronum_map[model] = picked_video

        # Remove models.
        models_to_removed = [] # Avoid modifying `patronum_map` in iteration.
        for model in self.patronum_map:
            if model == "mapped_videos":
                continue
            if not model in self.models:
                self.patronum_map["mapped_videos"].remove(self.patronum_map[model])
                models_to_removed.append(model)
        for model in models_to_removed:
            _ = self.patronum_map.pop(model)

        # Update map file.
        with open(Hotword.MAP_FILE, "wb") as f:
            pickle.dump(self.patronum_map, f)

        self.logger.debug(self.patronum_map)


if __name__ == "__main__":
    import queue
    from collections import deque
    from play import Player

    cb_queue = queue.Queue() # Callback queue for passing tasks between threads.
    strikes = deque([False]*10, 10)
    player = Player()
    player.logger.setLevel(logging.NOTSET)
    hw = Hotword(strikes, cb_queue)
    hw.logger.setLevel(logging.NOTSET)
    try:
        while True:
            if random.random() < 0.5:
                strikes.append(True)
            else:
                strikes.append(False)
            if not cb_queue.empty():
                video, level = cb_queue.get(False)
                hw.logger.info(
                        "Ready to play {} with level {}.".format(video, level))
                player.play(video, level)
                # Remove additional play tasks added during previous playing.
                with cb_queue.mutex:
                    cb_queue.queue.clear()
    except KeyboardInterrupt:
        player.destroy()
        hw.destroy()
