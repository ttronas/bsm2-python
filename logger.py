import sys
import logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S',
    stream=sys.stdout,
)
logging.root.setLevel(logging.INFO)

log = logging.getLogger('')
