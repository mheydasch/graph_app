# graph_app
This tool is intended to be used for exploration of microscopy data.
It provides you with the ability to load data, make graphs from it and display the images the data relates to
when clicking on individual points on the graphs.

### Compatibility
This tool has been developed on MacOs and been tested on Windows10

### Getting started:
To start you have to have a csv file of your data in long format and one or multiple folders called overlays
 with images related to that data
Your dataframe needs to have the following columns:
  1. Columns holding X and Y coordinates of the individual cells
  2. Columns holding your data. Can be the same as X  and Y coordinates
  3. A column holding the timepoints
  4. A column holding the unique ids of individual cells including the time. 
   These should be formatted the following: An identifier for the field of view, an Identifier for the tracking ID of the cell
   An identifier of the time. Each of these should be preceeded by a letter indicating which ID it is, such as 
   WC2_S0127_E1_T1. Where C2_S0127 is the field of view, 1 is the track ID and 1 is the Timepoint
  5. A column holding the unique ids without the time.
  6. A column which you want to use as a classifier

Your images need to contain the same identifier as the one in your csv file, without the unique cell identifier.
For example with the above mentioned unique ID: *WC2_S0127_E1_T1* the corresponding image can be named
something like  *t1_F0127_nuclei_C2_WC2_S0127_T1.png*. Whereas the part *C2_WC2_S0127_T1.png* is required
and the rest is optional. 
To capture the ID of above example you would employ a regular expression such as
*(?P<Site_ID>W[A-Z][0-9]+_S[0-9]{4})(?P\<TrackID\>_E[0-9]+)(?P\<Timepoint\>_T[0-9]+)*
It is crucial that your identification has these three different ids:
  * **Site_ID**
  * **TrackID**
  * **Timepoint** 

Currently the order of these IDs needs to be exactly this.
If you are having underscores separating your IDs they need to be captured
by the regular expression. **Every part** of the ID in your csv file needs to be captured.
The above regular expression is the standard one, but can be changed by the user


### Functionality

#### Launching the app
To start the app open your terminal and navigate to the folder holding the files by 
*cd /[...]/graph_app*
Then start the app by launching it with python from the terminal by typing
*python3 app_launcher.py* , or launch the script from a python editor

Progress will be printed to the terminal, as well as the URL the app will be launched on.
*Running on http://127.0.0.1:8050/*

Copy this URL to your browser and hit enter. 
I recommend using Google Chrome, as Firefox sometimes froze during usage.
#### Uploading Data
To upload data choose your *.csv* file in long format, containing all the comments mentioned above and either drag and drop it
into the menu **Upload the csv file holding your data:** or click on the button and select your file.

#### Uploading Images
Your images need to be in *.png* format.
To upload images you have to manually type in the full path to your folder that contains all the subfolders with images.
Add a regular expression, such as the example. This regular expression works the same as the one in cell profiler, so you can 
use cell profiler, or other third party software to test it. Submit the pattern, that should relate your images to your data and 
press the **UPLOAD IMAGES** button. 
Your images need to be contained in a folder called *overlays*. The images can be in different folders, and you must not
give the full path including the *overlays* folder. The app will look through all sub folders in the folder you have given and find
all folders called *overlays*. The path to all *.png* files that are in those folders will be uploaded.

#### Data Filtering
In the **Data Filtering** section you can filter the data that will be plotted.
This will not change your dataframe!
You can choose a value for the minimum track length.
Each cell that has been tracked for a shorter time than that value will be excluded.
It does not matter if the cell was present from the beginning or not, it only needs to be
tracked for a continuous time longer, or equal to the input value at some point during the
time of the experiment

You can choose user added flags that should be excluded from the graph.
You can select a minimum travelled distance:
All cells that have not travelled a distance equal or greater than the input value will 
be excluded from the *migration_distance* graph. This currently has no effect on any 
other graphs.

You can choose to exclude all cells that are in an image where a flag other than 'None' was added to any cell.
This can be useful if you want to make sure you took a look at all the images. Simply add a comment to any
cell, select this option and plot the graphs again, until no data points will be plotted anymore.

