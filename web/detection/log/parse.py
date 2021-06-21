import re
from datetime import datetime

import pandas as pd


def parse_log_file(path):
    data = {
        "host": [],
        "time": [],
        "date": [],
        "hour": [],
        "request": [],
        "status": [],
        "size": [],
        "referrer": [],
        "user_agent": [],
    }
    with open(path, "r") as file:
        lines = file.readlines()
        for line in reversed(lines):
            request = parse_line(line)

            if request:
                parsed_date = datetime.strptime(
                    request["time"][:-6], "%d/%b/%Y:%H:%M:%S"
                )
                date = datetime(parsed_date.year, parsed_date.month, parsed_date.day)
                data["host"].append(request["host"])
                data["time"].append(parsed_date)
                data["request"].append(request["request"])
                data["hour"].append(parsed_date.hour)
                data["date"].append(date)
                data["status"].append(request["status"])
                data["size"].append(request["size"])
                data["referrer"].append(request["referrer"])
                data["user_agent"].append(request["agent"])

            else:
                continue
    return pd.DataFrame(data)


def parse_line(log_line):
    parts = [
        r"(?P<host>\S+)",  # host %h
        r"\S+",  # indent %l (unused)
        r"(?P<user>\S+)",  # user %u
        r"\[(?P<time>.+)\]",  # time %t
        r'"(?P<request>.*)"',  # request "%r"
        r"(?P<status>[0-9]+)",  # status %>s
        r"(?P<size>\S+)",  # size %b (careful, can be '-')
        r'"(?P<referrer>.*)"',  # referrer "%{Referer}i"
        r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
    ]
    pattern = re.compile(r"\s+".join(parts) + r"\s*\Z")
    matched = pattern.match(log_line)
    if matched is not None:
        return matched.groupdict()
    else:
        pattern = re.compile(r"\s+".join(parts[0:-2]) + r"\s*\Z")
        matched = pattern.match(log_line)
        if matched is not None:
            request_data = matched.groupdict()
            request_data["referrer"] = "-"
            request_data["agent"] = "-"
            return request_data
        else:
            return None
