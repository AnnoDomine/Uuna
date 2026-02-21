import sys
import os
import json


class SeverityLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    ALL = ["DEBUG", "INFO", "WARNING", "ERROR", "SUCCESS"]


class DatabaseLogHandler:
    """
    A specialized Loguru sink.
    Preserves every log in a role-specific file AND the central Database (except DEBUG).
    Enriches logs with Task and Build context for the Observer.
    """

    def __init__(self, db_client, log_type: str):
        self.db = db_client
        self.log_type = log_type
        self.query_path_log = "Tools/core/api/queries/logs/insert_event_log.sql"
        self.query_path_get_builds = "Tools/core/api/queries/logs/get_build_ids.sql"

        # Ensure log directory exists
        self.log_dir = "Tools/core/logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f"{self.log_type}.log")

    def _get_build_context(self, task_id: str) -> str:
        try:
            with open(self.query_path_get_builds, "r") as f:
                sql = f.read().strip()
            res = self.db.execute(sql, [task_id]).fetchone()
            if res and res[0]:
                builds = res[0]
                if isinstance(builds, str):
                    builds = json.loads(builds)
                return ", ".join(builds)
        except Exception:
            pass
        return "N/A"

    def write(self, message):
        record = message.record
        extra = record.get("extra", {})

        task_id = extra.get("task_id", None)
        event_id = extra.get("event_id", None)
        role = extra.get("process", "System")
        severity = record["level"].name

        # 1. Handle Debug Filtering
        if severity == SeverityLevel.DEBUG and not os.getenv("AI_DEBUG", False):
            return

        # 2. Build Meta Information
        build_str = extra.get("builds")
        if not build_str and task_id:
            build_str = self._get_build_context(str(task_id))
        else:
            build_str = ", ".join(build_str) if isinstance(build_str, list) else (build_str or "N/A")

        timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
        meta_info = f"[{timestamp} - {severity} - Task: {task_id or 'N/A'} - Event: {event_id or 'N/A'} - Role: {role} - Builds: [{build_str}]]:"
        full_log_entry = f"{meta_info} {record['message']}"

        # 3. Write to File (Always if reached this point)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(full_log_entry + "\n")
        except Exception:
            pass

        # 4. Write to Terminal
        output_stream = sys.stderr if record["level"].no >= 40 else sys.stdout
        output_stream.write(full_log_entry + "\n")
        output_stream.flush()

        # 5. Save to Database (STRICTLY NO DEBUG LOGS)
        if severity != SeverityLevel.DEBUG and task_id and event_id:
            try:
                with open(self.query_path_log, "r") as f:
                    sql_log = f.read().strip()
                # Use the db client instead of direct connect
                self.db.execute(sql_log, [task_id, event_id, role, full_log_entry])
            except Exception as e:
                # Use standard print to avoid recursion if the error is within the logger itself
                print(f"CRITICAL: DB Logger failed: {e}", file=sys.stderr)