#### Graphs
In the first radio item menu under **Data filtering**
You can choose to display different types of graphs:

   **1. lineplot:**
   You choose two columns of data, your first column will be the X value your second the Y value
   If you want to display cell migration you should use normalized X and Y coordinates starting from 0,0
   at timepoint 1. If you want to display a time series you should use time as the first input and your 
   measurement as the second one. This will create one lineplot per classifier.
   
   **2. migration_distance:**
   Two boxplots showing the migration speed and the persistence of migration. It will add
   one box per classifier.
   
   **3. time_series:**
   Obsolete graph. Takes one input argument and plots it versus the time. Does not actually add
   anything that cannot be done with lineplot.
   
   **4. corel plot:**
   Gives a scatterplot of two input arguments and draws a regression line.
   
   **5. flag_count:**
   Produces a histogram for the number of cells where user added flags occur,
   separated by the given classifier.  Creates one histogram for each unique flag.

To view the graphs you Have to select the **Graph** tab first.
Select the kind of graph you want to plot and click the **DISPLAY PLOTS** button.
Above this button you can choose if you want to display a previously created instance of that graph.
Depending on the size of your data creating graphs can take several minutes.
Choosing *yes* for this option allows you to create a different graph and then go back to display
the previously created graphs without having to redo the computation. 
If you want to do any changes to filters, classifiers or data you have to select *no* to update the graph.

The table in the **Table** tab currently will not be updated and shows a subset of the table you have uploaded

Clicking on an individual datapoint in any of the graphs will display the corresponding image next to the graph.
The cell corresponding to the datapoint will be marked with a red dot. 
Each other tracked cell in the same image that meats your filter requirements
will be marked with a blue dot on the image. 
With the two sliders below the image you can click through the full timelapse and adjust the relative brightness of the image.

#### Flagging
If you click on the any of the dots on the image, or on the graph you can enter a comment to a newly created column 'flags' about the cell.
You can choose to make the comment either for the whole time course, or a single time point.

Check in the dialog box if the cell selected is the one you want, type your flag into the text field and press the **ADD COMMENT** button
If you want to save the commented dataframe type the path to the folder including the file name into the text field below that and press the
**DOWNLOAD DATATABLE** button.

The commented dataframe will be automatically saved as *temp.csv* in the *Cache* folder at the location you saved the app to.
So, in case you forgot downloading your commented data frame or the app, or your computer crashes before you had the chance
to download it you can retrieve the commented data frame from this location before restarting the app.
This is not a location to save your dataframe! The file will be overwritten every time you add a flag to a dataframe.

You can select to filter out all rows with a specific comment, filter out whole images if they contain a comment,
or even display a graph showing how often each comment occurs within different conditions.

#### Resetting Settings

Whenever you change any settings in the app, such as select columns, change filters etc. these settings will be saved
in the *settings.csv* inside the Cache folder. These settings will be loaded everytime you upload a dataframe to the app.
If you do not want to use previous settings, but want to use the default settings instead you can delete this *.csv* file.


### Help
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


If you want to make changes to the script it is reccomended to change debug in 
if __name__ == '__main__':
    app.run_server(debug=False)

to True. In addition there is a testmode flag for the graph plotting in the function plot_graph(). 
If you are having large datasets you should set this to True for faster testing.
What this flag does is defined in the plotting functions. Depending on the size of your data 
you might want to change the subsetting of data. 
After starting the app you can click on the Callback Graph, next to the Errors to see a rough overview of the apps logic.
The app is split in four main files.
app_launcher.py contains the html layout and all the callbacks of the app.

menu_definitions.py contains the definitions for most menus, buttons and other input options.

graph_defintions.py contains all the plotting functions





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
This might take some time, progress again will be printed to the terminal. A subset of the created dictionaries,
relating keys to filepaths to the images will be printed to the terminal. If no such dictionary is printed, this means
no images have been found. In this case you should check the path for spelling errors.
The files can be hidden in subfolders, the given folder must contain all subfolders that contain your files.
Currently the app will upload ALL png files that are directly in subfolders named 'overlays'. These folders therefore
must not contain any other png files, but the images you want to be displayed.
If you want to change the naming of the subfolder edit the variable find_dir in the update() function within 
the file app_launcher.py.


If an error occurs, or you want to use new data, simply relaunch the app.

