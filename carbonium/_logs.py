import logging
logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')
log = logging.getLogger("carbonium")
log.setLevel(logging.INFO) # FIXME, should be defined at bot instantiation
