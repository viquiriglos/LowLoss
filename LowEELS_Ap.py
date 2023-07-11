import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from shapesimilarity import shape_similarity
from math import sqrt  

#---- PATH SETTINGS---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
#css_file = current_dir/"styles"/"main.css"
example_spc = current_dir/"EELS_LowLoss_Fe2O3.csv"


st.write("""
# Low EELS App

This app allows to compare an EELS spectrum with two references, to determine to which phase the analyzed spectrum belongs. Just load your files and set x limits to avoid ZLP and innecessary data and watch the outcome.
Notice that, as the spectra is normalized, an inadequate selection of x limits (for instance, including ZLP) could lead to erroneous results.
The resulting graphs can be downloaded.

""")

#-----------------SideBar

st.sidebar.header('User Input File')

# Collects user input file
uploaded_file1 = st.sidebar.file_uploader("Upload first reference .csv file", type=["csv"])
uploaded_file2 = st.sidebar.file_uploader("Upload second reference .csv file", type=["csv"])
uploaded_file_Exper = st.sidebar.file_uploader("Upload spectrum to be analyzed .csv file", type=["csv"])

# Set the min and max limits in the spectra
x_min= st.sidebar.slider('Set the min. Energy Loss (eV)', 0, 30, 5)
x_max= st.sidebar.slider('Set the Max. Energy Loss (eV)', 30, 100, 50)
y_min= 0
y_max= 1.1

#------------------Main Panel----

# We display a generic plot before loading the files
df_example=pd.DataFrame()
fig = go.Figure()

if uploaded_file1 is None and uploaded_file1 is None and uploaded_file_Exper is None:
    example_df = pd.read_csv(example_spc)
    df_example=pd.DataFrame(example_df)
    cols_exam=df_example.columns
    X_exam= cols_exam[0] #'Energy Loss (eV)' #
    Y_exam= cols_exam[1] #'Intensity' #
    
    fig = px.line(
    x=df_example[X_exam],
    y=df_example[Y_exam], 
    height=325)

    fig.update_layout(
        title="Sample Low Loss EELS spectrum (Fe2O3)",
        xaxis_title="Energy Loss (eV)",
        yaxis_title="Intensity",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[y_min, 5000]),
        height=500,
        #legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
        )
    ) 


# Convert the uploaded files into pandas data frames
df1=pd.DataFrame() #Ref.1
df1b=pd.DataFrame() 
df2=pd.DataFrame() #Ref.2
df2b=pd.DataFrame()
df_Exper=pd.DataFrame() #Espectro que quiero identificar
df_Experb=pd.DataFrame()

# Set initial values
name_Ref1=""
name_Ref2=""
name_Exper=""

X1=""
Y1=""
X2=""
Y2=""
X3=""
Y3=""

E1_max=0
E2_max=0
E3_max=0

DeltaE_pico1=0
DeltaE_pico2=0

Delta_ind=0

# E1_arr = np.array([1,1,1])
# E2_arr = np.array([1,1,1])
# E3_arr_Ref1 = np.array([1,1,1])
# E3_arr_Ref2 = np.array([1,1,1])
# I1_arr = np.array([1,1,1])
# I2_arr = np.array([1,1,1])
# I3_arr = np.array([1,1,1])

factor1=1.0
factor2=1.0
#fig2 = go.Figure()
fig3 = go.Figure()
fig4 = go.Figure()


# Display the names of the uploaded files and save csv to data frame
if uploaded_file1 is not None:
    input_df1 = pd.read_csv(uploaded_file1)
    df1=pd.DataFrame(input_df1)
    file_name1=uploaded_file1.name
    name_Ref1= st.text_input('Set a name for Ref.1', file_name1)


if uploaded_file2 is not None:
    input_df2 = pd.read_csv(uploaded_file2)
    df2=pd.DataFrame(input_df2)
    file_name2=uploaded_file2.name
    name_Ref2= st.text_input('Set a name for Ref.2', file_name2)


