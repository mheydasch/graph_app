# graph_app

This tool is intended to be used for exploration of microscopy data.
It provides you with the ability to load data, make graphs from it and display the images the data relates to
while hovering over individual lines on the graphs.


To start the app open your terminal and navigate to the folder holding the files by 
cd /[...]/graph_app
Then start the app by launching it with python from the terminal by typing
python3 app_launcher.py
Progress will be printed to the terminal, as well as the URL the app will be launched on.
Running on http://127.0.0.1:8050/
Copy this URL to your browser and hit enter. 



Your data should be organized the following way:
A .csv file in long format with columns for:
Data (can be multiple columns)
Timepoint(should be starting from 0)
Unique ID of each object
A classifier for the different groups.


The naming of these columns is irrelevant. Though default naming exists, you can manually select which column 
represents which category in the app.

If your data has different but consistent namings and you want to change the default values 
you need to set the value parameters of the dropdown menus in the file menu_definitions.py to your naming.
These dropdown menus are
classifier_choice()
identifier_selector()
timepoint_selector()
data_selector()

In it's current version the app is only optimized for data representing cell migration in two dimensions.

The software is currently optimized for the unique id having the following format:
W{}_S{}_E{}.format(wellname, FoV name, TrackID). 
This is relevant for finding the associated images.
To make changes to this format edit the key pattern variable in the function update_images() in the file app_launcher.py.

Your filename needs to contain the unique ID to be associated to the data.

You can choose to display two sets of graphs: Either lineplots, where each line represents the migration
track of an individual cell, or two boxplots showing the total migrated distance and the persistence of migration.
The plots are seperated based on the given classifier.




To display plots, upload your csv file with the first upload button either by drag and drop, or by selecting
it's location.
This will also display the file as a table, in the app.
Select which columns are holding which information.
Select what plot you want to generate.
Select the filters for the minimum time a cell needs to be tracked and for a minimal distance it should have migrated.

Press the "Display Plots" button.
This will take some time. Progress is being printed to the terminal.
Change to the "Graph" tab.

If you want images to be displayed while hovering over the points on the graph you need to give the full path to the folder
that holds your images in the respective text field and press the "upload_images" button.
This might take some time, progress again will be printed to the terminal.
The files can be hidden in subfolders, the given folder must contain all subfolders that contain your files.
Currently the app will upload ALL files that are directly in subfolders named 'overlays'. These folders therefore
must not contain any other files, but the images you want to be displayed.
If you want to change the naming of the subfolder edit the variable find_dir in the update() function within 
the file app_launcher.py.

The upload button for images will only upload a single image and is only intended to be used for debugging.
I.e. you can check if your images will be correctly displayed within the app. 
.png files should work. .tiff files do not. Other filetypes have not been tested.

If an error occurs, or you want to use new data, simply relaunch the app.
