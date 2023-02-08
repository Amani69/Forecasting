from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import Window


#fonction pour calculer la distance
def get_distance(longit_a, latit_a, longit_b, latit_b):
  if longit_a is None or latit_a is None or longit_b is None or latit_b is None:
    return 0
  # Transform to radians
  longit_a, latit_a, longit_b, latit_b = map(radians, [longit_a, latit_a, longit_b, latit_b])
  dist_longit = longit_b - longit_a
  dist_latit = latit_b - latit_a
  # Calculate area
  area = sin(dist_latit / 2) ** 2 + cos(latit_a) * cos(latit_b) * sin(dist_longit / 2) ** 2
  # Calculate the central angle
  central_angle = 2 * asin(sqrt(area))
  radius = 6371
  # Calculate Distance in km
  distance = (central_angle * radius)
  return abs(distance)




