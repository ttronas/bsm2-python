import logging
import sys
from functools import partialmethod

from tqdm import tqdm


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.INFO, *, tqdm_level_is_lower=False):
        """
        A logging handler that writes log messages to tqdm.

        Parameters
        ----------
        level : int, optional
            The log level for this handler. Default is logging.INFO
        tqdm_level_is_lower : bool, optional
            If True, the progress bar is not shown when the log level is higher than the tqdm log level.
            Default is False
        """
        super().__init__(level)
        if tqdm_level_is_lower:
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


log_level = logging.INFO
tqdm_log_level = logging.INFO
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=log_level,
    datefmt='%H:%M:%S',
    stream=sys.stdout,
)
logging.root.setLevel(log_level)

logger = logging.getLogger('')
logger.addHandler(TqdmLoggingHandler(level=tqdm_log_level, tqdm_level_is_lower=log_level > tqdm_log_level))
