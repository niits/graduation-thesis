from datetime import timedelta

import numpy as np


def extract_feature(df):
    if len(df.values) < 3:
        raise ValueError("")

    list_of_pauses = pauseslist(df)
    allangles = angle_of_movement(df)
    var = curvature(df)
    speed_mean, speed_std = calculate_speeds(df)
    features = np.array(
        [
            mean_angle_of_movement(allangles),
            speed_mean,
            speed_std,
            mean_curvature(var),
            efficiency(df),
            regularity(df),
            total_change_in_angle(df),
            num_of_pauses(list_of_pauses),
            df.shape[0],
            df["timestamp"].max() - df["timestamp"].min(),
        ]
    )
    return features


def time(df):
    time_vector = np.array([])
    for i in range(len(df) - 1):
        time = df.iloc[i]["timestamp"]
        time_vector = np.append(time_vector, time)
    return time_vector


def delta_theta(no_rows, df):
    summation_deltatheta = 0
    for i in range(no_rows + 1):
        delta_x = df.iloc[i + 1]["x_client"] - df.iloc[i]["x_client"]
        delta_y = df.iloc[i + 1]["y_client"] - df.iloc[i]["y_client"]
        if delta_x == 0 and delta_y == 0:
            delta_thetavalue = 0 + 360
            summation_deltatheta += delta_thetavalue
        elif delta_x == 0:
            delta_thetavalue = 90 + 360
            summation_deltatheta += delta_thetavalue
        else:
            delta_thetavalue = np.arctan(delta_y / delta_x) + 360
            summation_deltatheta += delta_thetavalue
    return summation_deltatheta


def angle_of_movement(df):
    totalanglemovement = np.array([])
    for i in range(len(df) - 1):
        angle_movement = np.arctan2(
            df.iloc[i + 1]["y_client"] - df.iloc[i]["y_client"],
            df.iloc[i + 1]["x_client"] - df.iloc[i]["x_client"],
        )
        totalanglemovement = np.append(totalanglemovement, angle_movement * 180 / np.pi)
    return totalanglemovement


def mean_angle_of_movement(var):
    mean_angle_of_movementvalue = np.mean(var)
    return mean_angle_of_movementvalue


# Curvature


def diff_theta(x1, x2, y1, y2):
    delta_x = x2 - x1
    delta_y = y2 - y1
    if delta_y == 0 and delta_x == 0:
        distance = 1
        theta = 0 + 360
        diff_thetavalue = np.divide(theta, distance)
    elif delta_x == 0:
        s = (y2 - y1) ** 2
        distance = np.sqrt(s)
        theta = 90 + 360
        diff_thetavalue = np.divide(theta, distance)
    else:
        s = (x2 - x1) ** 2 + (y2 - y1) ** 2
        distance = np.sqrt(s)
        theta = np.arctan(delta_y / delta_x) + 360
        diff_thetavalue = np.divide(theta, distance)
    return diff_thetavalue


def curvature(df):
    curvature_vector = np.array([])
    for i in range(len(df) - 1):
        a = df.iloc[i + 1]["x_client"]
        b = df.iloc[i]["x_client"]
        c = df.iloc[i + 1]["y_client"]
        d = df.iloc[i]["y_client"]
        curvatureval = diff_theta(a, b, c, d)
        curvature_vector = np.append(curvature_vector, curvatureval)
    return curvature_vector


def mean_curvature(var):
    mean_curvatureval = np.mean(var)
    return mean_curvatureval


# This varies between 0 and 1 where 1 is
# equal to the shortest path between the initial point and final point
# It may be noted that generally humans have poor efficiency and bots have high efficiency and hence
# this may be very useful in differentiating between the two from mouse movements
def efficiency(df):
    max_x = df.iloc[len(df) - 1]["x_client"]
    max_y = df.iloc[len(df) - 1]["y_client"]
    init_x = df.iloc[0]["x_client"]
    init_y = df.iloc[0]["y_client"]
    sqrt_x = np.square(max_x - init_x)
    sqrt_y = np.square(max_y - init_y)
    best_dist = np.sqrt(sqrt_x + sqrt_y)
    sum_of_distances = 0
    for j in range(len(df) - 1):
        sum_of_distances += np.sqrt(
            np.square(df.iloc[j + 1]["x_client"] - df.iloc[j]["x_client"])
            + np.square(df.iloc[j + 1]["y_client"] - df.iloc[j]["y_client"])
        )

    final_efficiency = np.divide(best_dist, sum_of_distances) if sum_of_distances else 0
    return final_efficiency


def meandistance(df):
    temp_x = 0
    temp_y = 0
    for l in range(len(df)):
        temp_x += df.iloc[l]["x_client"]
        temp_y += df.iloc[l]["y_client"]
    mean_x = np.divide(temp_x, len(df))
    mean_y = np.divide(temp_y, len(df))
    meanboth = np.array([mean_x, mean_y])
    return meanboth


def distancefromcentre(mean_xy, current_xy):
    return np.sqrt(
        np.square(current_xy[0] - mean_xy[0]) + np.square(current_xy[1] - mean_xy[1])
    )


# Regularity is higher for bots as they might mostly move straight to the target
def regularity(df):
    temp_distance = 0
    distance_of_centre = meandistance(df)
    for u in range(len(df)):
        current_point = np.array([df.iloc[u]["x_client"], df.iloc[u]["y_client"]])
        temp_distance += distancefromcentre(distance_of_centre, current_point)
    mean_of_the_distances = np.divide(temp_distance, len(df))
    tempdeviation = 0
    for t in range(len(df)):
        current_point = np.array([df.iloc[u]["x_client"], df.iloc[u]["y_client"]])
        tempdeviation += np.square(
            distancefromcentre(distance_of_centre, current_point)
            - mean_of_the_distances
        )
    std_deviation_square = np.divide(tempdeviation, len(df))
    std_deviation = np.sqrt(std_deviation_square)
    final_path = np.divide(
        mean_of_the_distances, (mean_of_the_distances + std_deviation)
    ) if (mean_of_the_distances + std_deviation) else 1
    return final_path


# Denotes the total number of pauses in a session. A poorly designed bot that mimics the mouse
# may be easily caught with the help of this metric
def pauseslist(df):
    pauses = np.array([])
    for h in range(len(df) - 1):
        timediff = df.iloc[h + 1]["timestamp"] - df.iloc[h]["timestamp"]
        if (
            timediff.total_seconds() if isinstance(timediff, timedelta) else timediff
        ) > 0.03:  # Here, we use the standard value accepted in HCI for a pause i.e. 0.1
            pauses = np.append(pauses, timediff)
        else:
            pauses = np.append(pauses, 0)
    return pauses


def num_of_pauses(list_of_pauses):
    countpauses = 0
    for h in range(len(list_of_pauses)):
        if list_of_pauses[h] != 0:
            countpauses += 1
    return countpauses


def total_change_in_angle(df):
    finalangle = np.arctan2(
        df.iloc[len(df) - 1]["y_client"], df.iloc[len(df) - 1]["x_client"]
    )
    firstangle = np.arctan2(df.iloc[0]["y_client"], df.iloc[0]["x_client"])
    return (finalangle - firstangle) * 180 / np.pi

def calculate_speeds(positions_over_time):

    movements_over_timesteps = (
        np.roll(positions_over_time, -1, axis=0)
        - positions_over_time)[:-1]

    speeds = np.sqrt(
        movements_over_timesteps['x_client'] ** 2 +
        movements_over_timesteps['y_client'] ** 2
    ) / movements_over_timesteps['timestamp']

    return speeds.mean(), speeds.std()