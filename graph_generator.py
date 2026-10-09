import pandas as pd
import re
from pyvis.network import Network
import networkx as nx
import hashlib
import matplotlib.colors as mcolors
from find_person import find_person
import random
from datetime import datetime
from db_loader import load_table

CPC = load_table("CompanyPrimaryContact")
IAH = load_table("IndividualAffiliationHistory")
IEH = load_table("IndividualEmploymentHistory")
IPC = load_table("IndividualPrimaryContact")

# CPC = pd.read_excel('data/CompanyPrimaryContact.xlsx', index_col=0)
# IAH = pd.read_excel('data/IndividualAffiliationHistory.xlsx', index_col=0)
# IEH = pd.read_excel('data/IndividualEmploymentHistory.xlsx', index_col=0)
# IPC = pd.read_excel('data/IndividualPrimaryContact.xlsx', index_col=0)

# Load Excel files
#CPC = pd.read_excel('Demo_Files/CompanyPrimaryContactDemo.xlsx', index_col=0)
#IAH = pd.read_excel('Demo_Files/IndividualAffiliationHistoryDemo.xlsx', index_col=0)
#IEH = pd.read_excel('Demo_Files/IndividualEmploymentHistoryDemo.xlsx', index_col=0)
#IPC = pd.read_excel('Demo_Files/IndividualPrimaryContactDemo.xlsx', index_col=0)

def find_overlapping_rows(dataframe, history_df, key_column):
    """
    Finds rows with overlapping years and the same key_column in dataframe.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The dataframe in which to search for overlap.
    history_df : padnas.Dataframe
        A dataframe containing the person's history.
    key_column : 
        Column name in which to search for shared company or organization.

    Returns
    -------
    pandas.DataFrame
        A dataframe of the rows with overlapping years.
    """
    overlapping_rows = pd.DataFrame() # Initialize the returned dataframe

    # Iterate through each row of the person's history
    for _, person_row in history_df.iterrows():
        key_value = person_row[key_column]
        person_year_start = person_row['Year Start']
        if person_row['Year End'] != 'Present':
            person_year_end = person_row['Year End']
        else:
            person_year_end = datetime.now().year

        person_row['Overlap_Start'] = person_row['Year Start']
        person_row['Overlap_End'] = person_row['Year End']
        overlapping_rows = pd.concat([overlapping_rows, pd.DataFrame([person_row])], ignore_index=True)

        # Find the rows with the same key_column
        overlaps = dataframe[(dataframe[key_column] == key_value) & (dataframe['PID'] != person_row['PID'])]

        # Filter out rows that do not have overlapping years
        overlaps = overlaps[
            overlaps.apply(
                lambda row: (row['Year Start'] <= person_year_end and row['Year End'] >= person_year_start),
                axis=1
            )
        ]
        
        # Add a column with overlapping years
        if not overlaps.empty:
            overlaps['Overlap_Start'] = overlaps.apply(lambda row: max(row['Year Start'], person_year_start), axis = 1)
            overlaps['Overlap_End'] = overlaps.apply(lambda row: min(row['Year End'], person_year_end), axis = 1)
        
        # Add the overlapping rows to the returned dataframe
        overlapping_rows = pd.concat([overlapping_rows, overlaps])

    return overlapping_rows

def find_connections(input_name):
    """
    Searches for a person's connections.

    Parameters
    ----------
    input_name : str
        Name of the person whose connections to search for.

    Returns
    -------
    overlapping_AH : dict
        Overlapping afiliations.
    overlapping_EH : dict
        Overlapping employment. 
    """
    person_info, person_PID, person_EH, person_AH = find_person(input_name)
    if person_info.empty:
        return None, None, None, None
        
    # Find the overlapping rows for affiliation
    overlapping_AH = find_overlapping_rows(IAH, person_AH, 'Organization')
    if not overlapping_AH.empty:
        overlapping_AH = overlapping_AH.merge(IPC[['PID', 'Label']], on='PID', how='left')
    
    # Find the overlapping rows for enployment
    overlapping_EH = find_overlapping_rows(IEH, person_EH, 'Company')
    if not overlapping_EH.empty:
        overlapping_EH = overlapping_EH.merge(IPC[['PID', 'Label']], on='PID', how='left')

    return overlapping_AH, overlapping_EH

