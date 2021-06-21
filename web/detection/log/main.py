from analyze import get_session_attributes
from parse import parse_log_file

df = parse_log_file("access.log")

aggregated_by_hour_df = get_session_attributes(df, aggregation_level="hour")
print(
    aggregated_by_hour_df[
        [
            "host",
            "date",
            "hour",
            "number_requests_total",
            "avg_request_interarrival_time",
        ]
    ]
)
print(
    aggregated_by_hour_df[
        [
            "host",
            "date",
            "hour",
            "HEAD_requests_ratio",
            "GET_requests_ratio",
            "POST_requests_ratio",
            "no_referrer_requests_ratio",
            "no_user_agent_requests_ratio",
            "requests_has_user_agent_contains_phantom_ratio",
        ]
    ]
)
