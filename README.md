# graph_app

This tool is intended to be used for exploration of microscopy data.
It provides you with the ability to load data, make graphs from it and display the images the data relates to
when clicking on individual points on the graphs.
You can choose to display different types of graphs:
Lineplots, where each line represents the migration track of an individual cell
Two boxplots showing the total migrated distance and the persistence of migration.
Lineplots showing the changes of one measurement over time
Correlation plot showing how migration speed and migration persistence correlate with each other
Bar plots showing how often a user given flag occurs in the data.

The plots are seperated based on the given classifier.

When you click on an individual datapoint, the corresponding image the data is taken from is displayed next to the graph.
You can click through the full timelapse and adjust the relative brightness of the image.
This works with all plots except for the flag_count plot.

Each tracked cell that meats your filter requirements will be marked with a blue dot on the image. 
The cell corresponding to the data point you selected from the graph will be marked with a red dot.

If you click on the dot you can enter a comment to a newly created column 'flags' about the cell.
You can choose to make the comment either for the whole time course, or a single time point.

You can select to filter out all rows with a specific comment, filter out whole images if they contain a comment,
or even display a graph showing how often each comment occurs within different conditions.

The dataframe with the columns will be saved as 'temp.csv' in the folder containing the app, so make sure you do not
have any file with the same name in that folder.
You can save the file manually by giving the desired full path and name in field above the DOWNLOAD DATATABLE 
button and then click the button.


To start the app open your terminal and navigate to the folder holding the files by 
cd /[...]/graph_app
Then start the app by launching it with python from the terminal by typing
python3 app_launcher.py, or launch the script from a python editor
Progress will be printed to the terminal, as well as the URL the app will be launched on.
Running on http://127.0.0.1:8050/
Copy this URL to your browser and hit enter. 




Your data should be organized the following way:
A .csv file in long format with columns for:
Data (can be multiple columns)
X and Y coordinates (can be same as data)
Timepoint(should be starting from 1)
Unique ID of each object
A column that holds the unique ID + the timepoint
A classifier for the different groups.


The naming of these columns is irrelevant. Though default naming exists, you can manually select which column 
represents which category in the app.

If your data has different but consistent namings and you want to change the default values 
you need to set the value parameters of the dropdown menus in the file menu_definitions.py to your naming.
These dropdown menus are:
classifier_choice()
identifier_selector()
timepoint_selector()
data_selector()
coordinate_selector()
unique_time_selector


In it's current version the app is only optimized for data representing cell migration in two dimensions.

The software is currently optimized for the unique id having the following format:
WWellname_SSitenumber_Etrackid_Ttimepoint, such as:
WC3_S0423_E10_T37

This is relevant for finding the associated images.
A standard regular expression for this format is given as 
'(?P<Site_ID>W[A-Z][0-9]+_S[0-9]{4})(?P<TrackID>_E[0-9]+)(?P<Timepoint>_T[0-9]+)'
but can be changed.
It is, however required that each regular expression you change this to contains the three key words:
Site_ID, TrackID, Timepoint. 
Each naming of a cell with its time point has to be unique!
The order of these key words is irrelevant.

This regular expression format is the same as is used in cell profiler. 
To interactively test your regular expression I recommend using the cell profiler
Regular expression editor in the tab Metadata.
The filename of your images needs to contain the Site_ID and the Timepoint to be associated to the data.
If you want to make more substantial changes to this format  it is necessary to change every piece of code including re.compile
and re.search statements. 


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
Currently the app will upload ALL png files that are directly in subfolders named 'overlays'. These folders therefore
must not contain any other png files, but the images you want to be displayed.
If you want to change the naming of the subfolder edit the variable find_dir in the update() function within 
the file app_launcher.py.


If an error occurs, or you want to use new data, simply relaunch the app.


To help you get your data in the required format there are several files
in the folder examples_and_helpers:
rename.FoV.py is a pythonscript used from the terminal to rename images with standard Nikon naming to an easier to work with format.
It takes input arguments
-d full directory to your images)
-i identifiers of your image (for example Channel name). Can be a list, seperated by spaces.

example_cp_pipeline.cpproj is an example Cell Profiler pipeline for batch processing.
For tracking we use u-track software from the Danuser lab 
https://github.com/DanuserLab/u-track

track_import.py does collect all the seperate .csv files from the u-track software merges them into a single data frame,
and bring them into an appropriate format for the app.
It needs to be run from a python editor, such as Spyder, or PyCharm.
First the class Experiment_data needs to be initiated with the path to your data, 
then the normalize_tracks() function needs to be called and then the Experiment_data.tracks object
needs to be saved as a csv.
