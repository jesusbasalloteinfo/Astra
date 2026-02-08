import os
import json
import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from rich.text import Text

DEFAULT_WIDTH = 16
_console = Console()

class SmartFormatter(logging.Formatter):
    def __init__(self, fmt, width=DEFAULT_WIDTH, is_file=False):
        super().__init__(fmt)
        self.width = width
        self.is_file = is_file

    def format(self, record):
        terminal_width = _console.width
        dynamic_max = max(40, terminal_width - 45)

        original_msg = record.msg
        full_data = getattr(record, 'full_msg', None)
        has_extra = full_data is not None

        # 1. CONSOLE
        if not self.is_file:
            # Si es muy largo o tiene extra, ponemos el indicador
            if len(original_msg) > dynamic_max or has_extra:
                short_msg = original_msg[:dynamic_max].strip()
                if len(original_msg) > dynamic_max:
                    short_msg += "..."
                record.msg = f"{short_msg} [cadet_blue](+)[/]"

        # 2. FILE
        else:
            if has_extra:
                if isinstance(full_data, (dict, list)):
                    formatted_data = json.dumps(full_data, indent=4, ensure_ascii=False)
                    margin = " " * 36
                    full_data = formatted_data.replace("\n", "\n" + margin)

                record.msg = f"{original_msg}\n{" "*24}└── DETAILS: {full_data}"
            else:
                record.msg = original_msg
            # Clean tags
            record.msg = Text.from_markup(str(record.msg)).plain

        orig_name = record.name
        record.name = f"{record.name:^{self.width}}"

        result = super().format(record)

        # Restore for other handlers
        record.msg = original_msg
        record.name = orig_name
        return result

class ExtraLogger(logging.LoggerAdapter):
    def __init__(self, logger):
        super().__init__(logger, {})

    def debug(self, msg, details=None, *args, **kwargs):
        if details: kwargs["extra"] = {"full_msg": details}
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, details=None, *args, **kwargs):
        if details: kwargs["extra"] = {"full_msg": details}
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, details=None, *args, **kwargs):
        if details: kwargs["extra"] = {"full_msg": details}
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, details=None, *args, **kwargs):
        if details: kwargs["extra"] = {"full_msg": details}
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, details=None, *args, **kwargs):
        if details: kwargs["extra"] = {"full_msg": details}
        self.logger.critical(msg, *args, **kwargs)

def setup_global_logging(level = logging.DEBUG, file_path: str = "logs/app.log"):
    root_logger = logging.getLogger()
    if root_logger.handlers: return

    # Logger colors
    theme = Theme({
        "logging.level.debug": "bold italic green", # Callbacks and other types
        "logging.level.info": "bold italic dodger_blue2", # Normal events
        "logging.level.warning": "bold orange_red1",
        "logging.level.error": "bold red1",
        "logging.level.critical": "bold white on red",
        "log.time": "cadet_blue"
    })
    name_color="bold grey50"

    # CONSOLE-only
    console = Console(theme=theme)

    rich_handler = RichHandler(
        level="DEBUG",
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
        log_time_format="[%X]"
    )
    rich_handler.setFormatter(SmartFormatter("["+name_color+"]%(name)s[/]  │ %(message)s", width=14, is_file=False))
    rich_handler.setLevel(level)

    # File mode
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    file_handler = RotatingFileHandler(file_path, maxBytes=5*1024*1024, backupCount=3) # 5MB max file, 3 max files
    file_handler.setFormatter(SmartFormatter("%(asctime)s | %(levelname)-8s | %(name)s -> %(message)s", is_file=True))
    file_handler.setLevel(level)

    root_logger.setLevel(level)
    root_logger.addHandler(rich_handler)
    root_logger.addHandler(file_handler)

def get_logger(name: str):
    return ExtraLogger(logging.getLogger(name))
