from datetime import datetime, timedelta


class Aggregator:
    def __init__(self, database):
        self._db = database

    def aggregate_hour(self, hour_start):
        start_str = hour_start.strftime("%Y-%m-%d %H:%M:%S")
        end = hour_start + timedelta(hours=1)
        end_str = end.strftime("%Y-%m-%d %H:%M:%S")

        counts = self._db.count_clicks_in_range(start_str, end_str)
        periods = self._db.get_activity_periods_in_range(start_str, end_str)

        active_seconds = 0
        pause_seconds = 0

        for p in periods:
            p_start = datetime.strptime(p["start_time"], "%Y-%m-%d %H:%M:%S")
            p_end = datetime.strptime(p["end_time"], "%Y-%m-%d %H:%M:%S") if p["end_time"] else datetime.now()

            effective_start = max(p_start, hour_start)
            effective_end = min(p_end, end)

            if effective_end > effective_start:
                seconds = (effective_end - effective_start).total_seconds()
                if p["type"] == "active":
                    active_seconds += int(seconds)
                else:
                    pause_seconds += int(seconds)

        self._db.upsert_hourly_stats(
            start_str,
            counts["total"],
            counts["left_clicks"],
            counts["right_clicks"],
            counts["middle_clicks"],
            active_seconds,
            pause_seconds,
        )

    def get_hourly_stats(self, date_str):
        return self._db.get_hourly_stats(date_str)

    def get_current_hour_clicks(self):
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        start_str = hour_start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = (hour_start + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        counts = self._db.count_clicks_in_range(start_str, end_str)
        return counts["total"]

    def aggregate_previous_hour(self):
        now = datetime.now()
        previous_hour = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        self.aggregate_hour(previous_hour)
