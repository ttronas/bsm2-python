import logging
import sys

import tqdm


# TODO tqdm progress bar nicht anzeigen, wenn logging level zu hoch
class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S',
    stream=sys.stdout,
)
logging.root.setLevel(logging.INFO)

logger = logging.getLogger('')
# logger.addHandler(TqdmLoggingHandler())

# TODO: write custom tqdm logger that writes the progress bar to the logger: https://github.com/tqdm/tqdm/issues/313
# then, replace all tqdm calls with the custom tqdm-logger
# maybe this? https://stackoverflow.com/questions/74222161/tqdm-and-print-logging-doesnt-work-properly-no-linebreak-for-first-logging
# import time
# for i in tqdm.tqdm(range(100)):
#     if i % 10 == 0:
#         logger.info("test")
#     time.sleep(.1)
#     pass
