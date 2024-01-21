import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from itertools import zip_longest
import math
import json # für material import
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize # normalizing für die colormaps
from matplotlib.cm import ScalarMappable # color maps
import random # für random Nummer
import secrets # für random Hex Farbe
import copy # um st.session_state werte zu kopieren ohne diese weiter zu referenzieren
import requests # um material.json auf github abzufragen

st.set_page_config(
    page_title="fragwerk Fachwerkrechner",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/oelimar/images/main/fragwerk_icon.png"
)

#svg_path = r"C:\Users\DerSergeant\Desktop\fragwerk\fragwerk.png"



st.title("")
st.image("https://raw.githubusercontent.com/oelimar/images/main/fragwerk.png", width=300)

col0_1, col0_2 = st.columns([0.8, 0.2], gap="large")
with col0_1:
    st.title("dein Fachwerkrechner")
    st.title("")

with col0_2:
    Tester = st.toggle("Tester",)
    debug = st.toggle("Debug Mode")
    #st.text_input("test", label_visibility="collapsed", value="test", disabled=True, type="password")

#st.markdown(f":red[Das Programm befindet sich noch im Aufbau. Verzeihen Sie eventuelle Fehler oder Mängel.]")

trussOptions = [
    "Strebenfachwerk",
    "Parallelträger"
    #"Dreiecksfachwerk"
]

roofOptions = {
    "Schwer" : 1,
    "Mittelschwer" : 0.5,
    "Leicht" : 0.3
}

roofOptions2 = [
    "Schwer",
    "Mittelschwer",
    "Leicht",
    "Eigener Aufbau"
]

roofLayers = {
    "Schwer" : {
        1 : ("Kies 5cm", 1),
        2 : ("zweilagige Dachabdichtung", 0.15),
        3 : ("Dämmstoff 20cm", 0.8),
        4 : ("Dampfsperre", 0.07),
        5 : ("BSH 4cm", 0.12)
    },
    "Mittelschwer" : {
        1 : ("zweilagige Dachabdichtung", 0.15),
        2 : ("Dämmstoff 15cm", 0.6),
        3 : ("Dampfsperre", 0.07),
        4 : ("Trapezblech", 0.125)
    },
    "Leicht" : {
        1 : ("zweilagige Dachabdichtung", 0.15),
        2 : ("Dämmstoff 5cm", 0.2),
        3 : ("Dampfsperre", 0.07),
        4 : ("Trapezblech", 0.125)
    },
    "Eigener Aufbau" : {
        1 : ("Schicht 1", 0),
        2 : ("Schicht 2", 0),
        3 : ("Schicht 3", 0),
        4 : ("Schicht 4", 0),
        5 : ("Schicht 5", 0)
    }

}

roofColors = {
    "Intensive Dachbegrünung" : "#60b9cb",
    "Extensive Dachbegrünung" : "#6082cb",
    "Photovoltaik" : "#a060cb",
    "Dachlast" : "#CB6062",
    "Windlast" : "#60C5CB",
    "Schneelast" : "#5F6969"
}

roofAdditives = {
    "Intensive Dachbegrünung" : 2.8,
    "Extensive Dachbegrünung" : 1.5,
    "Photovoltaik" : 0.15
}

defaultPathLocal = r"C:\Users\DerSergeant\Desktop\fragwerk\materials.json"
defaultPathGithub = "https://raw.githubusercontent.com/oelimar/images/main/materials.json"

def load_json_file(file_url, file_path):
    try:
        response = requests.get(file_url)
        #st.text(response)
        response.raise_for_status()
        #st.text(response.raise_for_status())
        materialSelect = json.loads(response.text)
        #st.text(response.text)
        #st.text(f"loaded Github URL")
        return materialSelect

    except Exception as e:
        with open(file_path, "r") as json_file:
            materialSelect = json.load(json_file)
            #st.text(f"local File had to be used. Error: {e}")
        return materialSelect

if "loaded_json" not in st.session_state:
    st.session_state.loaded_json = load_json_file(defaultPathGithub, defaultPathLocal)

materialSelect = st.session_state.loaded_json

#Tabelle der Dichten für Gewichtsberechnung. "Material" : [Dichte in kg/m³]
materialDensity = {
    "Holz" : 500,
    "Stahl" : 7850
}


def draw_test_truss(num_nodes, force_range):
    # Generate random forces for each strut
    forces = [random.uniform(force_range[0], force_range[1]) for _ in range(num_nodes - 1)]
    st.text(forces)
    length = 1

    # Generate node positions
    nodes = np.linspace(0, 1, num_nodes)

    nodes = []
    
    i = 0
    while i <= num_nodes:
        if i % 2 != 0:
            nodes.append((i*(length/num_nodes), 0.1))
        if i % 2 == 0:
            nodes.append((i*(length/num_nodes), 0))
        i += 1

    st.text(nodes)
    st.text(range(num_nodes - 1))
    # Create Matplotlib figure
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='datalim')  # Equal aspect ratio for a clearer visualization

    # Plot the truss with individual line widths representing the force
    for i in range(num_nodes - 1):
        if forces[i] < 0:
            color = "red"
        elif forces[i] > 0:
            color = "blue"
        else:
            color = "black"
        width = 0.1 + 2 * (forces[i] - force_range[0]) / (force_range[1] - force_range[0])  # Scale line width based on force
        if int(forces[i]) == 0:
            width = 0.1
        ax.plot([nodes[i][0], nodes[i + 1][0]], [nodes[i][1], nodes[i + 1][1]], color=color, linewidth=width)
        for node in nodes:
            ax.plot(node[0], node[1], color="black", marker='o', markersize=3)

    ax.set_xlim(0, 1)
    ax.set_ylim(-1, 1)
    ax.axis('off')  # Turn off axis labels

    st.pyplot(fig)


if Tester == True:
    num_nodes = st.slider("Number of Nodes:", min_value=2, max_value=20, value=10)
    force_range = st.slider("Force Range:", min_value=-10.0, max_value=10.0, value=(2.0, 8.0))
    draw_test_truss(num_nodes, force_range)


# Funktion um die Eingabe von Werten mit Kommas zu ermöglichen
def correctify_input(value):
    try:
        #variable initialisieren
        numberString = ""

        #iteriere durch alle Ziffern um Zahlen, Punkte und Kommata zu extrahieren, Falls jemand einen Buchstaben eintippt.
        for character in str(value):
            if character.isdigit() or character == "." or character == ",":
                numberString += character

        valueChanged = str(numberString).replace(",", ".")
        valuePositive = abs(float(valueChanged))  # make value positive in case anyone is funny enough to enter negative distance
        return valuePositive
    except ValueError:
        return None

# Funktion, um Errormeldung zu schreiben, falls correctify_input ein None returned
def print_error_and_set_default(default):
        st.markdown(":red[Bitte gültigen Wert eingeben!]")
        st.markdown(f"Es wird mit {default}m weitergerechnet.")

        return default




snow_mapping_2 = {
            1: 1.05,
            2: 2.06,
            3: 3.07
        }
wind_mapping_2 = {
            1: 0.5,
            2: 0.7,
            3: 0.9,
            4: 1.2
        }

snow_mapping = {
    200 : (0.65, 0.85, 1.10),
    300 : (0.65, 0.89, 1.29),
    400 : (0.65, 1.21, 1.78),
    500 : (0.84, 1.60, 2.37),
    600 : (1.05, 2.06, 3.07),
    700 : (1.30, 2.58, 3.87),
    800 : (1.58, 3.17, 4.76),
    900 : (None, 3.83, 5.76),
    1000 : (None, 4.55, 6.86),
    1100 : (None, 5.33, 8.06),
    1200 : (None, 6.19, 9.36),
    1300 : (None, None, 10.76),
    1400 : (None, None, 12.26),
    1500 : (None, None, 13.86)
}



lambda_values = {
    "Holz":{
        30 : 0.998,
        35 : 0.972,
        40 : 0.941,
        45 : 0.900,
        50 : 0.849,
        55 : 0.785,
        60 : 0.715,
        65 : 0.644,
        70 : 0.577,
        75 : 0.516,
        80 : 0.463,
        85 : 0.417,
        90 : 0.376,
        95 : 0.341,
        100 : 0.310,
        105 : 0.283,
        110 : 0.260,
        115 : 0.239,
        120 : 0.221,
        125 : 0.204,
        130 : 0.189,
        135 : 0.176,
        140 : 0.164,
        145 : 0.154,
        150 : 0.144

    },
    "Stahl":{
        20 : 0.995,
        25 : 0.975,
        30 : 0.956,
        35 : 0.935,
        40 : 0.914,
        45 : 0.891,
        50 : 0.867,
        55 : 0.841,
        60 : 0.813,
        65 : 0.784,
        70 : 0.753,
        75 : 0.720,
        80 : 0.686,
        85 : 0.652,
        90 : 0.617,
        95 : 0.583,
        100 : 0.549,
        105 : 0.517,
        110 : 0.487,
        115 : 0.458,
        120 : 0.431,
        125 : 0.406,
        130 : 0.382,
        135 : 0.360,
        140 : 0.340,
        145 : 0.321,
        150 : 0.303
    }
}

