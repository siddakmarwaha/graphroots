from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from find_person import find_person, search_suggestions, find_company, person_info  # Import functions
from graph_generator import create_graph
import os
from find_person import business_search_suggestions  # Add to your imports
from business_graph_generator import comp_create_graph



app = Flask(__name__)
CORS(app)  # Allow frontend connections

@app.route("/api/contacts/search", methods=["GET"])
def search_contacts():
    query = request.args.get("name", "").strip()

    if not query:
        return jsonify({"error": "No name provided."}), 400

    person, employment, affiliations = person_info(query)

    if person is not None and isinstance(person, dict) and person.get("Label"):
        print("\n--- Debugging API Response ---")
        print(person)
        print("--------------------------------\n")

        if employment:
            print("\n--- Debugging Employment ---")
            print(employment)
            print("--------------------------------\n")

        if affiliations:
            print("\n--- Debugging Affiliations ---")
            print(affiliations)
            print("--------------------------------\n")

        person_details = {
            "name": person.get("Label", "N/A"),
            "phone": person.get("PhoneNumber", "N/A"),
            "email": person.get("Email", "N/A"),
            "job": person.get("Job", "N/A"),
            "company": person.get("Company", "N/A"),
            "address": person.get("HomeAddress", "N/A"),
            "workAddress": person.get("WorkAddress", "N/A"),
            "xLink": person.get("X/Twitter Link", "N/A"),
            "FacebookLink": person.get("Facebook Link", "N/A"),
            "LinkedInLink": person.get("LinkedIn Link", "N/A"),
            "InstagramLink": person.get("Instagram Link", "N/A")
        }

        return jsonify({
            "person": person_details,
            "employment": employment,
            "affiliations": affiliations
        })

    return jsonify({"message": "No contact found."}), 404


@app.route("/api/contacts/suggestions", methods=["GET"])
def get_suggestions():
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided."}), 400

    suggestions = search_suggestions(query)

    return jsonify({"suggestions": suggestions})


@app.route("/api/contacts/generate-graph", methods=["POST"])
def generate_graph():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "No name provided."}), 400

    graph_path = create_graph(name)

    if not os.path.exists(graph_path):
        return jsonify({"error": "Graph not found."}), 500

    return jsonify({"success": True, "graph_url": graph_path})

@app.route("/contact_graph.html")
def serve_graph():
    return send_file("contact_graph.html")

@app.route("/api/business/search", methods=["GET"])
def search_business():
    query = request.args.get("name", "").strip()
    if not query:
        return jsonify({"error": "No business name provided."}), 400

    company_name, comp, row, employees = find_company(query)
    print(employees)

    if company_name:
        business_details = {
            "name": company_name,
            "phone": comp["PhoneNumber"].values[0] if "PhoneNumber" in comp else "N/A",
            "email": comp["Email"].values[0] if "Email" in comp else "N/A",
            "address": comp["WorkAddress"].values[0] if "WorkAddress" in comp else "N/A",
            "financial": comp["Financial"].values[0] if "Financial" in comp else "N/A",
            "sector": comp["BusinessSector"].values[0] if "BusinessSector" else "N/A"
        }

        # Ensure employees data exists
        if not employees.empty:
            # Group employees by EmploymentType
            connections = employees[employees["History"] == "Affiliation"][["Year Start", "Year End", "Role", "Organization"]].to_dict(orient="records")

            current_employees = employees[employees["EmploymentType"] == "Current"]
            former_employees = employees[employees["EmploymentType"] == "Former"]

            # Add consistent output
            relevant_employees = []

            for _, row in current_employees.iterrows():
                relevant_employees.append({
                    "Label": row["Label"],
                    "Job": row.get("Job", "N/A"),
                    "Email": row.get("Email", "N/A"),
                    "PhoneNumber": row.get("PhoneNumber", "N/A"),
                    "Status": f"Current ({row['Year Start']}-{row['Year End']})"
                })

            for _, row in former_employees.iterrows():
                relevant_employees.append({
                    "Label": row["Label"],
                    "Job": row.get("Role", "N/A"),  # Former employees come from IEH which uses 'Role'
                    "Email": row.get("Email", "N/A"),
                    "PhoneNumber": row.get("PhoneNumber", "N/A"),
                    "Status": f"Former ({row['Year Start']}-{row['Year End']})"
                })
        else:
            relevant_employees = []
            connections = []

        return jsonify({"business": business_details, "employees": relevant_employees, "connections": connections})

    return jsonify({"message": "No business found."}), 404

@app.route("/api/business/suggestions", methods=["GET"])
def get_business_suggestions():
    query = request.args.get("query", "").strip()
    suggestions = business_search_suggestions(query)
    return jsonify({"suggestions": suggestions})

@app.route("/api/business/generate-graph", methods=["POST"])
def generate_business_graph():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "No business name provided."}), 400

    graph_path = comp_create_graph(name)

    if not graph_path or not os.path.exists(graph_path):
        return jsonify({"error": "Graph generation failed."}), 500

    return jsonify({"success": True, "graph_url": graph_path})


@app.route("/business_graph.html")
def serve_business_graph():
    return send_file("business_graph.html")


if __name__ == "__main__":
    app.run(debug=True)
