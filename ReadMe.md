# Denver Real Estate

## Problem Statement
Can we identify real estate properties that are showing high likelihood to be "fixer" homes, which should be lower cost but require significant work? Can we project home costs, and potentially repair/remodel costs to see overall net price? Goal is to be able to identify homes, and then project total cost of move-in.

## Data Sources

### 1. Zillow Data
Webscraping Zillow listings via smaller queries on geographic locations. Each query can show up to 40 properties on the screen which get grabbed by the spider and added to overall dataframe. If record is not net new, no duplicate entry is made in the database at this time.

### 2. Education Data

https://www.schooldigger.com/go/CO/districtrank.aspx

https://datalab.cde.state.co.us/cognos/bi/?perspective=classicviewer&pathRef=.public_folders%2FState+Assessment+Data+Lab%2FState+Assessment+Data+Lab&id=i68C28829B9DE44C998B011AC31EAF441&objRef=i68C28829B9DE44C998B011AC31EAF441&type=report&format=HTML&Download=false&prompt=true&cmProperties%5Bid%5D=i68C28829B9DE44C998B011AC31EAF441&cmProperties%5BdefaultName%5D=State+Assessment+Data+Lab&cmProperties%5Btype%5D=report&cmProperties%5Bpermissions%5D%5B%5D=execute&cmProperties%5Bpermissions%5D%5B%5D=read&cmProperties%5Bpermissions%5D%5B%5D=traverse

### 3. Physical Environment Data

https://www.americashealthrankings.org/explore/annual/measure/physical_environment/state/CO?edition-year=2021

### 4. Air Quality Data

https://coepht.colorado.gov/air-quality-data

### 5. Climate Data

https://coepht.colorado.gov/climate-data

### 6. Primary Care Physician Ratio Data

https://www.countyhealthrankings.org/app/colorado/2022/measure/factors/4/data

## Models (In Production or Development)

### 1. Customer Interest Model
Model Customer Interest in property on scale of 1-10, with 10 being the most likely a customer is interested. Model score to then be used in plotting potential locations on map.

### 2. "Fixer" Identification Model


### 3. Price Model

### 4. Repair Estimate Model


