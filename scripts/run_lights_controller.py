import argparse
import logging
import logging.config as log_config
import yaml

from lights.controller import Controller

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", default='data/config.yaml', help="configuration file location")
    parser.add_argument("-l", "--logging", default="logging.yaml", help="logging configuration")
    args = parser.parse_args()

    with open(args.logging, 'r') as f:
        config = yaml.safe_load(f.read())
        log_config.dictConfig(config)

    with open(args.config, 'r') as f:
        app_config = yaml.safe_load(f.read())
    controller = Controller(app_config)
    try:

        controller.start()
    except KeyboardInterrupt:
        logger.info(f"Stopping service (interrupted by user)")
        controller.turn_off()
    except Exception:
        logger.exception(f"Stopping service")
        controller.turn_off()