if uploaded_file_Exper is not None:
    input_df_Exper = pd.read_csv(uploaded_file_Exper)
    df_Exper=pd.DataFrame(input_df_Exper)
    file_name_Exper=uploaded_file_Exper.name
    name_Exper= st.text_input('Set a name for the spectrum to be identified', file_name_Exper)


# Muestro los nombres de los archivos seleccionados, asigno los nombres de las columnas a variables y grafico
if df1.empty==False:
    cols1=df1.columns
    X1= cols1[0] #'Energy Loss (eV)' #
    Y1= cols1[1] #'Intensity' #
    E1=df1[X1]
    I1=df1[Y1]
    
    # convierto a float los valores de E
    for i in range(len(E1)):
        try:
            E1[i]=float(E1[i])
        except ValueError:
            E1[i]=0

    # creo un nuevo dataframe para esos valores
    df1b=pd.DataFrame({X1: E1, Y1: I1})
    df1b=df1b.loc[df1b[X1]!=0] # como igualé a cero para las excepciones, filtro esos valores

    # Busco el valor de la energia para el maximo
    y1_max=df1b[Y1].loc[df1b[X1]>=x_min].max()
    E1_max=df1b[X1].loc[df1b[Y1]==y1_max].mean()

    x_min_ind1 = (df1b[df1b[X1]>=x_min].index).min()
    x_max_ind1 = (df1b[df1b[X1]<=x_max].index).max()
    Delta_ind = (x_max_ind1 - x_min_ind1)
    # E1_arr = df1b[X1][x_min_ind1:x_max_ind1].to_numpy()
    # I1_arr = df1b[Y1][x_min_ind1:x_max_ind1].to_numpy()

    fig.update_layout(
        title="Low Loss EELS spectra",
        xaxis_title="Energy Loss (eV)",
        yaxis_title="Normalized Intensity",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[y_min, y_max]),
        height=500,
        #legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    ) 

    fig.add_trace(go.Scatter(
        x=df1b[X1],#serie
        y=df1b[Y1]/y1_max, #/y_max1,
        name= name_Ref1, #file_name1, #"Ref. 1",
        mode='lines',
        line=dict(
            color="royalblue"
        )
    ))

    fig3.add_trace(go.Scatter(
        x=df1b[X1],
        y=df1b[Y1]/y1_max,
        name= name_Ref1,
        mode='lines',
        line=dict(
            color="royalblue"
        )
    )) 

    fig3.update_layout(
        #title="Comparison between Unidentified spectrum and Ref.1",
        xaxis_title="Energy Loss (eV)",
        yaxis_title="Normalized Intensity",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[y_min, y_max]),
        height=500,
        #legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
        )
    )


if df2.empty==False:
    cols2=df2.columns
    X2= cols2[0] #'Energy Loss (eV)' #
    Y2= cols2[1] #'Intensity' #
    E2=df2[X2]
    I2=df2[Y2]
    
    for i in range(len(E2)):
        try:
            E2[i]=float(E2[i])
        except ValueError:
            E2[i]=0

    df2b=pd.DataFrame({X2: E2, Y2: I2})
    df2b=df2b.loc[df2b[X2]!=0]

    y2_max=df2b[Y2].loc[df2b[X2]>=x_min].max()
    E2_max=df2b[X2].loc[df2b[Y2]==y2_max].mean()

    x_min_ind2 = (df2b[df2b[X2]>=x_min].index).min()
    x_max_ind2 = (x_min_ind2 + Delta_ind)
    # E2_arr = df2b[X2][x_min_ind2 : x_max_ind2].to_numpy()
    # I2_arr = df2b[Y2][x_min_ind2 : x_max_ind2].to_numpy()

    fig.add_trace(go.Scatter(
        x=df2b[X2],
        y=df2b[Y2]/y2_max,
        name= name_Ref2,
        mode='lines',
        line=dict(
            color="IndianRed"
        )
    ))

    fig4.add_trace(go.Scatter(
        x=df2b[X2],
        y=df2b[Y2]/y2_max,
        name= name_Ref1,
        mode='lines',
        line=dict(
            color="IndianRed"
        )
    )) 

    fig4.update_layout(
        #title="Comparison between Unidentified spectrum and Ref.2",
        xaxis_title="Energy Loss (eV)",
        yaxis_title="Normalized Intensity",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[y_min, y_max]),
        height=500,
        #legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
        )
    )

