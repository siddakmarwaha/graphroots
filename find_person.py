import pandas as pd
import re
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
# CPC = pd.read_excel('Demo_Files/CompanyPrimaryContactDemo.xlsx')
# IAH = pd.read_excel('Demo_Files/IndividualAffiliationHistoryDemo.xlsx')
# IEH = pd.read_excel('Demo_Files/IndividualEmploymentHistoryDemo.xlsx')
# IPC = pd.read_excel('Demo_Files/IndividualPrimaryContactDemo.xlsx')

def clean_phone_number(number):
    """
    Returns a phone number in the format +1-111-111-1111x1111.

    Parameters
    ----------
    number : str
        Phone number to be cleaned.

    Returns
    -------
    str
        The formatted number.
    """
    # Splits on x or X to separate main number and extension
    parts = re.split(r'[xX]', number, maxsplit=1)
    main = parts[0]
    ext = parts[1] if len(parts) > 1 else ""
    main_digits = re.sub(r'\D', '', main) # Remove any non-digits from the main number
    
    # If main_digits has more than 10 digits then extra digits at the beginning are the country code
    if len(main_digits) > 10:
        country_code = main_digits[:-10].lstrip('0')  # Remove leading zeros
        main_number = main_digits[-10:]
        formatted_main = f"{main_number[:3]}-{main_number[3:6]}-{main_number[6:]}"
        plus_country = f"+{country_code}" if country_code else "" # Add + if number had a country code
        clean_number = f"{plus_country}-{formatted_main}" if plus_country else formatted_main
    elif len(main_digits) == 10:
        clean_number = f"{main_digits[:3]}-{main_digits[3:6]}-{main_digits[6:]}"
    else:
        # If phone number is not 10 digits then just return the number as some countries do not use 10 digit system
        clean_number = main_digits

    # Add back extention if it had one
    if ext:
        clean_number += f"x{ext}"
    
    return clean_number

def find_person(input_name):
    """
    Finds a person's information and history.

    Parameters
    ----------
    input_name : str
        Name of the person to search for.

    Returns
    -------
    person_info : padnas.DataFrame
        Person's personal information.
    person_PID : str
        Person's personal identification number.
    person_EH : pandas.DataFrame
        Person's employment history.
    person_AH : pandas.DataFrame
        Person's affiliation history.
    """
    # Remove non-letters and converts name to all lowercase
    name = re.sub(r'[^a-zA-Z]', '', str(input_name)).lower()
    
    # Find person's information
    person_info = IPC[IPC['Label'].apply(lambda x: re.sub(r'[^a-zA-Z]', '', str(x)).lower()) == name]
    if not person_info.empty:
        person_PID = person_info.iloc[0,0]
        person_EH = IEH[IEH["PID"] == person_PID]
        person_AH = IAH[IAH["PID"] == person_PID]
        current_employment = pd.DataFrame({'PID' : person_info['PID'],
                                            'Role' : person_info['Job'], 
                                            'Company' : person_info['Company'],
                                            'Year Start': person_info['Year Start'], 
                                            'Year End': 'Present'})
        person_E = pd.concat([current_employment, person_EH], ignore_index=True)
        return person_info, person_PID, person_E, person_AH
    return None

def person_info(input_name):
    """
    Separates a person's information into dictionaries.

    Parameters
    ----------
    input_name : str
        Name of the person whose information is wanted.

    Returns
    -------
    personal_info : dict
        Dictionary of person's information to display.
    ah_info : dict
        Dictionary of person's affiliation history to display.
    eh_info : dict
        Dictionary of person's employment history to display.
    """
    person_info, person_PID, person_EH, person_AH = find_person(input_name)

    # Separates information to be displayed into dictionaries
    if not person_info.empty:
        person_info['PhoneNumber'] = person_info['PhoneNumber'].apply(clean_phone_number)
        personal_info = person_info.loc[:, ['Label', 'Job', 'Company', 'PhoneNumber', 
                                    'Email', 'WorkAddress', 'HomeAddress', 'X/Twitter Link', 
                                    'Facebook Link', 'LinkedIn Link', 'Instagram Link']].iloc[0].to_dict()
        ah_info = person_AH.loc[:, ['Year Start', 'Year End', 'Role', 'Organization']].sort_values(by='Year Start').to_dict(orient='records')
        eh_info = person_EH.loc[:, ['Year Start', 'Year End', 'Role', 'Company']].sort_values(by='Year Start').to_dict(orient='records') # Employment history
        return personal_info, eh_info, ah_info
    return None, [], [] # Return empty lists if no match

