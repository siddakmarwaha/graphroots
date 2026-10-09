import hashlib
import matplotlib.colors as mcolors
import networkx as nx
from pyvis.network import Network
from find_person import find_company, find_person, IPC

def comp_create_graph(comp_name):
    company_name, comp, row_num, connecting_people = find_company(comp_name)
    if comp is None:
        return None

    G = nx.Graph()
    G.add_node(company_name,
               label=company_name,
               color='blue',
               size=20)

    for row in connecting_people.itertuples():
        print(row)
        if row.EmploymentType == 'Current':
            color = 'blue'
        else:
            color = 'red'
        name = IPC.loc[IPC['PID'] == row.PID, 'Label'].values[0]

        G.add_node(name,
                label=name,
                title=f"{name} \n Phone Number: {row.PhoneNumber} \n Email: {row.Email}",
                color = color)
        G.add_edge(company_name, name,
                title=f"{name} worked at {company_name} in {row._15}-{row._17}",
                color = color)

        person_info, person_PID, person_E, person_AH = find_person(name)
        for rows in person_E.itertuples():
            if rows.Company != company_name:
                G.add_node(rows.Company,
                        label=rows.Company,
                        color = color)
                G.add_edge(name, rows.Company,
                        title=f"{name} worked at {rows.Company} in {rows._4}-{rows._5}",
                        color = color)
    net = Network(notebook=True, cdn_resources='remote')
    net.toggle_drag_nodes(False)
    net.from_nx(G)
    graph_path = "business_graph.html"
    net.save_graph(graph_path)
    return graph_path
