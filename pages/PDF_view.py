import streamlit as st
import base64
import os
import pickle
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
import io



def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
def set_background_image(image_path):
    with open(image_path, "rb") as file:
        bg_image = base64.b64encode(file.read()).decode("utf-8")
    st.markdown(f"""<style>.stApp {{background-image: url("data:image/png;base64,{bg_image}");background-size: cover;background-position: center center;background-attachment: fixed;}}</style>""", unsafe_allow_html=True)
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True)
        writer._save()
    processed_data = output.getvalue()
    return processed_data


#def show_pdf(pdf_path):
#    pdf_path = "https://arxiv.org/pdf/2404.03682.pdf"
#    # Display the PDF
#    pdf_viewer_url = f"https://docs.google.com/gview?embedded=true&url={pdf_path}"
#   st.markdown(f'<iframe src="{pdf_viewer_url}" width="500" height="500"></iframe>', unsafe_allow_html=True)

def show_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        html_display = F'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="400" height="500" type="application/pdf"></iframe>'
        st.markdown(html_display, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("PDF not found. Please check the file path.")


# INDECES:
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
pdf_path = os.path.join (dir_PDFs,  str(pdf) + ".pdf")




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





# Add content to the main area
col1, col2 = st.columns([3, 1], gap="small")  

with col1.container(height=500):
    #pdf_viewer(input=pdf_path, width = 500)
    show_pdf(pdf_path)



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



