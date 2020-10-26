#! /usr/bin/env python
#
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from math import cos
from math import sqrt

if len(sys.argv) != 2:
    print("usage: gpx_analyze.py GPX_FILE")
    sys.exit(1)

tree = ET.parse(sys.argv[1])
trkpts = tree.getroot().findall(".//{http://www.topografix.com/GPX/1/1}trkpt")
ntrk = len(trkpts)
start_time = trkpts[0].find(".//{http://www.topografix.com/GPX/1/1}time").text
start_date = datetime.fromisoformat(start_time[0: len(start_time) - 1])
end_time = trkpts[ntrk - 1].find(".//{http://www.topografix.com/GPX/1/1}time").text
end_date = datetime.fromisoformat(end_time[0: len(end_time) - 1])
elapsed_time = (end_date - start_date).total_seconds()
elapsed_hrs = int(elapsed_time / 3600)
elt=elapsed_time - (elapsed_hrs * 3600)
elapsed_mins=int(elt / 60)
elt -= elapsed_mins * 60
elapsed_secs = elt
PI_RAD = float(3.141592653589793 / 180.)
POLAR_FEET_PER_DEGREE = float(363996.911486963)
EQUATORIAL_FEET_PER_DEGREE = float(365221.427229593)
lat_vals = [(0, 0), (0, 0)]
lon_vals = [(0, 0), (0, 0)]
vidx = 0
total_dist = float(0.)
for trkpt in trkpts:
    lat_s = trkpt.attrib["lat"]
    idx = lat_s.find(".")
    lat_s = lat_s.replace('.', '')
    lat_s_prec = len(lat_s) - idx
    lon_s = trkpt.attrib["lon"]
    idx = lon_s.find(".")
    lon_s = lon_s.replace('.', '')
    lon_s_prec = len(lon_s) - idx
    lat_vals[vidx] = (float(lat_s), lat_s_prec)
    lon_vals[vidx] = (float(lon_s), lon_s_prec)
    last_vidx = vidx
    vidx = 1 - vidx
    if lat_vals[vidx][0] != 0:
        curr_val = lat_vals[last_vidx][0]
        curr_prec = lat_vals[last_vidx][1]
        last_val = lat_vals[vidx][0]
        last_prec = lat_vals[vidx][1]
        while curr_prec < last_prec:
            curr_val *= 10
            curr_prec += 1
        while last_prec < curr_prec:
            last_val *= 10
            last_prec += 1
        lat2 = curr_val / pow(10., curr_prec)
        lat1 = last_val / pow(10., curr_prec)
        lat_diff = lat2 - lat1
        avg_lat = (lat2 + lat1) / 2.
        lat_dist = abs(lat_diff * POLAR_FEET_PER_DEGREE)
        curr_val = float(lon_vals[last_vidx][0])
        curr_prec = lon_vals[last_vidx][1]
        last_val = float(lon_vals[vidx][0])
        last_prec = lon_vals[vidx][1]
        while curr_prec < last_prec:
            curr_val *= 10
            curr_prec += 1
        while last_prec < curr_prec:
            last_val *= 10
            last_prec += 1
        lon_diff = (float(curr_val) - float(last_val)) / pow(10., curr_prec)
        lon_dist = abs(lon_diff * EQUATORIAL_FEET_PER_DEGREE) * cos(avg_lat * PI_RAD)
        total_dist += sqrt((lat_dist * lat_dist) + (lon_dist * lon_dist))
total_dist /= 5280.
pace = elapsed_time / 60. / total_dist
pace_mins = int(pace)
pace_secs = (pace - pace_mins) * 60.
equiv_5k_time = pace * 3.10685596118667
e5k_mins = int(equiv_5k_time)
e5k_secs = (equiv_5k_time - e5k_mins) * 60.

# print
print("Number of track points: ", ntrk)
print("Start time:             ", start_time)
print("End time:               ", end_time)
print("Elapsed time:            {0} seconds ({1}:{2:02}:{3:0.3f})".format(elapsed_time, elapsed_hrs, elapsed_mins, elapsed_secs))
print("Approximate resolution:  {0:.3f} seconds".format(elapsed_time / ntrk))
print("Total distance:          {0:.3f} mi".format(total_dist))
print("Pace:                    {0:02}:{1:0.3f} /mi".format(pace_mins, pace_secs))
print("Equivalient 5K time:     {0:02}:{1:0.3f}".format(e5k_mins, e5k_secs))