sigmas = {
    "Holz" : (1.3, 0.9), # (Druck, Zug)
    "Stahl" : (21.8, 21.8)
}

fieldSettings = {
    "Strebenfachwerk" : (1, 3, 3), # step, start value, min value
    "Parallelträger"  : (2, 4, 4)
}

# Einstellung der Breiten für das gesamte Layout
columnsParameters = [0.45, 0.55]


with st.container(border=True):
    st.subheader("Lasteinzugsfeld", divider="red")

    col1, col2 = st.columns(columnsParameters, gap="large")


    with col1:

        trussDistanceInput = st.text_input("Träger Abstand [m]", value="5.25")
        trussDistance = correctify_input(trussDistanceInput)
        if trussDistance == None:   # falls ungültiger Wert erkannt wird, Warnung anzeigen
            trussDistance = print_error_and_set_default(5.25)   # standardwert einfügen, damit bei Error script nicht abbricht

        #with st.expander("Dachaufbau"):
        if 'roofAdditives' not in st.session_state:
            st.session_state.roofAdditives = roofAdditives
        if "roofColors" not in st.session_state:
            st.session_state.roofColors = roofColors

        if "currentSelection" not in st.session_state:
            st.session_state.currentSelection = None

        #st.text(st.session_state.currentSelection.keys())
        #st.text(st.session_state.roofAdditives.keys())

        if st.session_state.currentSelection == None:
            roofAdded_default = []
        else:
            roofAdded_default = st.session_state.currentSelection.keys()
        #st.text(roofAdded_default)

        #st.markdown("<div style='font-size: 13px; font-weight: 100;'>Anzeige Lasten</div>", unsafe_allow_html=True)
        #col0_1, col0_2 = st.columns([0.5, 0.5], gap="small")
        #with col0_1:
            #lastAnzeige_einfach = st.button("Einfach", use_container_width=True)

        #with col0_2:
            #lastAnzeige_einfach = st.button("Erweitert", use_container_width=True


        # Theoretisch ursprüngliche Auswahlmöglichkeit für Ansicht
        #lastAnzeige = st.radio("Anzeige Lasten", ["Einfach", "Erweitert"], 0, horizontal=True)
        
        lastAnzeige = "Erweitert"   # Ansicht bis aufs weitere als "Erweitert" festgelegt




        
        
        roofTypeExpander = st.expander("Dachaufbau")
        with roofTypeExpander:
                
                
            #roofType = st.selectbox("Dachaufbau [kN/m²]", placeholder="Wähle einen Dachaufbau", index=1, options=roofOptions.keys())   #old save
            roofType = st.selectbox("Dachaufbau", placeholder="Wähle einen Dachaufbau", index=1, options=roofOptions2, label_visibility="collapsed")
            st.image("https://www.ing-büro-junge.de/assets/images/Belastungen-Dachschichtenaufbau-2.jpg", use_column_width=True)

            # initialisiere Variablen
            roofLayerSum = 0
            flat_data = []

            # anfängliche Bearbeitbarkeit in Abhängigkeit von Einstellung des Dachaufbaus
            if roofType == "Eigener Aufbau":
                roofEditValue = True
            else:
                roofEditValue = False

            roofEdit = st.toggle("Dachlagen bearbeiten", value=roofEditValue)
            # roofLayers JSON struktur in Pandas struktur umwandeln
            for layer, (layer_name, value) in roofLayers[roofType].items():
                flat_data.append({
                "Lage": str(layer),
                "Bezeichnung": layer_name,
                "Last [kN/m²]": value
                })
            # erzeuge DataFrame
            df = pd.DataFrame(flat_data)

            if roofEdit == True:
                # erstelle bearbeitbaren DataFrame als Widget
                edited_df = st.data_editor(df, hide_index=True, num_rows="fixed", use_container_width=True, disabled=["Lage"])
            else:
                # erstelle statischen DataFrame für bessere Darstellung
                st.dataframe(df, hide_index=True, use_container_width=True)
                edited_df = df

            # Aufsummieren aller Werte der Spalte "Last [kN/m²]"
            roofLayerSum = abs(edited_df["Last [kN/m²]"]).sum()     # abs() damit Negative eingaben trotzdem richtig addiert werden
            # Auf 2 Nachkommastellen runden
            roofLayerSum = round(roofLayerSum, 2)
            st.markdown(f"Die Gesamtlast beträgt **{roofLayerSum} kN/m²**.")

        

        
        
        roofAdded = st.multiselect("Zusätzliche Dachlasten", st.session_state.roofAdditives.keys(), default=roofAdded_default, placeholder="Wähle hier zusätzliche Lasten", label_visibility="collapsed")

        if roofAdded != []:
            st.session_state.currentSelection = {}
            for name in roofAdded:
                st.session_state.currentSelection[name] = copy.deepcopy(st.session_state.roofAdditives[name])


        addButton = st.button("Eigene Last hinzufügen", type="primary", use_container_width=True, disabled=False)

        col1_1, col1_2, col1_3 = st.columns([0.5, 0.3, 0.1], gap="small")
        with col1_1:
            customAdditive = st.text_input("Bezeichnung", label_visibility="collapsed", placeholder="Bezeichnung", value="")
        with col1_2:
            customValueInput = st.text_input("Last",  label_visibility="collapsed", placeholder="Last in kN/m²", value="")
            customValue = correctify_input(customValueInput)
        with col1_3:
            customColor = st.color_picker("Farbe", label_visibility="collapsed", value="#FFFFFF")

        #addButton = st.button("Eigene Last hinzufügen", type="primary", use_container_width=True, disabled=False)

        # counter, um Anzahl an unbenannten Lasten zu zählen
        if "additiveCounter" not in st.session_state:
            st.session_state.additiveCounter = 1

        if addButton:
            try:
                # test ob Bezeichnugsfeld leer ist
                if customAdditive == "":
                    customAdditive = "Eigene Last " + str(st.session_state.additiveCounter) # Falls keine Bezeichnung eingetragen wird, wird automatisch immer ein neuer Name generiert.
                    st.session_state.additiveCounter += 1

                float_value = float(customValue)
                st.session_state.roofAdditives[customAdditive] = float_value
                if customColor == "#FFFFFF":
                    customColor = "#" + secrets.token_hex(3) # generiere random HEX Farbcode "#123456"
                st.session_state.roofColors[customAdditive] = customColor

                if st.session_state.currentSelection == None:
                    st.session_state.currentSelection = {}
                st.session_state.currentSelection[customAdditive] = float_value
                st.rerun()
                    
                # Warnung, falls Wert bei Knopfdruck keinen sinnvollen Wert bilden kann
            except (ValueError, TypeError):     #ValueError, falls nur ein string übrigbleibt; TypeError falls versucht wird float(None) zu bilden, wenn correctify_input() None ausgibt
                st.markdown(":red[Last unzulässig. Bitte Wert in [kN/m²] angeben.]")

        with st.expander("veränderliche Lasten"):
            
            heightZoneInput = st.text_input("Geländehöhe über NN [m]", value=400 )
            heightZone = correctify_input(heightZoneInput)
            if heightZone == None:
                heightZone = 400
                st.markdown(":red[Bitte gültigen Wert eingeben!]")
                st.markdown(f"Es wird mit {heightZone}m weitergerechnet.")

            if int(heightZone) > 1500:
                st.markdown(":red[Werte bis maximal 1500m!]")
                st.markdown(f"Es werden anstelle von {heightZone}m die Werte für 1500m angezeigt.")
                heightZone = 1500

            for height in snow_mapping.keys():
                if int(height) >= int(heightZone):
                    if debug == True:
                        st.text(height)
                    snowHeight = height
                    break
            
            
            if snow_mapping[snowHeight][0] == None: # anpassen der maximal/mininmalwerte für Schneezonen in Bezug auf Geländehöhe
                snowMinValue = 2
                if snow_mapping[snowHeight][1] == None: # anpassen der maximal/mininmalwerte für Schneezonen in Bezug auf Geländehöhe
                    snowMinValue = 3
            else:
                snowMinValue = 1

            col1_4, col1_5 = st.columns([0.5, 0.5], gap="small")
            with col1_4:
                windZone = st.number_input("Windlastzone", help="Wähle Anhand der Lage auf der Karte eine der 4 Windlastzonen", step=1, value=2, min_value=1, max_value=4)
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShbi3oQsR2FrAbMAkfjh-Fw-ODeuYsS9NZrAojIXYJCWXZsK65qCyQejR-QJaFzEmheEY&usqp=CAU", caption="Windlastzonen in DE")

            with col1_5:
                snowZone = st.number_input("Schneelastzone", help="Wähle Anhand der Lage auf der Karte eine der 3 Schneelastzonen", step=1, value=snowMinValue, min_value=snowMinValue, max_value=3)
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4A-8ZgmAVEg-fwtBN1ndVuCaCfbG3p5VOpwya0ZXY7NljUrRNvYoH4Hng9DVW0TriyDM&usqp=CAU", caption="Schneelastzonen in DE")

        snowForce = snow_mapping_2[snowZone] * 0.8 # berechnung wie in Tabellenbuch
        snowForce = snow_mapping[snowHeight][snowZone - 1] * 0.8

        windForce = wind_mapping_2[windZone] * 0.2
        roofForce = roofLayerSum

        for force in roofAdded:
            roofForce += st.session_state.roofAdditives[force]

        qTotal = snowForce + windForce + roofForce
        qTotalField = qTotal * trussDistance

    #with col2:
        #st.text("GRAPH LEF")


