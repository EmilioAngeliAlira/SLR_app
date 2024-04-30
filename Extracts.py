import streamlit as st
import os
import pickle
import pandas as pd
import base64
import io


st.set_page_config(page_title="Multipage App", page_icon="👋")

# conda activate UI_environment
# streamlit run "C:\Users\EmilioAngeli\OneDrive - Alira Health\Documents\SLRAutomationFolder\APP_DEPLOYMENT\Excerpts.py"



# FUNCTIONS:
# Add background image
def set_background_image(image_path):
    with open(image_path, "rb") as file:
        bg_image = base64.b64encode(file.read()).decode("utf-8")
    st.markdown(f"""<style>.stApp {{background-image: url("data:image/png;base64,{bg_image}");background-size: cover; background-position: center center;background-attachment: fixed;}}</style>""", unsafe_allow_html=True)
# Load tables
def load_tables(directory_pickle_files, variable):
    file_path = os.listdir(directory_pickle_files)
    tables = {}
    for file_name in file_path:
        with open(os.path.join(directory_pickle_files, file_name), 'rb') as file:
            tables[file_name.split('.')[0]] = pickle.load(file)  
    return tables[variable]
# Get image as base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()




# Directories and indices
current_directory  = os.getcwd()
dir_output = os.path.join(current_directory, "Output")
dir_PDFs = os.path.join(current_directory, "ArticlesPDFs")
Output_dir = os.path.join(current_directory, "OutputExcelTable.xlsx")
background_image_path = os.path.join(current_directory, "images", "background.png")
logo_img = get_img_as_base64(os.path.join(current_directory, "images", "AHlogo.png"))

set_background_image(background_image_path)

pdf_list =sorted( [el[:-4] for el in os.listdir(dir_PDFs)])
variables_list = sorted([el[:-7] for el in os.listdir(dir_output)])



# Initialize session state
if 'variable_index' not in st.session_state or 'pdf_index' not in st.session_state:
    st.session_state.update({"variable_index": 0, "pdf_index": 0})
if 'df_out' not in st.session_state:
    st.session_state.df_out = pd.DataFrame(index = pdf_list, columns = variables_list)
variable = variables_list[st.session_state.variable_index]
pdf = pdf_list[st.session_state.pdf_index]




# SIDEBAR:
chosen_variable = st.sidebar.selectbox("Current variable:", variables_list, index = st.session_state.variable_index)
chosen_article = st.sidebar.selectbox("Current article:", pdf_list, index = st.session_state.pdf_index)
st.sidebar.write("")
st.sidebar.write("")  
st.sidebar.write("")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # Write each dataframe to a different worksheet.
    st.session_state.df_out.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file to the buffer
    writer._save()
    st.sidebar.download_button(
        label="Download ",
        data=buffer,
        file_name="Table.xlsx",
        mime="application/vnd.ms-excel")
st.sidebar.write("")  
st.sidebar.write("")
st.sidebar.write("")  
# Reduce the space between the horizontal line and the logo
st.sidebar.markdown(f"""<style>.sidebar .sidebar-content {{  display: flex;  flex-direction: column;    justify-content: space-between;  /* This ensures the image sticks to the bottom */ }}.img-container {{  display: flex;  justify-content: center;  /* Center the image horizontally */   align-items: end;  /* Align the image to the bottom */    margin-top: 10px;  /* Decrease top margin to push the image closer to the line */}}.img-container img {{ max-width: 40%;  /* Keep the image smaller */ height: auto;  /* Maintain aspect ratio */   margin-bottom: 20px;  /* Adjust the margin as needed */ }} </style><hr>  <!-- Horizontal line --> <div class="img-container"><img src="data:image/png;base64,{logo_img}" alt="Logo"></div>""", unsafe_allow_html=True)








# Content display logic
output_df = load_tables(dir_output, variable)
text_content = output_df.iloc[st.session_state.pdf_index,1][0]["OpenAI"]
tables_and_figures = output_df.iloc[st.session_state.pdf_index,1][1]




# COLUMNS:
col1, col2 = st.columns([3, 1], gap="small")  # Create three columns

with col1.container(height=500):
    i = 0
    for el in text_content:
        i += 1
        st.write(f"**Extract from '{el}':**")
        st.write(text_content[el])
        if i < len(text_content):
            st.markdown("<hr>", unsafe_allow_html=True)
    if tables_and_figures:
        if text_content:
            st.markdown("""<br><hr style="border: 2px solid #000000; margin-top: 20px; margin-bottom: 20px"><br>""", unsafe_allow_html=True)
        st.write(f"**Tables & figures:**")
        for image_dir in tables_and_figures:
            aux_name = image_dir.split('\\')[-1]
            image_dir = os.path.join(current_directory, "ExtractedTablesAndFigures", aux_name)
            st.image(image_dir + ".png")
    if not text_content and not tables_and_figures:
        st.write(f"**No relevant content found**")




with col2:
    value = st.session_state.df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] if type(st.session_state.df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index]) == str else ' ' 
    key = (st.session_state.pdf_index, st.session_state.variable_index)
    answer = st.text_area(label = "Your answer", key = key, value = value, height = 250)
    next_article = st.button("Next article", use_container_width=True)
    next_variable = st.button("Next variable", use_container_width=True)




if answer:
    st.session_state.df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
if next_article and st.session_state.pdf_index < len(pdf_list)-1:
    st.session_state.pdf_index += 1
    st.rerun()
if next_variable and st.session_state.variable_index < len(variables_list)-1:
    st.session_state.variable_index += 1
    st.rerun()
if chosen_variable != variables_list[st.session_state.variable_index]:
    aux = [i for i in range(len(variables_list)) if variables_list[i] == chosen_variable][0]
    st.session_state.variable_index = aux
    st.rerun()
if chosen_article != pdf_list[st.session_state.pdf_index]:
    aux = [i for i in range(len(pdf_list)) if pdf_list[i] == chosen_article][0]
    st.session_state.pdf_index = aux
    st.rerun()
