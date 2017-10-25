# Graphic Explanation of Globally Unique Identifiers (GUIDs) in the CR Spatial Data Transfer Standards

Each representation of any feature--whether a point, line or polygon--has its own "Locational GUID", or `GEOM_ID`. After that, each physically distinct cultural resource has its own "Cultural Resource GUID", or `CR_ID`. Finally, all various representations of the same CLI feature will have the same "Analysis Evaluation Feature Identification Number", or `CLI_ID`, which is an existing 6-digit identifier stored in the CLI for each feature. The following is a graphical illustration of this system, and how it would work given several different feature examples.

_note: A GUID looks something like: C84087D5-E035-4275-8E3C-444617049CC0_


#### Olson Well
![Olson Well](https://github.com/legiongis/clitoolbox/raw/master/docs/img/OlsonWell.JPG "Olson Well")


#### Hans Halseth House
![Hans Halseth House](https://github.com/legiongis/clitoolbox/raw/master/docs/img/HansHalsethHouses.JPG "Halseth House")


#### Sugar Maple Trees
![Sugar Maple Trees](https://github.com/legiongis/clitoolbox/raw/master/docs/img/SugarMapleTrees.JPG "Sugar Maple Trees")


#### Fences
![Fences](https://github.com/legiongis/clitoolbox/raw/master/docs/img/Fences.JPG "Fences")


#### Barn, Milkhouse and Retaining Wall 
_note: composite features like this are found in the CLI from time to time_

  ![Barn, Milkhouse and Retaining Wall](https://github.com/legiongis/clitoolbox/raw/master/docs/img/BarnMilkhs.JPG "Barn, Milkhouse")