def search_suggestions(query):
    """Return a list of potential names that match the entered query (autocomplete feature)."""
    query = re.sub(r'[^a-zA-Z]', '', str(query)).lower()
    
    if len(query) < 2:  # Avoid unnecessary searches for very short queries
        return []
    
    # Find all names that partially match the input query
    matches = IPC[IPC["Label"].apply(lambda x: re.sub(r'[^a-zA-Z]', '', str(x)).lower()).str.contains(query, na=False)]
    
    # Return the top 10 matches (to limit the response size)
    return matches[["Label"]].head(10).to_dict(orient="records")

def find_company(name_with_sector):
    """
    Accepts input like "Archer-Patel (Healthcare)" and returns business info and categorized employees.
    """
    # --- Cleanup PIDs across datasets ---
    IPC["PID"] = IPC["PID"].astype(str).str.strip()
    IEH["PID"] = IEH["PID"].astype(str).str.strip()
    IAH["PID"] = IAH["PID"].astype(str).str.strip()

 # Try to extract company name and sector
    match = re.match(r"^(.*?)\s*\((.*?)\)$", name_with_sector)
    
    if match:
        company_name, sector_name = match.group(1).strip(), match.group(2).strip()
        comp = CPC[(CPC["Company"] == company_name) & (CPC["BusinessSector"] == sector_name)]
    else:
        # Fallback if only company name is provided
        company_name = name_with_sector.strip()
        comp = CPC[CPC["Company"] == company_name]

    if comp.empty:
        return None

    row_num = comp.index.tolist()


    # --- Current Employees ---
    current_emp = IPC[IPC["Company"] == company_name].copy()
    current_emp["EmploymentType"] = "Current"
    current_emp["Year End"] = "Present"
    current_emp["History"] = "Employment"

    # Merge only contact info from IPC
    contact_cols = ["PID", "Label", "PhoneNumber", "Email", "WorkAddress", "HomeAddress", 
                    "X/Twitter Link", "Facebook Link", "LinkedIn Link", "Instagram Link"]
    IPC_clean = IPC[contact_cols].drop_duplicates(subset=["PID"])

    current_emp = current_emp.merge(IPC_clean, on="PID", how="left")

    # --- Former Employees ---
    former_emp = IEH[IEH["Company"] == company_name].copy()
    former_emp = former_emp[~former_emp["PID"].isin(current_emp["PID"])]
    former_emp["EmploymentType"] = "Former"
    former_emp["History"] = "Employment"

    # # Merge only contact info from IPC
    # contact_cols = ["PID", "Label", "PhoneNumber", "Email", "WorkAddress", "HomeAddress", 
    #                 "X/Twitter Link", "Facebook Link", "LinkedIn Link", "Instagram Link"]
    # IPC_clean = IPC[contact_cols].drop_duplicates(subset=["PID"])

    # former_emp = former_emp.merge(IPC_clean, on="PID", how="left")

    # --- Affiliates ---
    affiliates = IAH[IAH["Organization"] == company_name].copy()
    affiliates["EmploymentType"] = "Affiliate"
    affiliates["History"] = "Affiliation"

    # --- Combine all employee groups ---
    all_people = pd.concat([current_emp, former_emp, affiliates], ignore_index=True)

    # Keep only unique contact info columns from IPC
    contact_cols = ["PID", "PhoneNumber", "Email", "WorkAddress", "HomeAddress",
                    "X/Twitter Link", "Facebook Link", "LinkedIn Link", "Instagram Link", "Label"]
    contact_info = IPC[contact_cols].drop_duplicates(subset=["PID"])

    # Merge cleanly ONCE
    all_people = all_people.merge(contact_info, on="PID", how="left")

    # Optional: apply phone cleanup
    # if "PhoneNumber" in all_people.columns:
    #     all_people["PhoneNumber"] = all_people["PhoneNumber"].fillna("").apply(clean_phone_number)
    
    # Make sure Label column exists after merge
    if "Label" not in all_people.columns:
        label_cols = [col for col in all_people.columns if "Label" in col]
        if label_cols:
            all_people["Label"] = all_people[label_cols[0]]
        else:
            all_people["Label"] = "Unknown"
    else:
        all_people["Label"] = all_people["Label"].fillna("Unknown")
    return company_name, comp, row_num, all_people

 
def business_search_suggestions(query):
    """
    Return a list of business name and sector combinations for autocomplete.
    Example: "Archer-Patel (Healthcare)"
    """
    query = str(query).lower().strip()
    if len(query) < 2:
        return []

    matches = CPC[CPC["Company"].str.lower().str.contains(query, na=False)].copy()
    matches = matches.dropna(subset=["BusinessSector"])  # Ensure sector exists

    # Create Label = "Company (Sector)"
    matches["Label"] = matches["Company"] + " (" + matches["BusinessSector"] + ")"

    return matches[["Label"]].head(10).to_dict(orient="records")
