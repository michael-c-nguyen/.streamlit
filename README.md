# Note: 

In order to run the program, you need a Snowflake account and follow the
template below. Note that the databases will also be required to run the
program.

# Datasets:

### Provider: Knoema
### Title: Monthly Climatic Data for the World

### Provider: OAG
### Title: OAG: Global Airline Schedules

# Instructions:

* Create a `.streamlit` folder with a `secrets.toml` file in the directory. 

* Inside of the `secrets.toml` file, place the following code from below with your information.
One database and schema is okay.

* Run the program from the command line using `streamlit run "I. Main.py"`

### [snowflake] 

### user = "xxx" 

### password = "xxx" 

### account = "xxx"

### warehouse = "xxx" 

### database = "xxx" 

### schema = "xxx" 