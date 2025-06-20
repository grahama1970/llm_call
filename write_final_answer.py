from loguru import logger
import datetime

logger.add('task_execution.log', 
           rotation='1 MB', 
           enqueue=True, 
           backtrace=True, 
           diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("❓ TASK 7 STARTED: Answer question (verification passed)")
logger.info("-"*80)

# Write the answer to the question
answer = "Paris"
with open("final_answer.txt", "w") as f:
    f.write(answer)

logger.info("[FILE_WRITTEN] final_answer.txt:")
logger.info("```")
logger.info(answer)
logger.info("```")

logger.info("🎉 TASK 7 COMPLETED: Sequential execution finished")
logger.info("="*80)