with st.container(border=True):
    st.subheader("Fachwerk", divider="red")
    col3, col4 = st.columns(columnsParameters, gap="large")
    
    with col3:
        

        trussType = st.selectbox("Fachwerkart", placeholder="Wähle ein Fachwerk", options=trussOptions, index=0)

        if trussType == "Parallelträger":
            strebenParallel = st.selectbox("Streben", options=["Fallende Diagonalen", "Steigende Diagonalen"], label_visibility="collapsed",)

        trussWidthInput = st.text_input("Spannweite [m]", value="12")
        trussWidth = correctify_input(trussWidthInput)
        if trussWidth == None:
            trussWidth = print_error_and_set_default(12)

        trussHeightInput = st.text_input("Statische Höhe [m]", value=trussWidth/10)
        trussHeight = correctify_input(trussHeightInput)
        if trussHeight == None:
            trussHeight = print_error_and_set_default(trussWidth/10)

        fieldNumber = int(st.number_input("Anzahl an Fächern", step=fieldSettings[trussType][0], value=fieldSettings[trussType][1], min_value=fieldSettings[trussType][2], max_value=20))
        distanceNode = round(trussWidth / fieldNumber, 2)



with st.container(border=True):
    st.subheader("Querschnitte", divider="red")
    st.write("")
    
    struts_all_combined = {}

    querschnittContainer = st.container(border=False)
    obergurtColumn, strebenColumn, untergurtColumn = st.columns([1, 1, 1], gap="medium")
    
    with querschnittContainer:
        ALL_col_1, ALL_col_2 = st.columns(columnsParameters, gap="large")
        allOrEach = st.toggle("Individuelle Eingabe")
        
        if allOrEach == False:
            with ALL_col_1:
                ALL_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="ALL_material")
            with ALL_col_2:
                ALL_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[ALL_material].keys(), key="ALL_profile")
            
            OG_material = ST_material = UG_material = ALL_material
            OG_profile = ST_profile = UG_profile = ALL_profile

        with obergurtColumn:
            st.subheader("Obergurt")            
            #strutToCheck = st.selectbox("Dimensionierung durchführen an", ["Obergurt", "Streben", "Untergurt"], index=0)
                
            OG_col_5_1, OG_col_5_2 = st.columns([0.4, 0.6], gap="small")
            #st.text("Eingabe Querschnitt")

            # st.text(materialSelect.keys())
            if allOrEach == True:
                with OG_col_5_1:
                    OG_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="OG_material")  # key attribut, damit sich selectboxen untereinander unterscheiden
                    # st.text(material)
                with OG_col_5_2:
                    OG_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[OG_material].keys(), key="OG_profile")

            if OG_material in sigmas:
                sigma_rd = sigmas[OG_material]
            else:
                st.markdown(":red[Zu dem Material ist keine Randspannung vorhanden.]")
                sigmaInput = st.text_input("", placeholder="Randspannung in kN/cm²")
                if sigmaInput:
                    sigma_rd = sigmaInput

                

            OG_stress_expander = st.expander("Spannungsnachweis")
            with OG_stress_expander:
                OG_stress_einheiten = st.container()
                OG_stress_latex = st.container()

        with strebenColumn:
            st.subheader("Streben")
                
            #strutToCheck = st.selectbox("Dimensionierung durchführen an", ["Obergurt", "Streben", "Untergurt"], index=0)
                
            ST_col_5_1, ST_col_5_2 = st.columns([0.4, 0.6], gap="small")
            #st.text("Eingabe Querschnitt")

            # st.text(materialSelect.keys())
            if allOrEach == True:
                with ST_col_5_1:
                    ST_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="ST_material")
                    # st.text(material)
                with ST_col_5_2:
                    ST_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[ST_material].keys(), key="ST_profile")

            if ST_material in sigmas:
                ST_sigma_rd = sigmas[ST_material]
            else:
                st.markdown(":red[Zu dem Material ist keine Randspannung vorhanden.]")
                ST_sigmaInput = st.text_input("", placeholder="Randspannung in kN/cm²")
                if sigmaInput:
                    ST_sigma_rd = ST_sigmaInput

                

            ST_stress_expander = st.expander("Spannungsnachweis")
            with ST_stress_expander:
                ST_stress_einheiten = st.container()
                ST_stress_latex = st.container()

        with untergurtColumn:
            st.subheader("Untergurt")
                
            #strutToCheck = st.selectbox("Dimensionierung durchführen an", ["Obergurt", "Streben", "Untergurt"], index=0)
                
            UG_col_5_1, UG_col_5_2 = st.columns([0.4, 0.6], gap="small")
            #st.text("Eingabe Querschnitt")

            # st.text(materialSelect.keys())
            if allOrEach == True:
                with UG_col_5_1:
                    UG_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="UG_material")
                    # st.text(material)
                with UG_col_5_2:
                    UG_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[UG_material].keys(), key="UG_profile")

            if UG_material in sigmas:
                UG_sigma_rd = sigmas[UG_material]
            else:
                st.markdown(":red[Zu dem Material ist keine Randspannung vorhanden.]")
                UG_sigmaInput = st.text_input("", placeholder="Randspannung in kN/cm²")
                if sigmaInput:
                    UG_sigma_rd = UG_sigmaInput

                

            UG_stress_expander = st.expander("Spannungsnachweis")
            with UG_stress_expander:
                UG_stress_einheiten = st.container()
                UG_stress_latex = st.container()
    
    kraefteContainer = st.container(border=True)
    with kraefteContainer:
        col6_1, col6_2, col6_3 = st.columns([0.3, 0.3, 0.3], gap="medium")

    bauteilContainer = st.container(border=False)
    with bauteilContainer:
        bauteilExpander = st.expander("Bauteilliste", expanded=True)


