import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np
import os


def builCityGrid(gridSize, geoDF):
    cityGrid = np.empty((gridSize, gridSize), dtype=list)

    for insee, cityRow in geoDF.iterrows():
        #print(insee, cityRow['geometry'].bounds)
        if insee.startswith("97"):
            #print("DOM-TOM", insee)
            continue
        eastBorder =  int(gridSize*(cityRow['geometry'].bounds[2] - franceWest )/(franceEast-franceWest))
        westBorder =  int(gridSize*(cityRow['geometry'].bounds[0] - franceWest )/(franceEast-franceWest))
        southBorder = int(gridSize*(cityRow['geometry'].bounds[1] - franceSouth)/(franceNorth-franceSouth))
        northBorder = int(gridSize*(cityRow['geometry'].bounds[3] - franceSouth)/(franceNorth-franceSouth))
        #print(southBorder, northBorder, westBorder, eastBorder)
        for latitude in range(southBorder, northBorder+1):
            for longitude in range(westBorder, eastBorder+1):
                if not cityGrid[longitude, latitude]:
                    cityGrid[longitude, latitude] = [insee]
                else:
                    cityGrid[longitude, latitude].append(insee)
    return cityGrid


def getCityGridPosition(longitude, latitude, gridSize):
    gridLongitude = int(gridSize*(longitude - franceWest)/(franceEast-franceWest))
    gridLatitude = int(gridSize*(latitude - franceSouth)/(franceNorth-franceSouth))
    return gridLongitude, gridLatitude

def checkWithin(poly, point):
     return point.within(poly)
    
class NotInFranceError(Exception):
    pass

def findCity(longitude, latitude): #, cityGrid = None, geoDF = None, gridSize=1000
    global geoDF
    global cityGrid
    if cityGrid is None:
      if not os.path.exists(f"/dbfs/FileStore/geocode/cityGrid_{gridSize}.npy"):
        print("Need to build cities grid...", end="")
        cityGrid = builCityGrid(gridSize)
        np.save(f"/dbfs/FileStore/geocode/cityGrid_{gridSize}.npy", cityGrid)
        print("Done")
      else:
        cityGrid = np.load(f"/dbfs/FileStore/geocode/cityGrid_{gridSize}.npy", allow_pickle=True)
    
    point = Point(longitude, latitude)
    gridX, gridY = getCityGridPosition(longitude, latitude, cityGrid.shape[0])
    if gridX < 0 or gridX >= cityGrid.shape[0] or gridY < 0 or gridY >= cityGrid.shape[1]:
      return "-1", f"Outside of grid: longitude={longitude}, latitude={latitude}"
    
    citiesInGrid = cityGrid[gridX, gridY]
    if not citiesInGrid:
      #raise NotInFranceError(f"No city found in France, check your coordinates: longitude={longitude}, latitude={latitude}")
      return "-1", f"No city found in France, check your coordinates: longitude={longitude}, latitude={latitude}"
        
    gridGeoDF = geoDF.loc[citiesInGrid]
    cityRow = gridGeoDF.loc[gridGeoDF.geometry.apply(checkWithin, args=(point,))]
    
    if len(cityRow) == 0:
      #raise NotInFranceError(f"No city found in France, check your coordinates: longitude={longitude}, latitude={latitude}")
      return "-1", f"No city found in France, check your coordinates: longitude={longitude}, latitude={latitude}"
    return cityRow.index.values[0], cityRow['nom'][0]


  
# loading module variables

franceWest  = -5.134494
franceNorth = 51.115007
franceEast  = 9.618623619165001
franceSouth = 41.364294

geoDF = gpd.read_file("/dbfs/FileStore/geocode/communes_20210101.shp")
geoDF = geoDF.set_index("insee").sort_values(by="nom")

if os.path.exists("/dbfs/FileStore/geocode/cityGrid_1000.npy"):
  cityGrid = np.load("/dbfs/FileStore/geocode/cityGrid_1000.npy", allow_pickle=True)
else:
  print("Need to build cities grid...", end="")
  cityGrid = builCityGrid(1000)
  np.save("/dbfs/FileStore/geocode/cityGrid_1000.npy", cityGrid)
  print("Done")