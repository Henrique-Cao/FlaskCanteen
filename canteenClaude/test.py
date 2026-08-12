from datetime import datetime, timedelta
import random
def generate_time_series_data():
    now = datetime.now()
    return [
        {
            "x": (now - timedelta(days=i)).strftime("%Y-%m-%d"),
            "y": random.randint(20, 100)
        }
        for i in range(14, 0, -1)
    ]

print(generate_time_series_data())