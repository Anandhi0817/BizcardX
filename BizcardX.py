import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import re
import pandas as pd
import sqlite3

reader = easyocr.Reader(['en'])  #Initialize EasyOCR Reader

# SQLite3 Connection
connection = sqlite3.connect('Bizcard.db')
cursor = connection.cursor()

# Function to extract data from image
def data_extract(extract):
    for i in range(len(extract)):
        extract[i] = extract[i].rstrip(' ')
        extract[i] = extract[i].rstrip(',')
    return ' '.join(extract)

def phone(text_content):    #Extract phone numbers
    numbers = []
    for text in text_content:
        if re.findall(r'^[+]?[\d-]+$', text): 
            numbers.append(text)
    return numbers

def email(text_content):
    for text in text_content:  #Extract email from text
        if re.findall(r'[\w\.-]+@[\w\.-]+', text):
            return text
    return None

def website(text_content):     #Extract website from text
    for text in text_content:
        if re.findall(r'^WWW\.\w+\.com$', text):
            return text
    return "Not Available"

def name(text_content):       #Extract name from text
    return text_content[0] if text_content else None

def designation(text_content):    #Extract designation from text
    return text_content[1] if len(text_content) > 1 else None

def address(text_content):        #Extract address from text
    for text in text_content:
        if re.findall(r'^123\s[\w\.-]+', text):
            return text.split('123', 1)[1].strip()
    return "Not Available"

def company_name(text_content):   #Extract company name from text
    for text in reversed(text_content):
        if len(text) > 5:
            return text
    return "Not Available"

def district(text_content):       #Extract district from text
    for text in text_content:
        if re.search(r'^123\s', text):
            return re.sub(r'\W+', ' ', text[4:14]).strip()
        elif "Erode" in text:
            return "Erode"
    return "Not Available"

def pincode(text_content):        #Extract pincode from text
    for text in text_content:
        match = re.search(r'\b\d{6}\b', text)
        if match:
            return match.group()
    return "Not Available"

def state(text_content):          #Extract state from text
    for text in text_content:
        if "TamilNadu" in text:
            return "Tamil Nadu"
    return "Not Found"

def extract_data(image):          #Eextracted data
    text = reader.readtext(np.array(image))
    text_content = [result[1] for result in text]
    return {
        'Name': name(text_content),
        'Designation': designation(text_content),
        'Company_Name': company_name(text_content),
        'Contact': phone(text_content),
        'Email': email(text_content),
        'Website': website(text_content),
        'Address': address(text_content),
        'State': state(text_content),
        'Pincode': pincode(text_content)
    }

def insert_data_into_db(data):      #Insert extracted data into SQLite 
    contact_str = ', '.join(data['Contact'])
    cursor.execute('''INSERT INTO Bizcard (Name, Designation, Company_Name, Contact, Email, Website, Address, State, Pincode)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (data['Name'], data['Designation'], data['Company_Name'], contact_str, 
                       data['Email'], data['Website'], data['Address'], data['State'], data['Pincode']))
    connection.commit()
#SQLite database table
cursor.execute('''CREATE TABLE IF NOT EXISTS Bizcard (
                    Name TEXT,
                    Designation TEXT,
                    Company_Name TEXT,
                    Contact TEXT,
                    Email TEXT,
                    Website TEXT,
                    Address TEXT,
                    State TEXT,
                    Pincode TEXT
                )''')

# Streamlit part
st.markdown("<h1 style='text-align: center; color: Brown; font-size: 25px; font-family: Arial, sans-serif;'>BizCardX : Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected = st.sidebar.selectbox("Navigation", ["Home", "Upload & Extract Data", "View & Modify"])

# Home page
if selected == "Home":
    st.markdown("                 ")
    st.write("Welcome to BizCardX !")
    st.write("BizCardX is a powerful tool that allows you to effortlessly extract contact information from business cards.")
    st.write("With BizCardX, you can simply upload an image of a business card, and our advanced OCR technology will automatically extract key details such as name, email, phone number, and more.")
    st.write("Say goodbye to manual data entry and let BizCardX streamline your workflow. Get started today!")
    # Footer
    st.markdown('<div class="icon-container"><img src="/content/5.png" width="60"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.write("© 2024 BizCardX. All rights reserved.")
    
# Upload & Extract Data page
if selected == "Upload & Extract Data":
    st.markdown("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
            image = Image.open(uploaded_file)
            extracted_data = extract_data(image)
            insert_data_into_db(extracted_data)  # Insert into SQLite
        with col2:
            df = pd.DataFrame.from_dict(extracted_data, orient='index', columns=['Extracted Data'])     #Dataframe Convertion
            st.write(df)

# View & Modify page
if selected == "View & Modify":
    st.markdown("View & Modify Extracted Data")
    cursor.execute("SELECT * FROM Bizcard")  #Fetch data from SQLite
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=['Name', 'Designation', 'Company_Name', 'Contact', 'Email', 'Website', 'Address', 'State', 'Pincode'])
    if not df.empty:
        st.write(df)
    st.markdown("Modify Extracted Data")
    selected_row = st.number_input("Select Row Number to Modify", min_value=1, max_value=len(df), value=1, step=1)

    # Display the selected row's data
    selected_data = df.iloc[selected_row - 1]
    st.write("Selected Data:")
    st.write(selected_data)
    #Modify specific fields
    st.markdown("Modify Specific Fields")
    modified_data = selected_data.copy()
    modified_data['Name'] = st.text_input("Name", selected_data['Name'])  # Modify Name
    modified_data['Designation'] = st.text_input("Designation", selected_data['Designation'])   # Modify Designation
    modified_data['Company_Name'] = st.text_input("Company Name", selected_data['Company_Name'])     # Modify Company Name
    modified_data['Contact'] = st.text_input("Contact", selected_data['Contact'])    # Modify Contact
    modified_data['Email'] = st.text_input("Email", selected_data['Email'])      # Modify Email
    modified_data['Website'] = st.text_input("Website", selected_data['Website'])   # Modify Website
    modified_data['Address'] = st.text_input("Address", selected_data['Address'])   # Modify Address
    modified_data['State'] = st.text_input("State", selected_data['State'])          # Modify State
    modified_data['Pincode'] = st.text_input("Pincode", selected_data['Pincode'])     # Modify Pincode
     #Data in the DataFrame
    df.iloc[selected_row - 1] = modified_data
    # Display the updated DataFrame
    st.write("Updated Data:")
    st.write(df)
    # Update data in the SQLite database
    cursor.execute("DELETE FROM Bizcard")
    for index, row in df.iterrows():
        cursor.execute('''INSERT INTO Bizcard (Name, Designation, Company_Name, Contact, Email, Website, Address, State, Pincode)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (row['Name'], row['Designation'], row['Company_Name'], row['Contact'], row['Email'],
                        row['Website'], row['Address'], row['State'], row['Pincode']))
    connection.commit()
else:
    st.write("No data available to view and modify.")
