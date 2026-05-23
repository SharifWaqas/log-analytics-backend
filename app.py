import threading
from api.log_queue import Queue
from storage.postgres_db import PostgreSQLDB
from ingestion.metrics import Metrics
from ingestion.worker import Worker

shared_queue = Queue()
database = PostgreSQLDB()
metric_object = Metrics()
worker_object = Worker(database,shared_queue,metric_object)

worker_thread = threading.Thread(target=worker_object.start_worker, daemon=True)
worker_thread.start()