import logging
#from logstash_async.handler import AsynchronousLogstashHandler

class Logger() :
   def log(log:str):
     host='localhost'
     port=5000
     logger=logging.getLogger('antiprop-logging')
     logger.setLevel(logging.DEBUG)
     #async_handler=AsynchronousLogstashHandler(host,port,database_path=None)
     #logger.addHandler(async_handler)
     return logger.info(log)




