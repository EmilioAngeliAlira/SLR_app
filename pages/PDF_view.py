import streamlit as st
import base64
import os
import pickle
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer


# FUNCTIONS
#def show_pdf(pdf_path):
#    st.write(pdf_path)
#    with open(pdf_path, "rb") as f:
#        pdf_bytes = f.read()
#    encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
#    html_display = F"""<embed src="data:application/pdf;base64,{encoded_pdf}" width="400" height="500" type="application/pdf"> """
#    st.markdown(html_display, unsafe_allow_html=True)

def show_pdf(pdf_url):
    pdf_viewer(input=pdf_path, width = 500)
 
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
def set_background_image(image_path):
    with open(image_path, "rb") as file:
        bg_image = base64.b64encode(file.read()).decode("utf-8")
    st.markdown(f"""<style>.stApp {{background-image: url("data:image/png;base64,{bg_image}");background-size: cover;background-position: center center;background-attachment: fixed;}}</style>""", unsafe_allow_html=True)


# INDECES:
current_directory = os.getcwd()

dir_output = os.path.join(current_directory, "Output")
dir_PDFs = os.path.join(current_directory, "ArticlesPDFs")
OutputPickle_dir = os.path.join(current_directory, "OutputExcelTable.pickle")
background_image_path = os.path.join(current_directory, "images", "background.jpg")
logo_img = get_img_as_base64(os.path.join(current_directory, "images", "AHlogo.png"))
set_background_image(background_image_path)


pdf_list =sorted( [el[:-4] for el in os.listdir(dir_PDFs)])
variables_list = sorted([el[:-7] for el in os.listdir(dir_output)])


if 'variable_index' not in st.session_state and 'pdf_index' not in st.session_state:
    st.session_state.variable_index = 0
    st.session_state.pdf_index = 0
variable = variables_list[st.session_state.variable_index]
pdf = pdf_list[st.session_state.pdf_index]
pdf_path = os.path.join (dir_PDFs,  str(pdf) + ".pdf")


# read the output df, create it if it does not exist yet
try:
    with open(OutputPickle_dir, 'rb') as f:
      df_out = pickle.load(f)
except FileNotFoundError:
    df_out = pd.DataFrame(index=pdf_list, columns = variables_list)
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)



# SIDEBAR:
chosen_variable = st.sidebar.selectbox("Current variable:", variables_list, index = st.session_state.variable_index)
chosen_article = st.sidebar.selectbox("Current article:", pdf_list, index = st.session_state.pdf_index)
st.sidebar.write("")  
st.sidebar.write("")
export = st.sidebar.button("Export Excel")
st.sidebar.write("")  
st.sidebar.write("")
st.sidebar.write("")  
st.sidebar.write("")
# Reduce the space between the horizontal line and the logo
st.sidebar.markdown(f"""<style>.sidebar .sidebar-content {{  display: flex;  flex-direction: column;    justify-content: space-between;  /* This ensures the image sticks to the bottom */ }}.img-container {{  display: flex;  justify-content: center;  /* Center the image horizontally */   align-items: end;  /* Align the image to the bottom */    margin-top: 10px;  /* Decrease top margin to push the image closer to the line */}}.img-container img {{ max-width: 40%;  /* Keep the image smaller */ height: auto;  /* Maintain aspect ratio */   margin-bottom: 20px;  /* Adjust the margin as needed */ }} </style><hr>  <!-- Horizontal line --> <div class="img-container"><img src="data:image/png;base64,{logo_img}" alt="Logo"></div>""", unsafe_allow_html=True)



# Add content to the main area
col1, col2 = st.columns([3, 1], gap="small")  

with col1.container(height=500):
    show_pdf(pdf_path)

with col2:
    value = df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] if type(df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index]) == str else ' ' 
    key = (st.session_state.pdf_index, st.session_state.variable_index)
    answer = st.text_area(label = "Your answer", key = key, value = value, height = 250)
    next_article = st.button("Next article", use_container_width=True)
    next_variable = st.button("Next variable", use_container_width=True)



if answer:
    df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)
if next_article and st.session_state.pdf_index < len(pdf_list)-1:
    df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)
    st.session_state.pdf_index += 1
    st.rerun()
if next_variable and st.session_state.variable_index < len(variables_list)-1:
    df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)
    st.session_state.variable_index += 1
    st.rerun()
if chosen_variable != variables_list[st.session_state.variable_index]:
    df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)
    aux = [i for i in range(len(variables_list)) if variables_list[i] == chosen_variable][0]
    st.session_state.variable_index = aux
    st.rerun()
if chosen_article != pdf_list[st.session_state.pdf_index]:
    df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)
    aux = [i for i in range(len(pdf_list)) if pdf_list[i] == chosen_article][0]
    st.session_state.pdf_index = aux
    st.rerun()
if export:
    df_out.iloc[st.session_state.pdf_index, st.session_state.variable_index] = answer
    with open(OutputPickle_dir, 'wb') as f:
        pickle.dump(df_out, f)
    df_out.to_excel(OutputPickle_dir)
