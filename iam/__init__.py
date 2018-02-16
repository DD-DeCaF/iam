import logging
import sys


formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
