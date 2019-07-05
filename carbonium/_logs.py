import logging
logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')
log = logging.getLogger("carbonium")
log.setLevel(logging.DEBUG) # FIXME, should be defined at bot instantiation

fblog = logging.getLogger('client')
fblog.setLevel(logging.WARNING) # don't ask