def draw_q_over_truss(minNodeX, minNodeY, ax):
    qNodes = [
        [minNodeX, minNodeY + trussHeight * 4/3],
        [minNodeX, minNodeY + 0.5 + trussHeight * 4/3],
        [minNodeX + trussWidth, minNodeY + 0.5 + trussHeight * 4/3],
        [minNodeX + trussWidth, minNodeY + trussHeight * 4/3]
    ]

    ax.fill([point[0] for point in qNodes], [point[1] for point in qNodes], color="white", facecolor="lightblue", hatch="|", alpha=0.7)
    ax.annotate(f"q = {float(qTotalField):.2f} kN/m", (minNodeX + trussWidth / 2, minNodeY + 0.5 + trussHeight * 4.5/3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)

def draw_mass_band(minNodeX, minNodeY, ax):
    
    ax.plot(minNodeX, minNodeY / 2, "k+", markersize=10)
    ax.plot(minNodeX + trussWidth, minNodeY / 2, "k+", markersize=10)
    ax.plot([minNodeX, minNodeX + trussWidth], [minNodeY / 2, minNodeY / 2], "k-", linewidth=1)

    measure = 0
    while measure < fieldNumber + 1:
        ax.plot(minNodeX + measure * distanceNode, 2* minNodeY / 3, "k+", markersize=10)
        if measure < fieldNumber:
            ax.plot([minNodeX + measure * distanceNode, minNodeX + (measure + 1) * distanceNode],[2 * minNodeY / 3, 2 * minNodeY / 3], "k-", linewidth=1)
            ax.annotate(f"{float(distanceNode):.2f}m", (minNodeX + distanceNode / 2 + measure * distanceNode, 3 * minNodeY / 4), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)
        measure += 1

    # create Massband Hoehe
    ax.plot(minNodeX / 2, minNodeY, "k+", markersize=10)
    ax.plot(minNodeX / 2, minNodeY + trussHeight, "k+", markersize=10)
    ax.plot([minNodeX / 2, minNodeX / 2], [minNodeY, minNodeY + trussHeight], "k-", linewidth=1)

    # Annotate width and height
    ax.annotate(f"{float(trussWidth):.2f}m", (minNodeX + trussWidth / 2, minNodeY / 3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)
    ax.annotate(f"{float(trussHeight):.2f}m", (minNodeX / 3, minNodeY + trussHeight / 2), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, rotation=90, annotation_clip=False)

def set_ax_settings(minNodeX, minNodeY, ax):

        # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_xlim([0, trussWidth + 2 * minNodeX])
    ax.set_ylim([0, trussHeight + 2 * minNodeY])

    ax.set_aspect(1.5, adjustable='datalim')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

def draw_truss_parallel(strebenParallel):
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNodeY = minNodeY + trussHeight
    nrNode = int(fieldNumber) + 1

    nodeArray = []

    i = 0
    while i < nrNode:
        nodeArray.append((float(minNodeX + i * distanceNode), minNodeY))
        nodeArray.append((float(minNodeX + i * distanceNode), maxNodeY))
        i += 1

    fig, ax = plt.subplots()

    edges = []

    i = 0
    while i < fieldNumber/2:
        if strebenParallel == "Fallende Diagonalen":
            edgesFront = [
                (1 + i*2, 0 + i*2),
                (0 + i*2, 2 + i*2),
                (2 + i*2, 1 + i*2),
                (1 + i*2, 3 + i*2),
                (3 + i*2, 2 + i*2)
            ]
        else:
            edgesFront = [
                (0 + i*2, 1 + i*2),
                (1 + i*2, 3 + i*2),
                (3 + i*2, 0 + i*2),
                (0 + i*2, 2 + i*2),
                (2 + i*2, 3 + i*2)
            ]
        edges.extend(edgesFront)
        i += 1

    while fieldNumber/2 - 1 < i < fieldNumber :
        if strebenParallel == "Fallende Diagonalen":
            edgesBack = [
                (0 + i*2, 1 + i*2),
                (1 + i*2, 3 + i*2),
                (3 + i*2, 0 + i*2),
                (0 + i*2, 2 + i*2),
                (2 + i*2, 3 + i*2)
            ]
        else:
            edgesBack = [
                (1 + i*2, 0 + i*2),
                (0 + i*2, 2 + i*2),
                (2 + i*2, 1 + i*2),
                (1 + i*2, 3 + i*2),
                (3 + i*2, 2 + i*2)
            ]

        edges.extend(edgesBack)
        i += 1

    for edge in edges:
        #st.text(f"Current Edge: {edge}")
        start_node = nodeArray[edge[0]]
        #st.text(f"Start Node: {edge}")
        end_node = nodeArray[edge[1]]
        #st.text(f"End Node: {edge}")
        ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)

    nodeCorner = [
        (nodeArray[0][0], nodeArray[0][1]),
        (nodeArray[-2][0], nodeArray[-2][1])
    ]

    for node in nodeArray:
        ax.plot(node[0], node[1], 'ko', markersize=5)
    for node in nodeCorner:
        ax.plot(node[0], node[1], "k^", markersize=10)

    draw_mass_band(minNodeX, minNodeY, ax)
    draw_q_over_truss(minNodeX, minNodeY, ax)
    set_ax_settings(minNodeX, minNodeY, ax)
    st.pyplot(fig, use_container_width=True)

    if debug == True:
        st.text(nodeArray)
        st.text(len(nodeArray))

def draw_truss_strebe():
    # Define truss nodes
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNode = minNodeY + trussHeight
    nrNodeLower = int(fieldNumber) 
    nrNodeUpper = int(fieldNumber) + 1

    nodeArray = []

    nodeLower = []
    nodeUpper = []




    #nodes = np.array([
        #[100, 100],  # Node 0
        #[200, 100],  # Node 1
        #[300, 100],  # Node 2
        #[150, 50],   # Node 3
        #[250, 50],   # Node 4
    #])


    # Create a figure
    fig, ax = plt.subplots()    

    nodeL = 0
    while nodeL < nrNodeLower:
        nodeLower.append((float((minNodeX + (distanceNode / 2)) + nodeL * distanceNode), minNodeY)) #create coordinates for all the Lower nodes
        nodeL += 1

    nodeU = 0
    while nodeU < nrNodeUpper:
        nodeUpper.append((float(minNodeX + nodeU * distanceNode), maxNode)) #create coordinates for all the Upper nodes
        nodeU += 1

    #nodeLower = np.array(nodeLower) #make numPy array (no idea why)
    #nodeUpper = np.array(nodeUpper)

    nodeArray = [item for pair in zip(nodeUpper, nodeLower) for item in pair] #sort all Node coordinates in opposing order
    if len(nodeLower) < len(nodeUpper): #add the last missing Node from the longer array
        nodeArray.extend(nodeUpper[len(nodeLower):])
    
    #nodeArray = np.array(nodeArray)

    # Define truss connections (edges)
    #edges = [
        #(0, 1),  # Edge connecting Node 0 to Node 1
        #(1, 2),  # Edge connecting Node 1 to Node 2
        #(0, 3),  # Edge connecting Node 0 to Node 3
        #(1, 4),  # Edge connecting Node 1 to Node 4
        #(2, 4),  # Edge connecting Node 2 to Node 4
        #(3, 4),  # Edge connecting Node 3 to Node 4
    #]

    edges = [
        (1, 0),
        (0, 2),
        (2, 1)
    ]

    i = 0

    while i < fieldNumber - 1: #extend the points that are used with every new field in the truss
        edgeExtend = [
            (1 + 2 * i, 3 + 2 * i),
            (3 + 2 * i, 4 + 2 * i),
            (4 + 2 * i, 2 + 2 * i),
            (2 + 2 * i, 3 + 2 * i)
        ]
        #st.text(edges)
        edges.extend(edgeExtend)
        i += 1


    # Draw edges in red
    for edge in edges:
        #st.text(f"Current Edge: {edge}")
        start_node = nodeArray[edge[0]]
        #st.text(f"Start Node: {edge}")
        end_node = nodeArray[edge[1]]
        #st.text(f"End Node: {edge}")
        ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)

    nodeCorner = [
        (nodeUpper[0][0], nodeUpper[0][1] - trussHeight),
        (nodeUpper[-1][0], nodeUpper[-1][1] - trussHeight)
    ]

    ax.plot([nodeArray[0][0], nodeCorner[0][0]], [nodeArray[0][1], nodeCorner[0][1]], "r-", linewidth=2)
    ax.plot([nodeCorner[1][0], nodeCorner[0][0]], [nodeCorner[1][1], nodeCorner[0][1]], "r-", linewidth=2)
    ax.plot([nodeArray[-1][0], nodeCorner[1][0]], [nodeArray[-1][1], nodeCorner[1][1]], "r-", linewidth=2)

    # Draw nodes in black
    for node in nodeLower:
        ax.plot(node[0], node[1], 'ko', markersize=5)

    for node in nodeUpper:
        ax.plot(node[0], node[1], "ko", markersize=5)

    for node in nodeCorner:
        ax.plot(node[0], node[1], "k^", markersize=10)


    # Calculate and display truss width and height
    #truss_width = np.max(nodes[:, 0]) - np.min(nodes[:, 0])
    #truss_height = np.max(nodes[:, 1]) - np.min(nodes[:, 1])

    # create Massband Gesamtlaenge
    draw_mass_band(minNodeX, minNodeY, ax)
    
    # Draw LEF Force above Truss
    draw_q_over_truss(minNodeX, minNodeY, ax)

    set_ax_settings(minNodeX, minNodeY, ax)
    # Set plot limits

    # Show the plot
    st.pyplot(fig, use_container_width=True)

    # debug to check node generation
    
    if debug == True:

        st.text(f"Lower Nodes: {nodeLower}")
        st.text(f"Upper Nodes: {nodeUpper}")
        st.text(f"Corner Nodes: {nodeCorner}")
        st.text(f"Combined Nodes: {nodeArray}")

def lasten_stack(nodes, last, debugOutput=False):

    global start_height_stack
    start_height_stack = 0.5

    if "stackStartHeight" not in st.session_state:
        st.session_state.stackStartHeight = start_height_stack

    if trussDistance <= 5:
        totalHeight = trussDistance * 0.6
    if trussDistance > 5:
        totalHeight = trussDistance * 0.6
    lastHeight = (last / qTotal) * totalHeight

    nodesStack = [
        [nodes[0][0], nodes[0][1] + st.session_state.stackStartHeight],
        [nodes[1][0], nodes[1][1] + st.session_state.stackStartHeight],
        [nodes[1][0], nodes[1][1] + st.session_state.stackStartHeight + lastHeight],
        [nodes[0][0], nodes[0][1] + st.session_state.stackStartHeight + lastHeight]
    ]

    if debugOutput == True:
        if debug == True:
            st.text(f"fängt an bei: {st.session_state.stackStartHeight:.2f}, mit Höhe {lastHeight:.2f} weiter")
            st.text(qTotal)
            #st.text(f"{roofAdded}")
            #for last in roofAdded:
                #st.text(f"{st.session_state.roofAdditives[last]} kN")

    st.session_state.stackStartHeight += lastHeight

    return nodesStack

