import csv
from datetime import datetime, timedelta


class Exporter:
    @staticmethod
    def export_day_csv(database, date_str, output_path):
        start = date_str
        end_dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
        end = end_dt.strftime("%Y-%m-%d")

        clicks = database.get_clicks_in_range(start, end)
        hourly = database.get_hourly_stats(date_str)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "button", "x", "y"])
            for c in clicks:
                writer.writerow([c["timestamp"], c["button"], c["x"], c["y"]])

            writer.writerow([])
            writer.writerow(["--- RESUMO HORÁRIO ---"])
            writer.writerow([
                "hora", "total_cliques", "esquerdo", "direito",
                "meio", "ativo_min", "pausa_min"
            ])
            for h in hourly:
                writer.writerow([
                    h["hour_start"],
                    h["total_clicks"],
                    h["left_clicks"],
                    h["right_clicks"],
                    h["middle_clicks"],
                    h["active_seconds"] // 60,
                    h["pause_seconds"] // 60,
                ])

    @staticmethod
    def export_range_csv(database, start_date, end_date, output_path):
        clicks = database.get_clicks_in_range(start_date, end_date)

        current = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        all_hourly = []
        while current < end_dt:
            day_str = current.strftime("%Y-%m-%d")
            hourly = database.get_hourly_stats(day_str)
            all_hourly.extend(hourly)
            current += timedelta(days=1)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "button", "x", "y"])
            for c in clicks:
                writer.writerow([c["timestamp"], c["button"], c["x"], c["y"]])

            writer.writerow([])
            writer.writerow(["--- RESUMO HORÁRIO ---"])
            writer.writerow([
                "hora", "total_cliques", "esquerdo", "direito",
                "meio", "ativo_min", "pausa_min"
            ])
            for h in all_hourly:
                writer.writerow([
                    h["hour_start"],
                    h["total_clicks"],
                    h["left_clicks"],
                    h["right_clicks"],
                    h["middle_clicks"],
                    h["active_seconds"] // 60,
                    h["pause_seconds"] // 60,
                ])
