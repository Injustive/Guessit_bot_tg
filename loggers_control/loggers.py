import logging.config
import yaml

with open('loggers_control/settings.yml', 'r', encoding='unicode_escape') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(config)
db_logger = logging.getLogger("db_logger")
