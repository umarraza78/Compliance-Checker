import streamlit as st
import os
import json
from compliance_checker import load_rules, load_vectorstore, check_compliance, check_all_rules
from compliance_checker import MY_GOOGLE_API_KEY

st.set_page_config(page_title="Compliance Checker", page_icon="📋", layout="wide")
st.title("📋 Policy Compliance Checker")

api_key = MY_GOOGLE_API_KEY
os.environ["GOOGLE_API_KEY"] = api_key

@st.cache_resource
def initialize_system():
    try:
        vectorstore = load_vectorstore("vectorstore")
        rules = load_rules()
        return vectorstore, rules
    except FileNotFoundError as e:
        st.error(f"Error: {str(e)}")
        return None, None

vectorstore, rules = initialize_system()

section = st.sidebar.radio("Select Section", ["Single Rule Check", "Full Audit", "Rules List"])

if vectorstore is not None and rules is not None:
    st.success("✓ System Ready!")
    
    if section == "Single Rule Check":
        st.header("Check Individual Rule Compliance")

        txt_dir = "CUAD_v1/full_contract_txt"
        contract_files = [f for f in os.listdir(txt_dir) if f.lower().endswith('.txt')]
        contract_files = sorted(contract_files)
        contract_choice = st.selectbox("Select a contract (or leave blank to search entire corpus):", ["(search all)"] + contract_files)

        rule_names = [f"{r['id']}. {r['name']}" for r in rules]
        selected_rule_name = st.selectbox("Select a rule to check:", rule_names)

        rule_id = int(selected_rule_name.split(".")[0])
        selected_rule = next(r for r in rules if r["id"] == rule_id)

        st.write(f"**Description:** {selected_rule['description']}")
        st.write(f"**Category:** {selected_rule['category']}")

        if st.button("Check Compliance"):
            with st.spinner("Checking compliance..."):
                try:
                    if contract_choice and contract_choice != "(search all)":
                        path = os.path.join(txt_dir, contract_choice)
                        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                            contract_text = fh.read()
                    else:
                        contract_text = ""

                    result = check_compliance(contract_text, selected_rule, vectorstore, api_key)

                    st.subheader("Compliance Check Result")

                    if result["status"] == "COMPLIANT":
                        st.success(f"Status: {result['status']}")
                    else:
                        st.warning(f"Status: {result['status']}")

                    st.subheader("Details")
                    st.write(result["response"])

                    st.subheader("Sources")
                    for source in result["sources"]:
                        st.write(f"- {source}")
                    if result.get('raw_docs'):
                        st.subheader('Retrieved document previews')
                        for i, doc in enumerate(result['raw_docs']):
                            with st.expander(f"Doc {i+1} - {doc.metadata.get('source', 'unknown')}"):
                                st.write(doc.page_content[:1000])
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif section == "Full Audit":
        st.header("Full Compliance Audit")
        st.write("Run compliance check on all rules.")
        
        if st.button("Run Full Audit"):
            with st.spinner("Running audit..."):
                try:
                    results = check_all_rules(vectorstore, api_key)
                    
                    st.subheader("Audit Results Summary")
                    
                    compliant_count = sum(1 for r in results if r["status"] == "COMPLIANT")
                    non_compliant_count = sum(1 for r in results if r["status"] == "NON-COMPLIANT")
                    error_count = sum(1 for r in results if r["status"] == "ERROR")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Compliant", compliant_count)
                    col2.metric("Non-Compliant", non_compliant_count)
                    col3.metric("Errors", error_count)
                    
                    st.subheader("Detailed Results")
                    
                    for result in results:
                        with st.expander(f"{result['rule_name']} - {result['status']}"):
                            st.write(result["response"])
                            st.write(f"**Sources:** {', '.join(result['sources'])}")
                    
                    output_file = "compliance_results.json"
                    with open(output_file, "w") as f:
                        json.dump(results, f, indent=2)
                    st.success(f"Results saved to {output_file}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif section == "Rules List":
        st.header("Compliance Rules")
        st.write("View all compliance rules in the system.")
        
        rules_table = []
        for rule in rules:
            rules_table.append({
                "ID": rule["id"],
                "Name": rule["name"],
                "Category": rule["category"],
                "Description": rule["description"]
            })
        
        import pandas as pd
        df = pd.DataFrame(rules_table)
        st.dataframe(df, use_container_width=True)
        
        st.write(f"**Total Rules:** {len(rules)}")

else:
    st.error("Failed to initialize system. Run: python preprocess_documents.py")