if df_Exper.empty==False:
    cols3=df_Exper.columns
    X3= cols3[0] #'Energy Loss (eV)' #
    Y3= cols3[1] #'Intensity' #
    E3=df_Exper[X3]
    I3=df_Exper[Y3]
    
    for i in range(len(E3)):
        try:
            E3[i]=float(E3[i])
        except ValueError:
            E3[i]=0

    df_Experb=pd.DataFrame({X3: E3, Y3: I3})
    df_Experb=df_Experb.loc[df_Experb[X3]!=0]

    y3_max=df_Experb[Y3].loc[df_Experb[X3]>=x_min].max()
    E3_max=df_Experb[X3].loc[df_Experb[Y3]==y3_max].mean()

    #Calculo una nueva columna de E para desplazar el pico exper hacia la Ref1. 
    # luego hago lo mismo con la Ref2.
    DeltaE_pico1 = E3_max - E1_max
    DeltaE_pico2 = E3_max - E2_max
    df_Experb['E_shift1'] = df_Experb[X3] - DeltaE_pico1
    df_Experb['E_shift2'] = df_Experb[X3] - DeltaE_pico2

    x_min_ind3 = (df_Experb[df_Experb[X3]>=x_min].index).min()
    x_max_ind3 = (x_min_ind3 + Delta_ind)
    # E3_arr_Ref1 = df_Experb['E_shift1'][x_min_ind3 : x_max_ind3].to_numpy()
    # E3_arr_Ref2 = df_Experb['E_shift2'][x_min_ind3 : x_max_ind3].to_numpy()
    # I3_arr = df_Experb[Y3][x_min_ind3 : x_max_ind3].to_numpy()

    fig.add_trace(go.Scatter(
        x=df_Experb[X3], #x=[0, 10, 20, 30, 40, 50, 60, 70],
        y=df_Experb[Y3]/y3_max, #y=[0, 10000, 30000, 20000, 10000, 5000, 0, 0],
        name= name_Exper, #file_name_Exper, #"Experimental Spectrum",
        mode='lines',
        line=dict(
            color='rgb(255,165,0)'
        )
    ))

    fig3.add_trace(go.Scatter(
        x=df_Experb['E_shift1'],
        y=df_Experb[Y3]/y3_max,
        name= name_Exper,
        mode='lines',
        line=dict(
            color='rgb(255,165,0)'
        )
    ))

    fig4.add_trace(go.Scatter(
        x=df_Experb['E_shift2']*factor2,
        y=df_Experb[Y3]/y3_max,
        name= name_Exper,
        mode='lines',
        line=dict(
            color='rgb(255,165,0)'
        )
    ))

st.write(fig)

st.subheader('Results')

col1, col2 = st.columns([1, 1])
df_max=pd.DataFrame([E1_max, E2_max, E3_max], [name_Ref1, name_Ref2, name_Exper],  columns=["E_peak(eV)"]) 
col1.write(df_max)

df_deltas=pd.DataFrame([DeltaE_pico1, DeltaE_pico2, "-"], ["E_max - E_max_Ref1", "E_max - E_max_Ref2", ""],  columns=["Delta E_peak(eV)"]) 
col2.write(df_deltas)

col1.subheader("Comparing to Ref.1")
col1.write(fig3)

col2.subheader("Comparing to Ref.2")
col2.write(fig4)

# calculo los cuadrados minimos
suma_ref1=0
suma_ref2=0

