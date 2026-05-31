import logging
from rich.logging import RichHandler
from rich.theme import Theme
from rich.console import Console

class CenterNameFormatter(logging.Formatter):
    """Simple formatter that centers the logger name for aesthetic alignment."""

    def __init__(self, fmt, width=14):
        """Initialize the formatter.

        Args:
            fmt (str): The logging format string.
            width (int): The target width for centering the logger name. Defaults to 14.
        """
        super().__init__(fmt)
        self.width = width

    def format(self, record):
        """Formats the record, centering the name field.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """
        orig_name = record.name
        record.name = f"{record.name:^{self.width}}"
        result = super().format(record)
        record.name = orig_name
        return result

def setup_global_logging(level=logging.DEBUG):
    """Configures the global logging system using Rich for stylized console output.

    Sets up a RichHandler with a custom theme and name centering for all loggers 
    in the application.

    Args:
        level (int): The logging level to set (e.g., logging.DEBUG, logging.INFO).
    """
    root_logger = logging.getLogger()
    if root_logger.handlers: 
        return

    # Color theme for the logs
    theme = Theme({
        "logging.level.debug": "bold italic green",
        "logging.level.info": "bold italic dodger_blue2",
        "logging.level.warning": "bold orange_red1",
        "logging.level.error": "bold red1",
        "logging.level.critical": "bold white on red",
        "log.time": "cadet_blue"
    })

    console = Console(theme=theme)

    rich_handler = RichHandler(
        level=level,
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
        log_time_format="[%X]"
    )
    
    name_color = "bold grey50"
    rich_handler.setFormatter(CenterNameFormatter(f"[{name_color}]%(name)s[/]  │ %(message)s", width=14))

    root_logger.setLevel(level)
    root_logger.addHandler(rich_handler)

def get_logger(name: str):
    """Retrieves a logger instance by name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The requested logger instance.
    """
    return logging.getLogger(name)
