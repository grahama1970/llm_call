# Logging Setup Helper

Standard loguru configuration for all scripts in this POC.

```python
from loguru import logger
import datetime
import os

# Remove default handler to prevent stderr output
logger.remove()

# Add only file handler
logger.add('task_execution.log', 
           rotation='1 MB', 
           enqueue=True, 
           backtrace=True, 
           diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
```

## For archiving old logs:
```python
if os.path.exists("task_execution.log"):
    archive_name = f"task_execution_archive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.rename("task_execution.log", archive_name)
    logger.info(f"[LOG_ARCHIVED] Previous log moved to {archive_name}")
```