if df1b.empty==False and df2b.empty==False and df_Experb.empty==False:
    for i in range(Delta_ind):
        suma_ref1 = suma_ref1 + (df_Experb['E_shift1'][x_min_ind3 + i] - df1b[X1][x_min_ind1 + i])**2 #(I3_arr[i] - I1_arr[i])**2
        suma_ref2 = suma_ref2 + (df_Experb['E_shift2'][x_min_ind3 + i] - df2b[X2][x_min_ind2 + i])**2

raiz_suma1 = sqrt(suma_ref1)
raiz_suma2 = sqrt(suma_ref2)

st.write('Sqr Distance for Ref.1', round(raiz_suma1, 2))
st.write('Sqr Distance for Ref.2', round(raiz_suma2, 2))


# Busco el indice de x_min y x_max
# x_min_ind1 = (df1b[df1b[X1]>=x_min].index).min()
# x_max_ind1 = (df1b[df1b[X1]<=x_max].index).max()
# Delta_ind = (x_max_ind1 - x_min_ind1)
# x_min_ind2 = (df2b[df2b[X2]>=x_min].index).min()
# x_max_ind2 = (x_min_ind2 + Delta_ind)
# x_min_ind3 = (dfExperb[dfExperb[X3]>=x_min].index).min()
# x_max_ind3 = (x_min_ind3 + Delta_ind)

#convierto a array de numpy cada columna de df1b, df2b y df_Experb
# entre x_max y x_min y de modo tal que todos los arrays tengan el mismo largo
# E1_arr = df1b[X1][x_min_ind1:x_max_ind1].to_numpy()
# I1_arr = df1b[Y1][x_min_ind1:x_max_ind1].to_numpy()
# E2_arr = df2b[X2][x_min_ind2 : x_max_ind2].to_numpy()
# I2_arr = df2b[Y2][x_min_ind2 : x_max_ind2].to_numpy()
# E3_arr = df_Experb[X3][x_min_ind3 : x_max_ind3].to_numpy()
# I3_arr = df_Experb[Y3][x_min_ind3 : x_max_ind3].to_numpy()


# shape1 = np.column_stack((E1_arr, I1_arr))
# shape2 = np.column_stack((E2_arr, I2_arr))
# similarity = shape_similarity(shape1, shape2)
#st.write(similarity)

#si quiero puedo pasar ambas columnas de df1b a float64 con: df.col.astype('float64')
    #array1= df1.to_numpy()
    #st.write(array1[:5,:]) #el primer rango del array son las filas y el segundo las columnas

# Derivadas
# calculo la derivada de la I (normalizada) respecto de E
    # DX1 = df1b[X1].diff() #defino los deltas de energia
    # DY1 = df1b[Y1].diff() #defino los deltas de intensidad

    # try:
    #     Delta1 = (DY1/DX1)/y1_max  #calculo la derivada
    # except ZeroDivisionError:
    #     Delta1 = DY1/y1_max

    # df1b['Delta'] = Delta1 # asigno la derivada a una nueva columan del df1b
    # Delta1_max = df1b['Delta'].loc[df1b[X1]>=x_min].max()
    # Delta1_min = df1b['Delta'].loc[df1b[X1]>=x_min].min()
    
    # Delta_max = Delta1_max
    # Delta_min = Delta1_min

# calculo la derivada de la I (normalizada) respecto de E
    # DX2 = df2b[X2].diff() #defino los deltas de energia
    # DY2 = df2b[Y2].diff() #defino los deltas de intensidad

    # try:
    #     Delta2 = (DY2/DX2)/y2_max  #calculo la derivada
    # except ZeroDivisionError:
    #     Delta2 = DY2/y2_max

    # df2b['Delta'] = Delta2 # asigno la derivada a una nueva columna del df2b
    # Delta2_max = df2b['Delta'].loc[df2b[X2]>=x_min].max()
    # Delta2_min = df2b['Delta'].loc[df2b[X2]>=x_min].min()

    # if Delta2_max > Delta_max:
    #     Delta_max = Delta2_max

    # if Delta2_min < Delta_min:
    #     Delta_min = Delta2_min

