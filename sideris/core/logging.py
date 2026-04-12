import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

class CenterNameFormatter(logging.Formatter):
    """Formateador simple que solo se encarga de centrar el nombre del logger."""
    def __init__(self, fmt, width=14):
        super().__init__(fmt)
        self.width = width

    def format(self, record):
        orig_name = record.name
        record.name = f"{record.name:^{self.width}}"
        result = super().format(record)
        record.name = orig_name
        return result

def setup_global_logging(level=logging.DEBUG):
    root_logger = logging.getLogger()
    if root_logger.handlers: 
        return

    # Tema de colores (se mantiene el original)
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
    return logging.getLogger(name)
