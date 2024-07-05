import logging
import sys

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S',
    stream=sys.stdout,
)
logging.root.setLevel(logging.INFO)

logger = logging.getLogger('')

# TODO: write custom tqdm logger that writes the progress bar to the logger: https://github.com/tqdm/tqdm/issues/313
# then, replace all tqdm calls with the custom tqdm-logger
