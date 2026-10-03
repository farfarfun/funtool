from funtool.log.log import log


def log_level():
    logger = log()

    logger.info("this is info")
    logger.debug("this is debug")
    logger.warning("this is warning")
    logger.error("this is error")
    logger.critical("this is critical")


log_level()
