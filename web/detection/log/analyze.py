import pandas as pd

aggregation_levels = {
    "day": ["ip_address", "date"],
    "hour": ["ip_address", "date", "hour"],
}


def get_session_attributes(df, aggregation_level="hour"):

    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour

    aggregation_columns = aggregation_levels[aggregation_level]

    df = df.sort_values(by=aggregation_columns + ["time"], ascending=True)
    df["time_previous"] = df.groupby(aggregation_columns)["time"].shift(1)

    df["time_previous"] = df["time_previous"].fillna(df["time"])

    df["time_previous"] = pd.to_datetime(df["time_previous"])
    df["request_time_delta"] = (df["time"] - df["time_previous"]).dt.total_seconds()

    aggregated_df = (
        df.groupby(aggregation_columns)
        .agg(
            number_requests_total=pd.NamedAgg(
                column="id",
                aggfunc="count",
            ),
            number_requests_GET=pd.NamedAgg(
                column="method",
                aggfunc=(lambda req: (req.str.startswith("GET")).sum()),
            ),
            number_requests_HEAD=pd.NamedAgg(
                column="method",
                aggfunc=(lambda req: (req.str.startswith("HEAD")).sum()),
            ),
            number_requests_POST=pd.NamedAgg(
                column="method",
                aggfunc=(lambda req: (req.str.startswith("POST")).sum()),
            ),
            number_requests_PATCH=pd.NamedAgg(
                column="method",
                aggfunc=(lambda req: (req.str.startswith("PATCH")).sum()),
            ),
            number_requests_PUT=pd.NamedAgg(
                column="method",
                aggfunc=(lambda req: (req.str.startswith("PUT")).sum()),
            ),
            avg_request_interarrival_time=pd.NamedAgg(
                column="request_time_delta",
                aggfunc="mean",
            ),
            std_dev_request_interarrival_time=pd.NamedAgg(
                column="request_time_delta",
                aggfunc="std",
            ),
            number_requests_no_referrer=pd.NamedAgg(
                column="referrer",
                aggfunc=(lambda req: (req.isna()).sum()),
            ),
            number_requests_no_user_agent=pd.NamedAgg(
                column="user_agent",
                aggfunc=(lambda req: (req.isna()).sum()),
            ),
            number_requests_get_static=pd.NamedAgg(
                column="path",
                aggfunc=(lambda req: (req.str.startswith("/static")).sum()),
            ),
        )
        .reset_index()
    )

    aggregated_df["HEAD_requests_ratio"] = (
        aggregated_df["number_requests_HEAD"] / aggregated_df["number_requests_total"]
    )
    aggregated_df["GET_requests_ratio"] = (
        aggregated_df["number_requests_GET"] / aggregated_df["number_requests_total"]
    )
    aggregated_df["POST_requests_ratio"] = (
        aggregated_df["number_requests_POST"] / aggregated_df["number_requests_total"]
    )
    aggregated_df["no_user_agent_requests_ratio"] = (
        aggregated_df["number_requests_no_user_agent"]
        / aggregated_df["number_requests_total"]
    )
    aggregated_df["get_static_requests_ratio"] = (
        aggregated_df["number_requests_get_static"]
        / aggregated_df["number_requests_total"]
    )

    return aggregated_df
