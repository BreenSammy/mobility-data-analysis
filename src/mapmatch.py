import pandas as pd
import requests
import ast
from shapely import Point


def mapmatch(df: pd.DataFrame):
    MAGIS_BASE_URL = "http://gis.ftm.mw.tum.de"
    mapmatch_query_template = "/match?coordinates={coordinate_list}&time={time_list}"

    coordinate_list = df.geometry.apply(lambda x: (x.y, x.x))
    coordinate_list = coordinate_list.values
    coordinate_list = [
        coordinate
        for coordinate_tuple in coordinate_list
        for coordinate in coordinate_tuple
    ]

    # time_list = df.index.to_series().values
    # time_list_str = str(list(time_list))
    output_time_format = "%Y-%m-%d %H:%M:%S"
    time_list = (
        df.index.to_series().apply(func=lambda x: x.strftime(output_time_format)).values
    )
    # Convert the output to a string and remove all apostrophes
    time_list = list(time_list)
    time_list_str = str(list(time_list)).replace("'", "")

    # splitting list into 4 equally long lists to ensure stability
    coordinate_list_split, time_list_split = split_lists(coordinate_list, time_list)

    matched_points_list = []

    for index in range(0, len(coordinate_list_split)):
        time_list_split_str = str(time_list_split[index]).replace("'", "")
        mapmatch_query = MAGIS_BASE_URL + mapmatch_query_template.format(
            coordinate_list=coordinate_list_split[index], time_list=time_list_split_str
        )
        response_mapmatch = requests.get(mapmatch_query)
        print(response_mapmatch.text)
        response_dict = ast.literal_eval(response_mapmatch.text.replace("\n", ""))
        if response_dict["code"] != "Error":
            mapmatch = response_mapmatch.json()

            matched_locations = mapmatch["matched_locations"]
            matched_points = [
                Point(coordinates[1], coordinates[0])
                for coordinates in matched_locations
            ]
            matched_points_list.append(matched_points)
        else:
            # use existing coordinates instead
            existingcoordinates = []
            for i in range(0, len(coordinate_list_split[index]), 2):
                existingcoordinates.append(
                    (
                        coordinate_list_split[index][i],
                        coordinate_list_split[index][i + 1],
                    )
                )

    # matched_nodes = mapmatch["nodes"]
    # gpd = gpd.GeoDataFrame(geometry=matched_points)
    # line = LineString(matched_points)

    df["geometry"] = matched_points_list

    return df


def split_lists(list_a, list_b):
    # Validate the lengths
    if len(list_a) != 2 * len(list_b):
        raise ValueError("Length of list_a should be twice the length of list_b")

    # Find divisors of len(list_b) that are odd
    def odd_divisors(n):
        divisors = []
        for i in range(
            1, n // 2 + 1, 2
        ):  # step by 2 starting from 1 to only consider odd numbers
            if n % i == 0:
                divisors.append(i)
        return divisors

    divisors_b = odd_divisors(len(list_b))

    if not divisors_b:
        raise ValueError("Cannot find suitable odd divisor for list_b")

    # Choose a divisor (for this example, I'm choosing the largest odd divisor)
    divisor_b = divisors_b[len(divisors_b) - 2]

    # Split list_b using divisor_b
    sublists_b = [list_b[i : i + divisor_b] for i in range(0, len(list_b), divisor_b)]

    # Split list_a using 2*divisor_b
    sublists_a = [
        list_a[i : i + 2 * divisor_b] for i in range(0, len(list_a), 2 * divisor_b)
    ]

    return sublists_a, sublists_b