def draw_LEF():

    minNodeLEF = trussDistance / 5
    minNodeLEFy = 2
    global start_height_stack

    edgesLEF = [
        (0, 1),
        (1, 2),
        (2, 3),
        (4, 5)
    ]

    nodesLEF = [
        [minNodeLEF, minNodeLEFy + 2.2],
        [minNodeLEF, minNodeLEFy + 4.5],
        [minNodeLEF + 2.75, minNodeLEFy + 3],
        [minNodeLEF + 2.75, minNodeLEFy + 0.3],
        [minNodeLEF, minNodeLEFy + 4.1],
        [minNodeLEF + 2.75, minNodeLEFy + 2.6]
    ]

    nodesForceField = [
        [
            [nodesLEF[1][0], nodesLEF[1][1] + 0],
            [nodesLEF[1][0] + trussDistance, nodesLEF[1][1] + 0],
            [nodesLEF[2][0] + trussDistance, nodesLEF[2][1] + 0],
            [nodesLEF[2][0], nodesLEF[2][1] + 0]
        ],
        [
            [nodesLEF[1][0] + trussDistance / 2, nodesLEF[1][1] + 0],
            [nodesLEF[1][0] + trussDistance + trussDistance / 2, nodesLEF[1][1] + 0],
            [nodesLEF[2][0] + trussDistance + trussDistance / 2, nodesLEF[2][1] + 0],
            [nodesLEF[2][0] + trussDistance / 2, nodesLEF[2][1] + 0]
        ],
        [
            [nodesLEF[1][0] + trussDistance, nodesLEF[1][1] + 0],
            [nodesLEF[1][0] + 2 * trussDistance, nodesLEF[1][1] + 0],
            [nodesLEF[2][0] + 2 * trussDistance, nodesLEF[2][1] + 0],
            [nodesLEF[2][0] + trussDistance, nodesLEF[2][1] + 0]
        ]        
    ]
    
    LEF_graph0 = plt.Polygon(nodesForceField[0], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.3)
    LEF_graph1 = plt.Polygon(nodesForceField[1], closed = True, edgecolor="lightblue", facecolor="lightblue", alpha=0.5)
    LEF_graph2 = plt.Polygon(nodesForceField[2], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.3)



    #st.write(LEF_graph)
    #st.write(nodesForceField[0])
    #LEF_graph = plt.Polygon(nodesForceField, closed = True, edgecolor=None, facecolor="lightblue", alpha=0.5)

        # Create a figure
    fig, ax = plt.subplots()

    #with col1:
        #lasten_stack(nodesForceField[1], 1, "test", ax)

    truss = 0
    while truss < 3:
        edgeNr = 0
        for edge in edgesLEF:
            #st.text(f"Current Edge: {edge}")
            start_node = [nodesLEF[edge[0]][0] + truss * trussDistance, nodesLEF[edge[0]][1]]
            #st.text(f"Start Node: {edge}")
            end_node = [nodesLEF[edge[1]][0] + truss * trussDistance, nodesLEF[edge[1]][1]]
            #st.text(f"End Node: {edge}")

            # Oberste Linie dicker zeichnen um Träger zu visualisieren
            if edgeNr in [1, 3]:
                ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)
            else:
                ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)
            edgeNr += 1

        nodeNr = 0
        for node in nodesLEF:
            if nodeNr not in [1, 2]:    # dont draw the upper 2 nodes
                ax.plot(node[0] + truss * trussDistance, node[1], 'ko', markersize=5)
            nodeNr += 1
        truss += 1


    colorTurn = 0


    if "completeRoofAdditives" not in st.session_state:
        st.session_state.completeRoofAdditives = {}

    st.session_state.completeRoofAdditives = copy.deepcopy(st.session_state.roofAdditives) # initialisiere completeRoofAdditives mit roodAdditive werten, ohne selben Memory platz zu teilen

    completeRoofStack = roofAdded
    
    st.session_state.completeRoofAdditives["Dachlast"] = roofLayerSum
    st.session_state.completeRoofAdditives["Windlast"] = round(windForce, 2)
    st.session_state.completeRoofAdditives["Schneelast"] = round(snowForce, 2)

    # Schnee und Windlast zum bestehenden RoofStack hinzufügen
    completeRoofStack.extend(["Schneelast", "Windlast"])
    # Dachlast auf Index 0 zum bestehenden RoofStack hinzufügen
    completeRoofStack.insert(0, "Dachlast")

    if debug == True:
        st.text(f"roofAdded {roofAdded}")
        st.text(f"completeRoofStack {completeRoofStack}")
        st.text(f"st.session_state.completeRoofAdditives {st.session_state.completeRoofAdditives}")
        st.text(f"st.session_state.roofAdditives {st.session_state.roofAdditives}")
        st.text(completeRoofStack)

    #stackPatches = []
        
    if lastAnzeige == "Erweitert":

        for name in completeRoofStack:
            if debug == True:
                st.text(name)

            turn = 0
            annotateNodes = []

            for nodes in lasten_stack(nodesForceField[1], st.session_state.completeRoofAdditives[name], debugOutput=True):
                #if debug == True:
                    #st.text(name)
                    #st.text(f"{nodes[0]} und {nodes[1]}")
                #ax.plot(*nodes, "ko", markersize=2)
                #if 2 <= turn < 4:
                annotateNodes.append(nodes)
                turn += 1

            #nodesStack = lasten_stack(nodesForceField[1], st.session_state.roofAdditives[name], name, ax)
            if debug == True:
                st.text(f"{annotateNodes}")
                st.text(f"{annotateNodes[0][0]}, {annotateNodes[2][1]}")
            
            # text um halbe höhe runterschieben
            halfHeight = (annotateNodes[2][1] - annotateNodes[1][1]) / 2 # höhere Y-Koordinate minus untere Y-Koordinate, geteilt durch 2

            ax.annotate(f"- {name}", (annotateNodes[1][0], annotateNodes[2][1] - halfHeight), xytext=(10, 0), textcoords='offset points', va='center', fontsize=8, annotation_clip=False)
            ax.annotate(f"{st.session_state.completeRoofAdditives[name]}kN/m²", (annotateNodes[1][0] - (trussDistance / 2), annotateNodes[2][1] - halfHeight), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False, color="black")

            stackPatch = plt.Polygon(annotateNodes, facecolor=st.session_state.roofColors[name], closed = True, edgecolor=st.session_state.roofColors[name], alpha=0.15, zorder=2 )
            ax.add_patch(stackPatch)

            colorTurn += 1

        ax.annotate(f"q = {qTotal:.2f}kN/m²", (minNodeLEF + trussDistance ,start_height_stack + minNodeLEFy + 4.5 + (st.session_state.stackStartHeight / 2)), xytext=(-100, -5), textcoords='offset points', ha="center", va='center', fontsize=8, annotation_clip=False)
        
        if "stackStartHeight" in st.session_state:
            del st.session_state["stackStartHeight"]

        

    measure = 0
    while measure < 3:
        ax.plot((minNodeLEF + 3) + measure * trussDistance, minNodeLEFy / 2, "k+", markersize=10)
        if measure < 2:
            ax.plot([(minNodeLEF + 3) + measure * trussDistance, (minNodeLEF + 3) + (measure + 1) * trussDistance],[minNodeLEFy / 2, minNodeLEFy / 2], "k-", linewidth=1)
            ax.annotate(f"{float(trussDistance):.2f}m", ((minNodeLEF + 3) + trussDistance / 2 + measure * trussDistance, minNodeLEFy / 3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)
        measure += 1

    # Set plot limits
    ax.set_xlim([0, 2 * trussDistance + 2 * minNodeLEF + 3])
    ax.set_ylim([0, 2 * 4 + 2 * minNodeLEF])

    # Add LEF on top
    ax.add_patch(LEF_graph0)
    ax.add_patch(LEF_graph1)
    ax.add_patch(LEF_graph2)

    #for patch in stackPatches:
        #ax.add_patch(patch)

    # nicht mehr genutzte Anzeige für Last
    if lastAnzeige == "Einfach":
        ax.annotate(f"q = g + w + s\nq = {float(roofForce):.2f} kN/m² + {float(windForce):.2f} kN/m² + {float(snowForce):.2f} kN/m²\n\nq = {float(qTotal):.2f} kN/m²", ((2 * trussDistance + 2 * minNodeLEF + 3)/2, 2 * 4 + 2 * minNodeLEF- minNodeLEF), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)


    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_aspect('equal', adjustable='datalim')

    # Show the plot
    st.pyplot(fig, use_container_width=True)

    if debug == True:
        st.text(f"zusätzliche Lasten: {roofAdded}")
        st.text(f"Lasten: {st.session_state.roofAdditives}")

def analyze_struts(strutObergurt, strutDiagonal, strutUntergurt, strutElse, strutToCheck):    #Analysiere jedes Teil einzeln
    
    if strutToCheck == "Obergurt":
        nr, length, material, profile, chosenProfile = strutObergurt
            
        materialVolume = (materialSelect[material][profile][chosenProfile][0] * length * nr)/1000
        struts_all_combined[strutToCheck] = {
            "Anzahl" : nr,
            "Länge" : length,
            "Material" : f"{material}",
            "Profil" : f"{chosenProfile} {profile}",
            "Volumen" : materialVolume,
            "Gewicht" : materialVolume * materialDensity[material]
        }

    if strutToCheck == "Streben":
        nr, length, material, profile, chosenProfile = strutDiagonal
            
        materialVolume = (materialSelect[material][profile][chosenProfile][0] * length * nr)/1000
        struts_all_combined[strutToCheck] = {
            "Anzahl" : nr,
            "Länge" : length,
            "Material" : f"{material}",
            "Profil" : f"{chosenProfile} {profile}",
            "Volumen" : materialVolume,
            "Gewicht" : materialVolume * materialDensity[material]
        }

    if strutToCheck == "Untergurt":
        nr, length, material, profile, chosenProfile = strutUntergurt
            
        materialVolume = (materialSelect[material][profile][chosenProfile][0] * length * nr)/1000
        struts_all_combined[strutToCheck] = {
            "Anzahl" : nr,
            "Länge" : length,
            "Material" : f"{material}",
            "Profil" : f"{chosenProfile} {profile}",
            "Volumen" : materialVolume,
            "Gewicht" : materialVolume * materialDensity[material]
        }

    #if strutToCheck not in ["Obergurt", "Streben", "Untergurt"]:
    if strutToCheck == "Untergurt":
        counter = 1
        for strut in strutElse:            
            nr, length, material, profile, chosenProfile = strut             
            strutName = f"Weitere Stäbe {counter}"
            materialVolume = (materialSelect[material][profile][chosenProfile][0] * length * nr)/1000
            struts_all_combined[strutName] = {
                "Anzahl" : nr,
                "Länge" : length,
                "Material" : None,
                "Profil" : f"undefiniert",
                "Volumen" : 0,
                "Gewicht" : 0
            }
            counter += 1
        
def number_of_nodes(trussType):
    if trussType == "Strebenfachwerk":
        nodesNr = (fieldNumber * 2) + 3
    if trussType == "Parallelträger":
        nodesNr = (fieldNumber + 1) * 2
    return nodesNr

def analyze_truss(strutToCheck, material, profile, chosenProfile):   #Analysiere das Gesamte Tragwerk mit allen Einzelteilen
    #Berechnung für Strebenfachwerk
    
    if trussType == "Strebenfachwerk":
        diagonalLength = math.sqrt((pow(distanceNode/2, 2)) + (pow(trussHeight, 2)))
        
        strutDiagonal = [(fieldNumber*2), diagonalLength, material, profile, chosenProfile]   # [Anzahl, Länge der Stäbe, material, profile, chosenProfile]
        strutObergurt = [fieldNumber, distanceNode, material, profile, chosenProfile]
        strutUntergurt = [fieldNumber - 1, distanceNode, material, profile, chosenProfile]
        strutElse = [[2, trussHeight, material, profile, chosenProfile], [2, (distanceNode/2), material, profile, chosenProfile]]
        analyze_struts(strutObergurt, strutDiagonal, strutUntergurt, strutElse, strutToCheck)
        return
    
    #Berechnung für Parallelträger
    if trussType == "Parallelträger":
        diagonalLength = math.sqrt((pow(distanceNode, 2)) + (pow(trussHeight, 2)))

        strutObergurt = strutUntergurt = [fieldNumber, distanceNode, material, profile, chosenProfile]    # [Anzahl, Länge der Stäbe, material, profile, chosenProfile]
        strutDiagonal = [fieldNumber, diagonalLength, material, profile, chosenProfile]
        strutElse = [[fieldNumber + 1, trussHeight, material, profile, chosenProfile]]
        analyze_struts(strutObergurt, strutDiagonal, strutUntergurt, strutElse, strutToCheck)
        return
    
    else:
        return False

def calc_strebewerk(strutToCheck, print_forces=False):

    #qTotal = 2.4

    diagonalLength = math.sqrt((pow(distanceNode/2, 2)) + (pow(trussHeight, 2)))
    diagonalAlpha = math.asin(trussHeight/diagonalLength)
    qProd = 0 # summe aller Momente durch Q
    qSum = 0 # summe aller Q Punktlasten
    qNum = []
    qCount = 1
    forceAuflager = (qTotal*trussDistance*trussWidth)/2
    totalLast = qTotal*trussDistance*trussWidth
    punktLastAussen = totalLast/(fieldNumber * 2)

    if math.ceil(fieldNumber/2) == 1:
        qTemp = (float((qTotal*trussDistance*trussWidth)/fieldNumber), float(qCount * (trussWidth/fieldNumber)))  # store Q Value and Q distance in array just for debugging purposes
        qNum.append(qTemp)
    else:
        while qCount < math.ceil(fieldNumber/2):    # draw forces exactly until the middle strut
            qTemp = (float((qTotal*trussDistance*trussWidth)/fieldNumber), float(qCount * (trussWidth/fieldNumber)))  # store Q Value and Q distance in array just for debugging purposes
            qNum.append(qTemp)
            qCount += 1
        if fieldNumber % 2 == 0:
            qNum.append(((qTotal*trussDistance*trussWidth)/fieldNumber, 0))

    # add all different qMomentums together
    for num in qNum:
        qProd += num[0] * num[1]
        qSum += num[0]

    # calculate U force 
    maxForceU = ((punktLastAussen * math.ceil(fieldNumber/2) * trussWidth/fieldNumber * -1) - qProd + ((forceAuflager) * math.ceil(fieldNumber/2) * trussWidth/fieldNumber)) / trussHeight
    ForceDmiddle = ((punktLastAussen + qSum - (totalLast/2)) / math.sin(diagonalAlpha))
    maxForceO = (-maxForceU - (math.cos(diagonalAlpha)*ForceDmiddle))

    ForceOaussen = ((punktLastAussen * (trussWidth/(fieldNumber*2))) - (forceAuflager * (trussWidth/(fieldNumber*2)))) / trussHeight
    maxForceD = (forceAuflager - punktLastAussen) / math.sin(diagonalAlpha)

    global maxForce

    if strutToCheck == "Obergurt":
        maxForce = maxForceO
    if strutToCheck == "Streben":
        maxForce = maxForceD
    if strutToCheck == "Untergurt":
        maxForce = maxForceU

    if print_forces != False:
        with col6_1:
            st.write(f"Maximale Druckkraft im Obergurt:" if maxForceO < 0 else f"Maximale Zugkraft im Obergurt:")
            st.write(f":blue[{abs(maxForceO):.2f} kN]" if maxForceO < 0 else f":red[{abs(maxForceO):.2f} kN]")
        with col6_2:
            st.write(f"Maximale Druckkraft in äußerster Strebe:" if maxForceD < 0 else f"Maximale Zugkraft in äußerster Strebe:")
            st.write(f":blue[{abs(maxForceD):.2f} kN]" if maxForceD < 0 else f":red[{abs(maxForceD):.2f} kN]")
        with col6_3:
            st.write(f"Maximale Druckkraft im Untergurt:" if maxForceU < 0 else f"Maximale Zugkraft im Untergurt:")
            st.write(f":blue[{abs(maxForceU):.2f} kN]" if maxForceU < 0 else f":red[{abs(maxForceU):.2f} kN]")
    


    if debug == True:
            st.subheader("debug:")
            st.text(f"Diagonalstab Länge: {diagonalLength}m")
            st.text(f"Punktlast aussen: {punktLastAussen}")
            st.text(f"alpha: {math.degrees(diagonalAlpha)}")
            st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
            st.text(f"Qs generiert: {len(qNum)}\nmit Werten: {qNum}\ninsgesamt Momente: {float(qProd):.2f}")
            st.text(f"Kraft im äußeren Obergurt: {ForceOaussen} kN")

    return maxForce

def calc_parallel(strebenParallel, strutToCheck, print_forces=False):
    
    #qTotal = 2.4
    #st.text(qTotal)

    diagonalLength = math.sqrt((pow(distanceNode, 2)) + (pow(trussHeight, 2)))
    diagonalAlpha = math.asin(trussHeight/diagonalLength)
    forceAuflager = (qTotal*trussDistance*trussWidth)/2
    totalLast = qTotal*trussDistance*trussWidth
    punktLastAussen = totalLast/(fieldNumber * 2)
    qProd = 0 # summe aller Momente durch Q
    qSum = 0 # summe aller Q Punktlasten
    qNum = []
    
    i = 1
    while i < (fieldNumber / 2):
        qTemp = (totalLast / fieldNumber, i * distanceNode) # Punktlast Wert, Distanz zu Drehpunkt
        qNum.append(qTemp)
        i += 1
    qNum.append((punktLastAussen, i * distanceNode))
    qNum.append((-forceAuflager, i * distanceNode))
    #st.text(len(qNum))

    for num in qNum:
        qSum += num[0]
        qProd += (num[0] * num[1])
        #st.text(f"{qSum} und {qProd}")

    if strebenParallel == "Fallende Diagonalen":
        ForceDmiddle = (-qSum)/math.sin(diagonalAlpha)
    else:
        ForceDmiddle = (qSum)/math.sin(diagonalAlpha)

    maxForceO = (qProd)/trussHeight
    maxForceU = -maxForceO - (ForceDmiddle*math.cos(diagonalAlpha))

    ForceOaussen = (punktLastAussen * distanceNode) - (forceAuflager * distanceNode)
    maxForceD = (-punktLastAussen + forceAuflager) / math.sin(diagonalAlpha)
    if strebenParallel != "Fallende Diagonalen":
        maxForceD = -maxForceD    


    if strutToCheck == "Obergurt":
        maxForce = maxForceO
    if strutToCheck == "Streben":
        maxForce = maxForceD
    if strutToCheck == "Untergurt":
        maxForce = maxForceU

    if print_forces != False:
        with col6_1:
            st.write(f"Maximale Druckkraft im Obergurt:" if maxForceO < 0 else f"Maximale Zugkraft im Obergurt:")
            st.write(f":blue[{abs(maxForceO):.2f} kN]" if maxForceO < 0 else f":red[{abs(maxForceO):.2f} kN]")
        with col6_2:
            st.write(f"Maximale Druckkraft in äußerster Strebe:" if maxForceD < 0 else f"Maximale Zugkraft in äußerster Strebe:")
            st.write(f":blue[{abs(maxForceD):.2f} kN]" if maxForceD < 0 else f":red[{abs(maxForceD):.2f} kN]")
        with col6_3:
            st.write(f"Maximale Druckkraft im Untergurt:" if maxForceU < 0 else f"Maximale Zugkraft im Untergurt:")
            st.write(f":blue[{abs(maxForceU):.2f} kN]" if maxForceU < 0 else f":red[{abs(maxForceU):.2f} kN]")

    if debug == True:
            st.subheader("debug:")
            st.text(f"Diagonalstab Länge: {diagonalLength}m")
            st.text(f"Punktlast aussen: {punktLastAussen}")
            st.text(f"total Last: {totalLast}")
            st.text(f"alpha: {math.degrees(diagonalAlpha)}")
            st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
            st.text(f"Qs generiert: {len(qNum)}\nmit Werten: {qNum}\ninsgesamt Momente: {float(qProd):.2f}")
            st.text(f"Kraft im äußeren Obergurt: {ForceOaussen} kN")
    
    return maxForce


def calc(trussType, strutToCheck, print_forces=False):
    if trussType == "Strebenfachwerk":
        maxForce = calc_strebewerk(strutToCheck, print_forces)
    if trussType == "Parallelträger":
        maxForce = calc_parallel(strebenParallel, strutToCheck, print_forces)
    return maxForce

def extract_numerical_part(key):
    # This function extracts the numerical part from a string key
    # Example: "8" -> 8, "12/12" -> 12
    return int(key.split('/')[0]) if '/' in key else int(key)

def stress_verification(material, profile, maxForce, stress_latex): # Spannungsnachweis zur Wahl des ersten Querschnitts
    
    #st.text(maxForce)

    maxForce_d = abs(maxForce) * 1.4
    
    if maxForce < 0:
        sigma_rd = sigmas[material][0]
    else:
        sigma_rd = sigmas[material][1]

    areaCalc = maxForce_d/sigma_rd

    

    
    if debug == True:
        st.text(f"benötigte Oberfläche: {areaCalc:.2f}cm²")
    
    for profil, values in materialSelect[material][profile].items():
        area = values[0]
        if area > areaCalc:
            chosenProfile = profil

            if maxForce > 0:
                st.session_state.finalArea = area


            with stress_latex:
                A_min = r"A_{min}"
                math_expression = r"A_{min} = \frac{{Nd}}{{\sigma_{Rd}}}"
                math_expression2 = f"{A_min} = {areaCalc:.2f} cm²"
                st.latex(math_expression)
                st.latex(math_expression2)
            
            if debug == True:

                st.text(f"Profil: {chosenProfile}")
                st.text(f"Profil Oberfläche: {materialSelect[material][profile][chosenProfile][0]}cm²")
            return chosenProfile, sigma_rd, areaCalc
    else:
        st.markdown(f'<font color="red">Es gibt keinen passenden {profile} Querschnitt, der den Spannungstest besteht.</font>', unsafe_allow_html=True)
        return False
    
def check_bend(material, min_i, A, maxForce, sigma_rd):

    lambdaCalc = (trussWidth/fieldNumber)*100/min_i

    for lmbda, k in lambda_values[material].items():
        if lmbda > lambdaCalc:

            check = sigma_rd * k
        
            if check > (-maxForce*1.4)/A:  # sigma*k > Nd/A
                math_expression = r"\sigma_{Rd} \cdot k > \frac{{Nd}}{{A}}"
                math_expression2 = f"{check:.2f} > {((-maxForce*1.4)/A):.2f}"

                with st.expander("Knicknachweis"):
                    
                    
                    st.text(f"A = {A} cm²")
                    st.text(f"k = {k}\nbei λ = {int(lambdaCalc)}")
                    

                    # Display the mathematical expression using st.latex
                    st.latex(math_expression)
                    st.latex(math_expression2)
                
                if debug == True:
                    st.text(f"Lambda: {lambdaCalc}")
                    st.text(f"k = {k}")
                    

                    # Display the mathematical expression using st.latex
                    st.latex(math_expression)
                    st.latex(math_expression2)
                
                return True

            else:
                return False

def profile_success(material, profile, chosenProfile, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck):

    #Hinzufügen zu strutArray, um daraus Bauteilliste zu gestalten
    #strutArray.append([])


    with stress_latex:
        A_gew = r"A_{gew}"
        math_expression = f"{A_gew}({chosenProfile}) = {materialSelect[material][profile][chosenProfile][0]:.2f} cm²"
        st.latex(math_expression)
    with stress_einheiten:
        A_min = r"A_{min}"
        st.text(f"σ = {sigma_rd} kN/cm²\nη = {((((abs(maxForce)*1.4)/materialSelect[material][profile][chosenProfile][0]) / sigma_rd) * 100):.2f} %")
        st.text(f"Nd = Nmax * 1.4 \nNd = {(abs(maxForce)*1.4):.2f} kN")

    st.title(f'{chosenProfile} {profile}')                
    st.markdown(f'<span style="color: green;">Der Querschnitt **{chosenProfile}** in **{material} {profile}** erfüllt die erforderlichen Nachweise!</font>', unsafe_allow_html=True)
        
    searchTerm = f"{chosenProfile} {profile} Profil Maße Tabelle" # Erstelle Suchquery für Querschnitt
    searchTerm_noSpaces = searchTerm.replace(" ", "+")  # Ersetze Leerzeichen durch "+"
    st.link_button(f"Kennwerte zu {chosenProfile} {profile}", url=f"https://www.google.com/search?q={searchTerm_noSpaces}", use_container_width=True)

    analyze_truss(strutToCheck, material, profile, chosenProfile)

def bend_verification(material, profile, chosenProfile, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck):
    # iterativer Knicknachweis
    if maxForce < 0:    # wenn Druckkraft vorliegt, dann Knicknachweis führen
        for profil, values in materialSelect[material][profile].items():
            if extract_numerical_part(profil) >= extract_numerical_part(chosenProfile):
                stressProfile = chosenProfile
                if debug == True:
                    st.text(f"Teste Profil: {profil}")
                min_i = values[1]
                A = values[0]
                if check_bend(material, min_i, A, maxForce, sigma_rd) == True:
                    profile_success(material, profile, profil, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck)

                    return chosenProfile
            #else:
                #st.text(f"{profil} ist nicht größer als {chosenProfile}")
        else:
            st.markdown(f'<font color="red">Es gibt keinen passenden {profile} Querschnitt, der den Knicktest besteht.</font>', unsafe_allow_html=True)
            #st.markdown(":red[Es gibt keinen passenden Querschnitt für]")

    else:   # wenn keine Druckkraft vorliegt (=Zugkraft) dann ergibt der Spannungsnachweis den Querschnitt
        with st.expander("Knicknachweis"):
            st.markdown(f":green[Bei Zugkräften ist kein Knicknachweis nötig!]")
        profile_success(material, profile, chosenProfile, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck)


def create_bauteilliste():
    
    bauteil_col_1, bauteil_col_2 = st.columns([0.7, 0.3], gap="medium")

    with bauteil_col_1:
        flat_data = [{"Position": element, **attributes} for element, attributes in struts_all_combined.items()]
        df = pd.DataFrame(flat_data)
        st.dataframe(df, column_order=("Position", "Anzahl", "Länge", "Profil", "Volumen"), use_container_width=True, hide_index=True, column_config={
            "Anzahl": st.column_config.NumberColumn(
                format="x %d"
            ),
            "Länge": st.column_config.NumberColumn(
                format="%.2f m"
            ),
            "Volumen": st.column_config.NumberColumn(
                format="%.2f m³"
            )
        })

    with bauteil_col_2:
        total_volumes = df.groupby("Material")["Volumen"].sum()
        total_weight = df.groupby("Material")["Gewicht"].sum()

        combined_df = pd.concat([total_volumes, total_weight], axis=1)

        st.dataframe(combined_df, use_container_width=True, column_config={
            "Volumen" : st.column_config.NumberColumn(
                format="%.2f m³"
            ),
            "Gewicht" : st.column_config.NumberColumn(
                format="%.2f kg"
            )
        })
        st.markdown(f"Gesamtgewicht: **{((df['Gewicht'].sum())/1000):.2f} t**.")

    nodesNr = number_of_nodes(trussType)
    st.markdown(f"Es werden **{nodesNr} Knoten** konstruiert.")


                    

def draw_truss2():
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNode = minNodeY + trussHeight
    distanceNode = trussWidth / fieldNumber

    nodeLower = [(float((minNodeX + (distanceNode / 2)) + i * distanceNode), minNodeY) for i in range(int(fieldNumber))]
    nodeUpper = [(float(minNodeX + i * distanceNode), maxNode) for i in range(int(fieldNumber + 1))]

    nodeArray = [item for pair in zip(nodeUpper, nodeLower) for item in pair]
    if len(nodeLower) < len(nodeUpper):
        nodeArray.extend(nodeUpper[len(nodeLower):])

    edges = [(1, 0), (0, 2), (2, 1)]

    for i in range(0, int(fieldNumber-1)):
        edges.extend([(1 + 2 * i, 3 + 2 * i), (3 + 2 * i, 4 + 2 * i), (4 + 2 * i, 2 + 2 * i), (2 + 2 * i, 3 + 2 * i)])

    # Create a figure
    fig, ax = plt.subplots()

    # Check if edges and nodeArray are not empty
    if edges and nodeArray:
        # Draw edges as LineCollection
        edge_collection = LineCollection([(nodeArray[edge[0]], nodeArray[edge[1]]) for edge in edges], color='red', linewidth=2, zorder=2)
        ax.add_collection(edge_collection)




    # Draw nodes
    # ax.scatter erwartet x_values und y_values als seperate arguments. zip(*nodeLower) sortiert alle tuple in x und y
    # *zip(*nodeLower) löst dann x und y jeweils als einzelne tupel aus.
    ax.scatter(*zip(*nodeLower), color='black', s=20, zorder=3)
    ax.scatter(*zip(*nodeUpper), color='black', s=20, zorder=3) # zorder gibt die Reihenfolge an in der die Objekte gezeichnet werden

    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Set plot limits
    ax.set_xlim([0, trussWidth + 2 * minNodeX])
    ax.set_ylim([0, trussHeight + 2 * minNodeY])

    ax.set_aspect(2, adjustable='datalim')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Show the plot
    st.pyplot(fig, use_container_width=True)
def draw_truss3():
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNode = minNodeY + trussHeight
    distanceNode = trussWidth / fieldNumber

    nodeLower = [(float((minNodeX + (distanceNode / 2)) + i * distanceNode), minNodeY) for i in range(int(fieldNumber))]
    nodeUpper = [(float(minNodeX + i * distanceNode), maxNode) for i in range(int(fieldNumber + 1))]

    nodeArray = [item for pair in zip(nodeUpper, nodeLower) for item in pair]
    if len(nodeLower) < len(nodeUpper):
        nodeArray.extend(nodeUpper[len(nodeLower):])

    edges = [(1, 0), (0, 2), (2, 1)]

    for i in range(0, int(fieldNumber -1)):
        edges.extend([(1 + 2 * i, 3 + 2 * i), (3 + 2 * i, 4 + 2 * i), (4 + 2 * i, 2 + 2 * i), (2 + 2 * i, 3 + 2 * i)])

    # Create a figure
    fig, ax = plt.subplots()

    nodeCorner = [
        (nodeUpper[0][0], nodeUpper[0][1] - trussHeight),
        (nodeUpper[-1][0], nodeUpper[-1][1] - trussHeight)
    ]
    
    ax.plot([nodeArray[0][0], nodeCorner[0][0]], [nodeArray[0][1], nodeCorner[0][1]], "k-", linewidth=2)
    ax.plot([nodeCorner[1][0], nodeCorner[0][0]], [nodeCorner[1][1], nodeCorner[0][1]], "k-", linewidth=2)
    ax.plot([nodeArray[-1][0], nodeCorner[1][0]], [nodeArray[-1][1], nodeCorner[1][1]], "k-", linewidth=2)

    # Check if edges and nodeArray are not empty
    if edges and nodeArray:
        # Draw edges as LineCollection
        edge_collection = LineCollection([(nodeArray[edge[0]], nodeArray[edge[1]]) for edge in edges], color='black', linewidth=2, zorder=2)
        ax.add_collection(edge_collection)

    # Draw nodes in black
    for node in nodeCorner:
        ax.plot(node[0], node[1], "k^", markersize=10)

    for node in nodeLower:
        ax.plot(node[0], node[1], 'ko', markersize=5)

    for node in nodeUpper:
        ax.plot(node[0], node[1], "ko", markersize=5)

    # Draw nodes
    # ax.scatter erwartet x_values und y_values als seperate arguments. zip(*nodeLower) sortiert alle tuple in x und y
    # *zip(*nodeLower) löst dann x und y jeweils als einzelne tupel aus.
    #ax.scatter(*zip(*nodeLower), color='black', s=20, zorder=3)
    #ax.scatter(*zip(*nodeUpper), color='black', s=20, zorder=3) # zorder gibt die Reihenfolge an in der die Objekte gezeichnet werden

    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Set plot limits
    ax.set_xlim([0, trussWidth + 2 * minNodeX])
    ax.set_ylim([0, trussHeight + 2 * minNodeY])

    ax.set_aspect(1.5, adjustable='datalim')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Show the plot
    st.pyplot(fig, use_container_width=True)

    




def main():

    with col2:
        draw_LEF()
    # Draw the truss
    with col4:
        if trussType == "Strebenfachwerk":
            draw_truss_strebe()
        if trussType == "Parallelträger":
            draw_truss_parallel(strebenParallel)



    with obergurtColumn:
        strutToCheck = "Obergurt"
        #draw_truss3()
        # maxForce als maximale Last, die sich aus dem calc() ergibt
        OG_maxForce = calc(trussType, strutToCheck)
    with obergurtColumn:
        try:
            OG_chosenProfile, OG_sigma_rd, areaCalc = stress_verification(OG_material, OG_profile, OG_maxForce, OG_stress_latex)
            bend_verification(OG_material, OG_profile, OG_chosenProfile, OG_maxForce, OG_sigma_rd, OG_stress_latex, OG_stress_einheiten, strutToCheck)
        except TypeError as e:
            st.text("")
        #if stress_verification(OG_material, OG_profile, OG_maxForce) != False:
            #bend_verification()

    with strebenColumn:
        strutToCheck = "Streben"
        #draw_truss3()
        # maxForce als maximale Last, die sich aus dem calc() ergibt
        ST_maxForce = calc(trussType, strutToCheck)
    with strebenColumn:
        try:
            ST_chosenProfile, ST_sigma_rd, areaCalc = stress_verification(ST_material, ST_profile, ST_maxForce, ST_stress_latex)
            bend_verification(ST_material, ST_profile, ST_chosenProfile, ST_maxForce, ST_sigma_rd, ST_stress_latex, ST_stress_einheiten, strutToCheck)
        except TypeError as e:
            st.text("")

    with untergurtColumn:
        strutToCheck = "Untergurt"
        #draw_truss3()
        # maxForce als maximale Last, die sich aus dem calc() ergibt
        UG_maxForce = calc(trussType, strutToCheck, print_forces=True)
    with untergurtColumn:
        try:
            UG_chosenProfile, UG_sigma_rd, areaCalc = stress_verification(UG_material, UG_profile, UG_maxForce, UG_stress_latex)
            bend_verification(UG_material, UG_profile, UG_chosenProfile, UG_maxForce, UG_sigma_rd, UG_stress_latex, UG_stress_einheiten, strutToCheck)
        except TypeError as e:
            st.text("")


    with bauteilExpander:
        create_bauteilliste()

if __name__ == "__main__":
    main()
