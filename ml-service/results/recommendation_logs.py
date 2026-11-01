import logging
logger=logging.getLogger("cinematch.recommendations")
def log_generation(user_id, duration_ms, count): logger.info("recommendations user=%s duration_ms=%.2f count=%d",user_id,duration_ms,count)
