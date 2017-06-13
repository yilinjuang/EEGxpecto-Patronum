import logging

import cv2
import numpy as np


class Player(object):
    """Video player using opencv3.

    Call destroy() before destruction.

    """
    # Window settings.
    WIN_NAME = "Patronum"
    WIN_WIDTH = 1280
    WIN_HEIGHT = 1024
    # WIN_WIDTH = 1440
    # WIN_HEIGHT = 900
    CAP_WIDTH_INDEX = 3
    CAP_HEIGHT_INDEX = 4

    def __init__(self):
        """ Create window and show default black background."""
        # Logging.
        logging.basicConfig()
        self.logger = logging.getLogger("player")
        self.logger.setLevel("DEBUG")

        # Create window.
        cv2.namedWindow(Player.WIN_NAME, cv2.WINDOW_AUTOSIZE)
        cv2.setWindowProperty(Player.WIN_NAME, cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN)

        # Create black background.
        self.bg = np.zeros((Player.WIN_HEIGHT, Player.WIN_WIDTH, 3), np.uint8)
        self.show_bg()

    def destroy(self):
        """Release resources. Must be called before class destruction.

        Returns:

        """
        cv2.destroyAllWindows()

    def play(self, video, level):
        """Play video with target level.

        Args:
            video (str): video path to be played.
            level (float): attention level. Range from 0.0 to 1.0.

        Returns:

        """
        self.logger.info("Play {} with level {}.".format(video, level))
        cap = cv2.VideoCapture(video)
        display = self.bg.copy()
        frame_w = int(cap.get(Player.CAP_WIDTH_INDEX))
        frame_h = int(cap.get(Player.CAP_HEIGHT_INDEX))
        x_offset = (Player.WIN_WIDTH - frame_w) // 2
        y_offset = (Player.WIN_HEIGHT - frame_h) // 2
        i_frame = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:     # Exit if no more frames.
                self.logger.debug("End of video.")
                break

            # Speed up.
            i_frame += 1
            if i_frame % 3 != 0:
                continue

            # Stop playing ealier according to level.
            if (level > 0.9 and i_frame > 50) or \
                    (level > 0.8 and i_frame > 100) or \
                    (level > 0.7 and i_frame > 200) or \
                    (level > 0.6 and i_frame > 800):
                self.logger.debug("Stop playing earlier.")
                break

            # Merge video and default black background.
            if x_offset > 0 and y_offset > 0:
                display[y_offset:-y_offset, x_offset:-x_offset, :] = frame
            elif x_offset < 0 and y_offset > 0: # Videos wider than screen.
                display[y_offset:-y_offset, :, :] = \
                        frame[:, -x_offset:x_offset, :]
            elif x_offset > 0 and y_offset < 0: # Videos higher than screen.
                display[:, x_offset:-x_offset, :] = \
                        frame[-y_offset:y_offset:, :, :]
            elif x_offset < 0 and y_offset < 0: # Videos wider and higher than screen.
                display = frame[-y_offset:y_offset, -x_offset:x_offset, :]

            # Blur the image according to level.
            sigma = min(np.exp(9*level)/100, 20)
            display = cv2.GaussianBlur(display, (0, 0), sigma)

            cv2.imshow(Player.WIN_NAME, display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.logger.debug("Key 'q' pressed. Stop playing.")
                break
        cap.release()
        # Resume to default black background.
        self.show_bg()

    def show_bg(self):
        """Show default black background.

        Returns:

        """
        cv2.imshow(Player.WIN_NAME, self.bg)
        cv2.waitKey(1)


if __name__ == "__main__":
    import time

    player = Player()
    player.logger.setLevel(logging.NOTSET)
    player.logger.debug("Show default black background for one second.")
    time.sleep(1)
    player.logger.debug("Play video.")
    player.play("video/swan.mp4", 0.6)
    player.logger.debug("Show default black background for one second.")
    time.sleep(1)
    player.destroy()
