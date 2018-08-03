import csv
import sys,os
import shapefile as shp
import osgeo.ogr as ogr
import osgeo.osr as osr

# use a dictionary reader so we can access by field name
reader = csv.DictReader(open('L:\\ADSB\\ADSB2017\\2letter\\1113_filtered.csv', 'rt'),
    delimiter=',',
    quoting=csv.QUOTE_NONE)

# set up the shapefile driver
driver = ogr.GetDriverByName("ESRI Shapefile")

# create the data source
if os.path.exists('GPS_1113_filtered_latlon.shp'):
  driver.DeleteDataSource('GPS_1113_filtered_latlon.shp')

data_source = driver.CreateDataSource("GPS_1113_filtered_latlon.shp")
if data_source is None:
  print('Could not create file')
  sys.exit(1)

# create the spatial reference, WGS84
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

# create the layer
layer = data_source.CreateLayer("GPS_1113_filtered_latlon", srs, ogr.wkbLineString)

# Add the fields we're interested in
field_name = ogr.FieldDefn("Code", ogr.OFTString)
field_name.SetWidth(24)
layer.CreateField(field_name)
layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))

for row in reader:
    current_code = row['Code']
    break

lineString = ogr.Geometry(ogr.wkbLineString)
# Process the text file and add the attributes and features to the shapefile
for row in reader:
#     # create the feature
    feature = ogr.Feature(layer.GetLayerDefn())
#     # Set the attributes using the values from the delimited text file
    feature.SetField("Code", row['Code'])
    feature.SetField("Latitude", row['Latitude'])
    feature.SetField("Longitude", row['Longitude'])

    # # create the WKT for the feature using Python string formatting
    # wkt = "POINT(%f %f)" %  (float(row['Longitude']) , float(row['Latitude']))

    if (row['Code'] == current_code):
        lineString.AddPoint(float(row['Longitude']), float(row['Latitude']))
    # lineString.AddPoint(x,y)
    # print(lineString)

    else:
        # Set the feature geometry using the point
        feature.SetGeometry(lineString)

        print(str(current_code))
        print(lineString)

        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
    # print(feature)
    # Dereference the feature
        feature.Destroy()
        current_code = row['Code']
        lineString.Empty()
        lineString.AddPoint(float(row['Longitude']), float(row['Latitude']))

# Save and close the data source
data_source = None

print ("Shapefile created")