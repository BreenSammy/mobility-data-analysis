# MDA Praktikum

# Dataset

GPS log files of two users, labeled trajectories with transportation mode

## 00inf.txt

Metdata file comprising information about the recording

| Line   | Description          | Unit     |
|--------|----------------------|----------|
| 1      | User ID              | -        |
| 2      | First sample time    | ms       |
| 3      | Last sample time     | ms       |
| 4      | Recording start date | -        |
| 5      | Recording length     | ms       |
| 6      | Recording ID         | -        |

## Torso_Location.txt

| Column | Description                                          | Unit     |
|--------|------------------------------------------------------|----------|
| 1      | Time                                                 | ms       |
| 2      | Ignore                                               | -        |
| 3      | Ignore                                               | -        |
| 4      | Accuracy of this location (radius of 68% confidence) | m        |
| 5      | Latitude                                             | degrees  |
| 6      | Longitude                                            | degrees  |
| 7      | Altitude                                             | m        |

## Torso_Motion.txt

GPS data

| Column | Description                   | Unit    |
|--------|-------------------------------|---------|
| 1      | Time                          | ms      |
| 2      | Acceleration X                | m/s²    |
| 3      | Acceleration Y                | m/s²    |
| 4      | Acceleration Z                | m/s²    |
| 5      | Gyroscope X                   | rad/s   |
| 6      | Gyroscope Y                   | rad/s   |
| 7      | Gyroscope Z                   | rad/s   |
| 8      | Magnetometer X                | μT      |
| 9      | Magnetometer Y                | μT      |
| 10     | Magnetometer Z                | μT      |
| 11     | Orientation w                 | -       |
| 12     | Orientation X                 | -       |
| 13     | Orientation Y                 | -       |
| 14     | Orientation Z                 | -       |
| 15     | Gravity X                     | m/s²    |
| 16     | Gravity Y                     | m/s²    |
| 17     | Gravity Z                     | m/s²    |
| 18     | Linear acceleration X         | m/s²    |
| 19     | Linear acceleration Y         | m/s²    |
| 20     | Linear acceleration Z         | m/s²    |
| 21     | Pressure                      | hPa     |
| 22     | Altitude (derived from pressure) | m    |


## labels_track_main.txt

| Column | Description                   | Unit    |
|--------|-------------------------------|---------|
| 1      | Label start time              | ms      |
| 2      | Label end time                | ms      |
| 3      | Activity label                | int     |

### Labels 

| Label | Description           |
|-------|-----------------------|
| 0     | Still; Stand; Outside |
| 1     | Still; Stand; Inside  |
| 2     | Still; Sit; Outside   |
| 3     | Still; Sit; Inside    |
| 4     | Walking; Outside      |
| 5     | Walking; Inside       |
| 6     | Run                   |
| 7     | Bike                  |
| 8     | Car; Driver           |
| 9     | Car; Passenger        |
| 10    | Bus; Stand            |
| 11    | Bus; Sit              |
| 12    | Bus; Up; Stand        |
| 13    | Bus; Up; Sit          |
| 14    | Train; Stand          |
| 15    | Train; Sit            |
| 16    | Subway; Stand         |
| 17    | Subway; Sit           |