def generate_color(name):
    """
    Generates a unique color based on a hash of the input string.
    
    Parameters
    ----------
    name : str
        String to hash.

    Returns
    -------
    str
        HEX color code.
    """
    hash_object = hashlib.md5(name.encode())
    hash_hex = hash_object.hexdigest()
    hue = int(hash_hex, 16) % 360 
    
    # Convert HSV to RGB and format as hex color string
    rgb = mcolors.hsv_to_rgb((hue / 360, 0.7, 0.9))  # Returns an ndarray (array of 3 values)
    hex_color = mcolors.to_hex(rgb)  # Convert to a hex string like '#ffcc00'
    
    return hex_color  # Now returning a serializable hex string

def create_graph(input_name):
    """
    Creates interactive connections graph for person.

    Parameters
    ----------
    input_name : str
        Name of the person to create a graph for.

    Returns
    -------
    path
        path to the pyvis Network object graph file.
    """
    person_info, person_PID, person_EH, person_AH = find_person(input_name)
    AH, EH = find_connections(input_name)

    if person_info is None:
        return None
    name = person_info.iloc[0]['Label']
    job = person_info.iloc[0]['Job']
    company = person_info.iloc[0]['Company']
    
    # Create NetworkX graph
    G = nx.Graph()

    # Add node for person
    G.add_node(name, 
               label = name, 
               title = f"Name: {name} \n Job: {job} \n Company: {company}",
               color = generate_color(company),
               size = 20,
               borderWidth = 6,
               borderWidthSelected = 6)
    
    # Add nodes for affiliation connections
    for row in AH.itertuples():
        if row.Label == name: # Get role of person for information on edges later
            role = row.Role
            org = row.Organization
            # Find the years the person was in the position
            if not pd.isna(row.Overlap_End) and row.Overlap_End is int:
                years = f"{int(row.Overlap_Start)}-{int(row.Overlap_End)}"
            elif not pd.isna(row.Overlap_End):
                years = f"{int(row.Overlap_Start)}-{row.Overlap_End}"
                
            # Add node for connected organization
            G.add_node(org,
                       label=org,
                       color=generate_color(str(org)))
            G.add_edge(org,
                       name,
                       title=f"{name} was affiliated with {org} in {years}",
                       color=generate_color(str(org)))

        if row.Label != name:
            con_name = row.Label
            # Finds the overlapping years for the connection
            if row.Overlap_Start == row.Overlap_End:
                overlap_years = int(row.Overlap_Start)
            else:
                overlap_years = f"{int(row.Overlap_Start)}-{int(row.Overlap_End)}"
            # Add node for each person connected
            G.add_node(con_name, 
                       label = con_name, 
                       title = f"Name: {con_name} \n Job: {row.Role} \n Years: {row._4} - {row._5}",
                       color = generate_color(row.Organization),
                       size = 4 * (row.Overlap_End - row.Overlap_Start + 3))
            G.add_edge(org, 
                       con_name,
                       title = f"{name} ({role}) and {con_name} ({row.Role}) \n were both affiliated with {row.Organization} in {overlap_years}",
                       color = generate_color(row.Organization))
        
    # Add nodes for employment connections
    for row in EH.itertuples():
        if row.Label == name:
            role = row.Role
            comp = row.Company
            # Find the years the person was in the position
            if not pd.isna(row.Overlap_End) and row.Overlap_End is int:
                years = f"{int(row.Overlap_Start)}-{int(row.Overlap_End)}"
            elif not pd.isna(row.Overlap_End):
                years = f"{int(row.Overlap_Start)}-{row.Overlap_End}"
            G.add_node(comp,
                       label=comp,
                       color=generate_color(str(comp)))
            G.add_edge(comp,
                       name,
                       title=f"{name} worked for {comp} in {years}",
                       color=generate_color(str(comp)))
        if row.Label != name:
            con_name = row.Label
            # Finds the overlapping years for the connection
            if row.Overlap_Start == row.Overlap_End:
                overlap_years = int(row.Overlap_Start)
            else:
                overlap_years = f"{int(row.Overlap_Start)}-{int(row.Overlap_End)}"
            # Add node for each connection
            G.add_node(con_name, 
                       label = con_name, 
                       title = f"Name: {con_name} \n Job: {row.Role} \n Years: {row._4} - {row._5}",
                       color = generate_color(row.Company),
                       size = 4 * (row.Overlap_End - row.Overlap_Start + 3))
            # Add edge for the connection
            G.add_edge(comp, 
                       con_name,
                       title = f"{name} ({role}) and {con_name} ({row.Role}) \n worked together at {row.Company} in {overlap_years}",
                       color = generate_color(row.Company))

    net = Network(notebook = True, cdn_resources='remote') # Create pyvis Network object
    net.toggle_drag_nodes(False) # Remove node movement
    net.from_nx(G) # Add nodes and edges
    graph_path = "contact_graph.html"
    net.save_graph(graph_path)
    return graph_path
