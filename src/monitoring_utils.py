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

    # def log_custom_metric(self, metric_type, value, labels=None):
    #     labels = labels or {}

    #     series = monitoring_v3.TimeSeries()
    #     series.metric.type = f"custom.googleapis.com/{metric_type}"
    #     series.resource.type = "global"
    #     series.resource.labels["project_id"] = self.project_id

    #     for k, v in labels.items():
    #         series.metric.labels[k] = v

    #     now = time.time()
    #     point = series.points.add()
    #     point.value.double_value = float(value)
    #     point.interval.end_time.seconds = int(now)
    #     point.interval.end_time.nanos = int((now - int(now)) * 10**9)

    #     self.monitoring_client.create_time_series(
    #         request={"name": self.project_name, "time_series": [series]}
    #     )
    #     self.log_event(f"Logged metric: {metric_type}={value} with labels {labels}")
    def log_custom_metric(self, metric_type, value, labels=None):
        labels = labels or {}

        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/{metric_type}"
        series.resource.type = "global"
        series.resource.labels["project_id"] = self.project_id

        # Optional but good practice
        series.metric.kind = monitoring_v3.MetricDescriptor.MetricKind.GAUGE
        series.metric.value_type = monitoring_v3.MetricDescriptor.ValueType.DOUBLE

        for k, v in labels.items():
            series.metric.labels[k] = v

        now = time.time()
        point = series.points.add()
        point.value.double_value = float(value)
        point.interval.end_time.seconds = int(now)
        point.interval.end_time.nanos = int((now - int(now)) * 10**9)

        self.monitoring_client.create_time_series(
            request={"name": self.project_name, "time_series": [series]}
        )

        self.log_event(f"Logged metric: {metric_type}={value} with labels {labels}")


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

# Example usage:
# monitor = GCPMonitoring("your-gcp-project-id")
# monitor.log_event("SQL query executed successfully.")
# monitor.log_custom_metric("query_success", 1, {"query_type": "natural_language"})
# monitor.log_custom_metric("gpt4_latency", 2.37, {"model": "gpt-4"})
