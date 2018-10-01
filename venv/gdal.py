import csv
import sys, os
import shapefile as shp
import osgeo.ogr as ogr
import osgeo.osr as osr

# use a dictionary reader so we can access by field name
csv_opener = open('L:\\ADSB\\ADSB2017\\2letter\\20171113_nofilter_latlon.csv', 'rt')
reader = csv.DictReader(csv_opener,
                        delimiter=',',
                        quoting=csv.QUOTE_NONE)

# set up the shapefile driver
driver = ogr.GetDriverByName("ESRI Shapefile")

# create the data source
if os.path.exists('GPS_1113.shp'):
    driver.DeleteDataSource('GPS_1113.shp')

data_source = driver.CreateDataSource("GPS_1113.shp")
if data_source is None:
    print('Could not create file')
    sys.exit(1)

# create the spatial reference, WGS84
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

# create the layer
layer = data_source.CreateLayer("GPS_1113", srs, ogr.wkbLineString)

# Add the fields we're interested in
field_name = ogr.FieldDefn("FlightNo", ogr.OFTString)
field_name.SetWidth(24)
layer.CreateField(field_name)
layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Altitude", ogr.OFTReal))

for row in reader:
    current_flight = row['Flight No.']
    break

# reset DictReader
csv_opener.seek(0)
reader.__next__()

num = 0  # counter of current point in linestring
lineString = ogr.Geometry(ogr.wkbLineString)
# Process the text file and add the attributes and features to the shapefile
for row in reader:
    #     # create the feature
    feature = ogr.Feature(layer.GetLayerDefn())
    #     # Set the attributes using the values from the delimited text file
    feature.SetField("FlightNo", row['Flight No.'])
    feature.SetField("Latitude", row['Latitude'])
    feature.SetField("Longitude", row['Longitude'])
    feature.SetField("Altitude", row['Altitude [ft]'])

    # # create the WKT for the feature using Python string formatting
    # wkt = "POINT(%f %f)" %  (float(row['Longitude']) , float(row['Latitude']))

    if (row['Flight No.'] == current_flight):
        lineString.AddPoint(float(row['Longitude']), float(row['Latitude']), float(row['Altitude [ft]']))
        # lineString.AddPoint(x,y)
        num += 1
    else:
        # check if current flight is arriving/departing from airport or NOT
        if (((lineString.GetX(0) >= 105.779244 and lineString.GetX(0) <= 105.825756)
                or (lineString.GetX(num - 1) >= 105.779244 and lineString.GetX(num - 1) <= 105.825756))
                and ((lineString.GetY(0) >= 21.217667 and lineString.GetY(0) <= 21.223671)
                or (lineString.GetY(num - 1) >= 21.217667 and lineString.GetY(num - 1) <= 21.223671))):
            # Set the feature geometry using the point
            feature.SetGeometry(lineString)
            # Create the feature in the layer (shapefile)
            layer.CreateFeature(feature)

        print(str(current_flight))

        # Dereference the feature
        feature.Destroy()
        current_flight = row['Flight No.']
        lineString.Empty()
        num = 0
        lineString.AddPoint(float(row['Longitude']), float(row['Latitude']), float(row['Altitude [ft]']))
        num += 1

# Save and close the data source
data_source = None

print("Shapefile created")
