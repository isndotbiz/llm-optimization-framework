import logging
from pathlib import Path
from datetime import datetime

def setup_logging(models_dir: Path, level=logging.INFO):
    """Setup logging for AI Router"""
    log_dir = models_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"ai-router-{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )

    return logging.getLogger('ai-router')