# calculo la derivada de la I (normalizada) respecto de E
    # DX3 = df_Experb[X3].diff() #defino los deltas de energia
    # DY3 = df_Experb[Y3].diff() #defino los deltas de intensidad

    # try:
    #     Delta3 = (DY3/DX3)/y3_max  #calculo la derivada
    # except ZeroDivisionError:
    #     Delta3 = DY3/y3_max

    # df_Experb['Delta'] = Delta3 # asigno la derivada a una nueva columna del df_Experb
    # Delta3_max = df_Experb['Delta'].loc[df_Experb[X3]>=x_min].max()
    # Delta3_min = df_Experb['Delta'].loc[df_Experb[X3]>=x_min].min()

    # if Delta3_max > Delta_max:
    #     Delta_max = Delta3_max

    # if Delta3_min < Delta_min:
    #     Delta_min = Delta3_min

     # fig2.add_trace(go.Scatter(
    #     x=df1b[X1],#serie
    #     y=Delta1,
    #     name= "Derivative of " + name_Ref1, #file_name1, #"Ref. 1",
    #     mode='lines',
    #     line=dict(
    #         color="royalblue"
    #     )
    # )) 

    # fig2.update_layout(
    #     title="Derivative of spectra Intensities with respect to the Energy Loss",
    #     xaxis_title="Energy Loss (eV)",
    #     yaxis_title="DI/DE",
    #     xaxis=dict(range=[x_min, x_max]),
    #     yaxis=dict(range=[Delta_min, Delta_max]),
    #     height=500,
    #     #legend_title="Legend Title",
    #     font=dict(
    #         family="Courier New, monospace",
    #         size=18,
    #     )
    # )    
    # fig2.add_trace(go.Scatter(
    #     x=df2b[X2],
    #     y=Delta2,
    #     name= "Derivative of " + name_Ref2,
    #     mode='lines',
    #     line=dict(
    #         color="IndianRed"
    #     )
    # ))
    # fig2.add_trace(go.Scatter(
    #     x=df_Experb[X3],
    #     y=Delta3,
    #     name= "Derivative of " + name_Exper,
    #     mode='lines',
    #     line=dict(
    #         color='rgb(255,165,0)'
    #     )
    # ))
    #st.write(fig2)

# Este codigo de abajo es para agregar factores para comprimir el grafico
# factor1 = col1.number_input('Insert a X-compression factor for Ref.1', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
# factor1b = col1.number_input('Insert a Y-compression factor for Ref.1', min_value=0.0, max_value=1.0, value=1.0, step=0.1)
# factor2 = col2.number_input('Insert a X-compression factor for Ref.2', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
# factor2b = col2.number_input('Insert a Y-compression factor for Ref.2', min_value=0.0, max_value=1.0, value=1.0, step=0.1)

# if df_Exper.empty==False and (factor1 != 1.0 or factor1b != 1.0):
#     fig3.add_trace(go.Scatter(
#         x = df_Experb['E_shift1']*factor1 - E1_max*(factor1-1), # hay que agregarle un termino que corrija el corrimiento del pico
#         y =df_Experb[Y3]*factor1b/y3_max,
#         name= name_Exper,
#         mode='lines',
#         line=dict(
#         color='rgb(255,165,0)'
#         )
#         ))
# elif df_Exper.empty==False and factor1 == 1.0 and factor1b == 1.0:
#     fig3.add_trace(go.Scatter(
#         x = df_Experb['E_shift1'],
#         y =df_Experb[Y3]/y3_max,
#         name= name_Exper,
#         mode='lines',
#         line=dict(
#         color='rgb(255,165,0)'
#         )
#         ))
# st.write('Factor for Ref.1 (X)', round(factor1, 2))
# st.write('Factor for Ref.2 (X)', round(factor2, 2))

# st.write('Factor for Ref.1 (Y))', round(factor1b, 2))
# st.write('Factor for Ref.2 (Y)', round(factor2b, 2))
