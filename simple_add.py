from loguru import logger
import datetime

logger.add('task_execution.log', 
           rotation='1 MB', 
           enqueue=True, 
           backtrace=True, 
           diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("📝 TASK 4 STARTED: Create simple function")
logger.info("-"*80)

def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    logger.info(f"Calculating {a} + {b}")
    result = a + b
    logger.info(f"Result calculated: {result}")
    
    # Write result to file
    with open("add_results.txt", "w") as f:
        f.write(f"The sum of {a} and {b} is {result}")
    logger.info("Result written to add_results.txt")
    
    return result

if __name__ == "__main__":
    # Log the code itself
    logger.info("[CODE_WRITTEN] simple_add.py:")
    logger.info("```python")
    with open("simple_add.py", "r") as f:
        logger.info(f.read())
    logger.info("```")
    
    # Execute the function
    logger.info("Executing add_numbers(2, 3)")
    result = add_numbers(2, 3)
    logger.info(f"Function returned: {result}")
    
    # Log the created file
    logger.info("[FILE_CREATED] add_results.txt:")
    logger.info("```")
    with open("add_results.txt", "r") as f:
        logger.info(f.read())
    logger.info("```")
    
    logger.info("✅ TASK 4 COMPLETED: Function created and executed")
    logger.info("="*80)