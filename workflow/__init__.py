import logging

logger = logging.getLogger(__name__)

if not logger.root.handlers:
    logger.setLevel(logging.INFO)
    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(fmt='{asctime} ; {name} ; {levelname} - {module} ; {lineno} ; {funcName} - {message}',
                              style='{')
        )
        logger.addHandler(handler)
