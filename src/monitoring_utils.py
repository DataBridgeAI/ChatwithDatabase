import time
import logging
from google.cloud import monitoring_v3
import google.cloud.logging as cloud_logging

class GCPMonitoring:
    def __init__(self, project_id):
        self.project_id = project_id
        self.project_name = f"projects/{project_id}"
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.logging_client = cloud_logging.Client()
        self.logger = self.setup_logger()

    def setup_logger(self):
        self.logging_client.setup_logging()
        logger = logging.getLogger("GCPMonitoring")
        logger.setLevel(logging.INFO)
        return logger

    def log_event(self, message, severity="INFO"):
        if severity == "ERROR":
            self.logger.error(message)
        elif severity == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def shutdown(self):
        # Flush and close all logging handlers to prevent lost logs
        for handler in logging.getLogger().handlers:
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
        try:
            self.logging_client.close()
        except Exception:
            pass
