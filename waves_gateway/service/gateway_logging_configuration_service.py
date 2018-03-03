"""
GatewayLoggingConfigurationService
"""

from logging import Logger, Handler
from typing import Optional, Union, List

from waves_gateway.common import Injectable, LOGGING_HANDLER_LIST, MANAGED_LOGGER_LIST


@Injectable(deps=[Logger, LOGGING_HANDLER_LIST, MANAGED_LOGGER_LIST])
class GatewayLoggingConfigurationService(object):
    """
    Controls the logging of the Gateway.
    """

    def __init__(self, logger: Logger, handlers: List[Handler], managed_loggers: List[Logger]) -> None:
        self._logger = logger
        self._logging_handlers = handlers
        self._managed_loggers = managed_loggers

    def set_log_level(self, level, loggers: Optional[Union[List[str], str]] = None):
        """
        Adjusts the log level for all known loggers or specific ones if an additional parameter is added.
        """
        to_be_adjusted = list()  # type: List[Logger]

        if loggers is None:
            for logger in self._managed_loggers:
                to_be_adjusted.append(logger)

            to_be_adjusted.append(self._logger)
        elif isinstance(loggers, str):
            if loggers == self._logger.name:
                to_be_adjusted.append(self._logger)

            for logger in self._managed_loggers:
                if logger.name == loggers:
                    to_be_adjusted.append(logger)
        else:
            if self._logger.name in loggers:
                to_be_adjusted.append(self._logger)

            for logger in self._managed_loggers:
                if logger.name in loggers:
                    to_be_adjusted.append(logger)

        for logger in to_be_adjusted:
            logger.setLevel(level)

        for handler in self._logging_handlers:
            handler.setLevel(level)
