#########################################
##### Name: Spandan Sharma          #####
##### Uniqname: spandans            #####
#########################################

import json
import requests
import numpy as np  
import matplotlib.pyplot as plt 
import matplotlib  
import random as random 
from matplotlib.path import Path 

baseUrl = "https://dsl.richmond.edu/panorama/redlining/static/downloads/geojson/MIDetroit1939.geojson"
respAPI = requests.get(baseUrl)

RedliningData = respAPI.json()

json_object = json.dumps(RedliningData, indent=2)
with open("hw4_spandans.json", "w") as outfile:
    outfile.write(json_object)

# data["features"] -> loop through dicts -> for each dict, get dict["geometry"] -> 
# get dict["geometry"]["coordinates"] -> add to list

class DetroitDistrict:
    '''write something HELLO ---------- ---------- ----------'''
    gradeColorMap = {"A":"darkgreen", "B":"cornflowerblue","C":"gold","D":"maroon"}
    
    def __init__(self, jsonObj, name = -1):
        self.Coordinates = jsonObj["geometry"]["coordinates"][0][0]
        self.HolcGrade = jsonObj["properties"]["holc_grade"]
        self.HolcColor = self.gradeColorMap.get(self.HolcGrade,"invalid grade")
        self.name = name
        self.qualitativeDescription = jsonObj["properties"]["area_description_data"]["8"]
        self.RandomLat = 0
        self.RandomLong = 0
        self.MedianIncome = 0
        self.CensusTract = ""

    def __repr__(self):
        return str(self.name) + " : " + self.qualitativeDescription

Districts = [DetroitDistrict(district,counter) for counter, district in enumerate(RedliningData["features"])]
 
'''Part 3: Plotting the map of Detroit using Matlab Polygons'''

fig, ax = plt.subplots() 
 
for district in Districts: # what kind of for loop makes sense?  
  ax.add_patch(plt.Polygon(district.Coordinates, facecolor = district.HolcColor, edgecolor='black')) # add arguments here 
  ax.autoscale() 
  plt.rcParams["figure.figsize"] = (15,15)   
 
# plt.show() #UNCOMMENT THIS LATER

'''Part 4: Picking latitudes and longitudes from each district'''
random.seed(17) # initialize the random generator
 
xgrid = np.arange(-83.5,-82.8,.004)  # create x,y axis grids with range and step size given
ygrid = np.arange(42.1, 42.6, .004) 
xmesh, ymesh = np.meshgrid(xgrid,ygrid) # create the actual grid/mesh
 
points = np.vstack((xmesh.flatten(),ymesh.flatten())).T # create a 2d list/matrix and take its transpose
# key = "0515d91b36ee7273ac64989377f8ecc93f7b21df"

for j in Districts: 
    p = Path(j.Coordinates)  
    grid = p.contains_points(points)  
    print(j," : ", points[random.choice(np.where(grid)[0])])  
    point = points[random.choice(np.where(grid)[0])] # choose random coordinates within district polygon
    j.RandomLong = point[0] # assign values
    j.RandomLat = point[1] 
    apiUrl = "https://geo.fcc.gov/api/census/block/find?latitude=" + str(j.RandomLat) + "&longitude=" + str(j.RandomLong) + "&censusYear=2010&showall=true&format=json"
    respCensusApi = requests.get(apiUrl)
    respCensusApiJson = respCensusApi.json()
    tractCode = respCensusApiJson["Block"]["FIPS"]
    j.CensusTract = tractCode[-6:] # getting last 6 digits of fips code [-6]
    censusUrl = "https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:{tract}&in=state:{state}%20county:{county}&key=0515d91b36ee7273ac64989377f8ecc93f7b21df".format(tract=tractCode[5:11], state=tractCode[0:2], county=tractCode[2:5])
    median_income = int(requests.get(censusUrl).json()[1][0])
    j.MedianIncome = median_income
    