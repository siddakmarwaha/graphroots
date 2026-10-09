# Installation

## Adding the Data
1. Download the de-identified dataset (named 'data') which can be found in the Grassroots Teams Folder: `Grassroots/Data_Files/`.
2. Move it to the location you plan to clone the repository in.
3. Make sure to not change the name of the folder 'data'.

## Cloning the repository
1.  Open a command terminal
2.  Clone the project repository onto your computer through terminal.
    `git clone https://gitlab.msu.edu/grassroots/graphroots.git`

## Using provided environment to avoid installations

To avoid manually installing all dependencies, you can use the provided [environment.yml](./environment.yml) file to set up your environment quickly.

#### Create and activate Conda environment:
1. Install [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)
2. Create and activate the provided environment using the following commands:
    - `conda env create --prefix ./envs --file environment.yml`
    - `conda activate ./envs`

**Note**: If you are using the provided environment, you can skip part 1-3 of the "Installation of Software" instructions below.

## Installation of Software

1. Install Node.js if you don't have it already using conda: `conda install -c conda-forge nodejs`
2. Open up another terminal, and navigate to the main graphroots directory: `cd path/to/graphroots`
3. Install all the packages by running the following command: `pip install -r requirements.txt`
4. Open up another terminal, and navigate to the graphroots directory within graphroots on your terminal (this graphroots is actually the frontend folder) `cd graphroots`
5. Install all packages/dependencies relevant to the frontend: `npm install`
6. Install axios with `npm install axios`

**Note**: `npm install` should install all the dependencies, but if any package is not installed automatically, the terminal should say which package is not installed, and do a `npm install <package_name>` to install the specific package in the ./graphroots/graphroots directory.

## Running the Application

Everytime you run the application, you don't have to install anything again, just do the following:
1. In the main graphroots directory, run the Flask app: `python flask_api.py` or `python3 flask_api.py`
2. Open up a new terminal, and navigate to the graphroots directory within graphroots: `cd graphroots/graphroots`
2. Run the frontend with the following (ensure to be in ./graphroots/graphroots): `npm run dev`
3. After both the flask api and frontend is running, feel free to open up the website url (http://localhost:5173/) in a search engine (google chrome/safari) and search for data in our database.

## (Optional) To deactivate the environment:

1. On Windows, in your Anaconda Prompt, run `deactivate`
2. On macOS and Linux, in your Terminal Window, run `conda deactivate`

**Note**: If you have trouble with the packages, refer to the Installation of Software instructions.