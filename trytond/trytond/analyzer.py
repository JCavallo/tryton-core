import os
from typing import Any

ANALYZING = bool(os.environ.get('TRYTON_ANALYZER_RUNNING', False))
Record = Any
Records = list[Any]
