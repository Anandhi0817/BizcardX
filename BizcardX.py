import streamlit as st
from PIL import Image
import easyocr
import sqlite3
import pandas as pd
import numpy as np

input_image = ("/content/3.png")

#sqlite3 Connection
connection = sqlite3.connect('Bizcard.db')
cursor = connection.cursor()

#data Extraction
def extract_information(image_path):
    input_image = Image.open(image_path)
    image_array = np.array(input_image)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_array, detail=0)
    return text, input_image

extracted_text, input_image = extract_information("/content/3.png")

create_query = '''CREATE TABLE IF NOT EXISTS Bizcard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR(225),
                    Designation VARCHAR(225),
                    Address VARCHAR(225),
                    Pincode TEXT,
                    Contact TEXT,
                    Email TEXT,
                    Website VARCHAR(225),
                    Company_Name VARCHAR(225)
                    )'''
cursor.execute(create_query)

data = {
    "Name": extracted_text[0] if len(extracted_text) > 0 else "",
    "Designation": extracted_text[1] if len(extracted_text) > 1 else "",
    "Address": extracted_text[2] if len(extracted_text) > 2 else "",
    "Pincode": extracted_text[3] if len(extracted_text) > 3 else "",
    "Contact": extracted_text[4] if len(extracted_text) > 4 else "",
    "Email": extracted_text[5] if len(extracted_text) > 5 else "",
    "Website": extracted_text[6] if len(extracted_text) > 6 else "",
    "Company_Name": extracted_text[7] if len(extracted_text) > 7 else ""
}

insert_query = '''INSERT INTO Bizcard (Name, Designation, Address, Pincode, Contact, Email, Website, Company_Name)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
values = (
    data["Name"],
    data["Designation"],
    data["Address"],
    data["Pincode"],
    data["Contact"],
    data["Email"],
    data["Website"],
    data["Company_Name"]
)

# Execute the INSERT INTO query
cursor.execute(insert_query, values)

# Commit changes and close connection
connection.commit()

df = pd.DataFrame(data, index=[0])

#streamlit part
def fetch_data():
    cursor.execute("SELECT * FROM Bizcard")
    data = cursor.fetchall()
    return data

# Streamlit part
st.markdown("<h1 style='text-align: center; color: Brown; font-size: 25px; font-family: Arial, sans-serif;'>BizCardX : Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected = st.sidebar.selectbox("Navigation", ["Home", "Upload & Extract Data", "Edit & Download a BizcardX"])

if selected == "Home":
    st.markdown("                 ")
    st.write("Welcome to BizCardX!")
    st.write("BizCardX is a powerful tool that allows you to effortlessly extract contact information from business cards.")
    st.write("With BizCardX, you can simply upload an image of a business card, and our advanced OCR technology will automatically extract key details such as name, email, phone number, and more.")
    st.write("Say goodbye to manual data entry and let BizCardX streamline your workflow. Get started today!")
    # Footer
    st.markdown('<div class="icon-container"><img src="/content/5.png" width="60"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.write("© 2024 BizCardX. All rights reserved.")

if selected == "Upload & Extract Data":
    st.markdown("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
        if st.button('Extract'):
            image = Image.open(uploaded_file)
            image_np = np.array(image)
            extracted_text = extract_information(image_np)
            text_content = [text[1] for text in extracted_text]
            df = pd.DataFrame(text_content, columns=['Extracted Text'])
            st.write(df)

if selected == "Edit a BizcardX":
    st.write("Modify BizcardX Data")
    bizcard_data = fetch_data()
    
    # Displaying data in a DataFrame
    df = pd.DataFrame(bizcard_data, columns=['Id','Name', 'Designation', 'Address', 'Pincode', 'Contact','Email', 'Website', 'Company_Name'])
    st.write(df)

    # Editing the data
    st.write("Edit Data")
    edit_name = st.text_input("Edit Name:")
    edit_designation = st.text_input("Edit Designation:")
    edit_address = st.text_input("Edit Address:")
    edit_pincode = st.text_input("Edit Pincode:")
    edit_contact = st.text_input("Edit Contact:")
    edit_email = st.text_input("Edit Email:")
    edit_website = st.text_input("Edit Website:")
    edit_company_name = st.text_input("Edit Company Name:")

    if st.button("Update"):
      # Update the data in the SQLite database
      cursor.execute("""
          UPDATE Bizcard
          SET Name=?, Designation=?, Address=?, Pincode=?, Contact=?, Email=?, Website=?, Company_Name=?
          WHERE Id=?
      """, (edit_name, edit_designation, edit_address, edit_pincode, edit_contact, edit_email, edit_website, edit_company_name, bizcard_data[0][0]))  # Assuming Id is the first column in your data
      connection.commit()

      # Fetch and display the updated data
      updated_bizcard_data = fetch_data()
      updated_df = pd.DataFrame(updated_bizcard_data, columns=['Id','Name', 'Designation', 'Address', 'Pincode', 'Contact','Email', 'Website', 'Company_Name'])
      st.write("Updated Data:")
      st.write(updated_df)
