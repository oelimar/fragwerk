import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import math
import json # für material import
import secrets # für random Hex Farbe
import copy # um st.session_state werte zu kopieren ohne diese weiter zu referenzieren
import requests # um material.json auf github abzufragen
from correct_input import correct_input

#Initiiere Seiten Konfiguration
st.set_page_config(
    page_title="fragwerk Fachwerkrechner",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/oelimar/images/main/fragwerk_icon.png",
    menu_items={
        "About" : f"# by ØLIMAR. \nhttps://soundcloud.com/oelimar"
    }
)

if "logo" not in st.session_state:
    st.session_state["logo"] = "https://raw.githubusercontent.com/oelimar/images/main/fragwerk.png"

col0_1, col0_2 = st.columns([0.6, 0.4], gap="large")
with col0_1:
    st.title("")
    #Fragwerk Logo
    st.image(st.session_state["logo"], width=350)
    st.title("dein Fachwerkrechner")
    st.title("")

#Toggle switch für Debuganzeige
with col0_2:
    debug = False
    #debug = st.toggle("Debug Mode")

#Initiiere Fachwerkarten
trussOptions = [
    "Strebenfachwerk",
    "Parallelträger"
]

#Initiiere Dachvoreinstellungen
roofOptions = [
    "Schwer",
    "Mittelschwer",
    "Leicht",
    "Eigener Aufbau"
]

#Schichten der verschiedenen Dächer
roofLayers = {
    "Schwer" : {
        1 : ("Kies 5cm", 1),
        2 : ("zweilagige Dachabdichtung", 0.04),
        3 : ("Dämmstoff 20cm", 0.2),
        4 : ("2 ⋅ KVH 10/20", 0.24),
        5 : ("Dampfsperre", 0.01),
        6 : ("Deckenbekleidung 2cm", 0.07)
    },
    "Mittelschwer" : {
        1 : ("zweilagige Dachabdichtung", 0.04),
        2 : ("Dämmstoff 16cm", 0.16),
        3 : ("2 ⋅ KVH 8/16", 0.24),
        4 : ("Dampfsperre", 0.01),
        5 : ("Deckenbekleidung 2cm", 0.07)
    },
    "Leicht" : {
        1 : ("zweilagige Dachabdichtung", 0.04),
        2 : ("Dämmstoff 5cm", 0.05),
        3 : ("Dampfsperre", 0.01),
        4 : ("Trapezblech", 0.125)
    },
    "Eigener Aufbau" : {
        1 : ("Schicht 1", 0.0),
        2 : ("Schicht 2", 0.0),
        3 : ("Schicht 3", 0.0),
        4 : ("Schicht 4", 0.0),
        5 : ("Schicht 5", 0.0),
        6 : ("Schicht 6", 0.0)
    }
}

#Dachdiagramm in Abhängigkeit zu Auswahl
roofImage = {
    "Schwer" : "https://raw.githubusercontent.com/oelimar/images/main/Dach_Schwer.png",
    "Mittelschwer" : "https://raw.githubusercontent.com/oelimar/images/main/Dach_Mittel.png",
    "Leicht" : "https://raw.githubusercontent.com/oelimar/images/main/Dach_Leicht.png",
    "Eigener Aufbau" : "https://raw.githubusercontent.com/oelimar/images/main/Dach_Eigen.png"
}

#Voreingestellte HEX Farben für lasten_Stack()
roofColors = {
    "Intensive Dachbegrünung" : "#60b9cb",
    "Extensive Dachbegrünung" : "#6082cb",
    "Photovoltaik" : "#a060cb",
    "Dachlast" : "#CB6062",
    "Windlast" : "#60C5CB",
    "Schneelast" : "#5F6969"
}

#Voreingestellte Dachauflasten. "Bezeichnung" : [Last in kN/m²]
roofAdditives = {
    "Intensive Dachbegrünung" : 2.8,
    "Extensive Dachbegrünung" : 1.5,
    "Photovoltaik" : 0.15
}

#Link zur materials.json
defaultPathGithub = "https://raw.githubusercontent.com/oelimar/images/main/materials.json"


#Lade materials.json vom Github Repository
def load_json_file(file_url):
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        materialSelect = json.loads(response.text)
        return materialSelect

    except Exception:
        return st.text("material.json konnte nicht geladen werden.")

#Speichere material.json im st.session_state, um nicht jedes mal neu laden zu müssen
if "loaded_json" not in st.session_state:
    st.session_state.loaded_json = load_json_file(defaultPathGithub)
#Speichere Dictionary in der Variable materialSelect
materialSelect = st.session_state.loaded_json

#Tabelle der Dichten für Gewichtsberechnung. "Material" : [Dichte in kg/m³]
materialDensity = {
    "Holz" : 500,
    "Stahl" : 7850
}

#Funktion um die Eingabe Kommas und Buchstaben zu ermöglichen
def correctify_input(value):
    try:
        #Variable initialisieren
        numberString = ""

        #Iteriere durch alle Ziffern um Zahlen, Punkte und Kommata zu extrahieren,
        #Falls jemand einen Buchstaben eintippt.
        for character in str(value):
            if character.isdigit() or character == "." or character == ",":
                numberString += character
        valueChanged = str(numberString).replace(",", ".")
        #Mache Wert positiv falls jemand so lustig ist und negative Längen einträgt
        valuePositive = abs(float(valueChanged))  
        return valuePositive
    
    #Falls kein sinnvoller Wert gebildet werden kann:
    except ValueError:
        return None

#Funktion, um Errormeldung zu schreiben, falls correctify_input ein None returned
def print_error_and_set_default(default):
        st.markdown(":red[Bitte gültigen Wert eingeben!]")
        st.markdown(f"Es wird mit {default}m weitergerechnet.")

        return default

#Initialisiere Windlasttabelle S.47
wind_mapping = {
            1: (0.50, 0.65, 0.75),
            2: (0.70, 0.90, 1.00),
            3: (0.90, 1.10, 1.20),
            4: (1.20, 1.30, 1.40)
        }

#Initialisiere Schneelasttabelle S.45
snow_mapping = {
    200 : (0.65, 0.81, 0.85, 1.06, 1.10),
    300 : (0.65, 0.81, 0.89, 1.11, 1.29),
    400 : (0.65, 0.81, 1.21, 1.52, 1.78),
    500 : (0.84, 1.04, 1.60, 2.01, 2.37),
    600 : (1.05, 1.32, 2.06, 2.58, 3.07),
    700 : (1.30, 1.63, 2.58, 3.23, 3.87),
    800 : (1.58, 1.98, 3.17, 3.96, 4.76),
    900 : (None, None, 3.83, 4.78, 5.76),
    1000 : (None, None, 4.55, 5.68, 6.86),
    1100 : (None, None, 5.33, 6.67, 8.06),
    1200 : (None, None, 6.19, 7.73, 9.36),
    1300 : (None, None, None, None, 10.76),
    1400 : (None, None, None, None, 12.26),
    1500 : (None, None, None, None, 13.86)
}

#Initialisiere Schlankheitswerte aus Tabellenbuch S.83/S.117
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

#Randspannungen nach Material
sigmas = {
    "Holz" : (1.3, 0.9), #(Druck, Zug)
    "Stahl" : (21.8, 21.8)
}

#Einstellung wie sich Eingaben je nach Fachwerk verhalten
fieldSettings = {
    "Strebenfachwerk" : (1, 3, 3), # step, start value, min value
    "Parallelträger"  : (2, 4, 4)
}

#Einstellung der Breiten für das gesamte Layout
columnsParameters = [0.45, 0.55]
check = col0_2

#Erstelle ersten Abschnitt
with st.container(border=True):
    st.subheader("Lasteinzugsfeld", divider="red")

    col1, col2 = st.columns(columnsParameters, gap="large")

    with col1:
        trussDistanceInput = st.text_input("Träger Abstand [m]", value="5.25")
        trussDistance = correctify_input(trussDistanceInput)
        #Falls ungültiger Wert erkannt wird, Warnung anzeigen
        if trussDistance == None:
            #Standardwert einfügen, damit bei Error script nicht abbricht
            trussDistance = print_error_and_set_default(5.25)   

        if "roofAdditives" not in st.session_state:
            st.session_state.roofAdditives = roofAdditives
        if "roofColors" not in st.session_state:
            st.session_state.roofColors = roofColors

        if "currentSelection" not in st.session_state:
            st.session_state.currentSelection = None

        #Theoretisch ursprüngliche Auswahlmöglichkeit für Ansicht
        #lastAnzeige = st.radio("Anzeige Lasten", ["Einfach", "Erweitert"], 0, horizontal=True)
        lastAnzeige = "Erweitert"   # Ansicht bis aufs weitere als "Erweitert" festgelegt

        #Ausklappbare Dachaufbauten
        roofTypeExpander = st.expander("Dachaufbau")
        with roofTypeExpander:
            roofType = st.selectbox("Dachaufbau", placeholder="Wähle einen Dachaufbau", index=1, options=roofOptions, label_visibility="collapsed")
            with check:
                reloader = st.button("reload")

            #Anzeige des Diagramms in Abhängigkeit zu Auswahl
            st.image(roofImage[roofType], use_column_width=True)

            #Initialisiere Variablen
            roofLayerSum = 0
            flat_data = []

            #Anfängliche Bearbeitbarkeit in Abhängigkeit von Einstellung des Dachaufbaus
            if roofType == "Eigener Aufbau":
                #Tabelle lässt sich bearbeiten
                roofEditValue = True
            else:
                #Tabelle bleibt statisch
                roofEditValue = False

            roofEdit = st.toggle("Dachlagen bearbeiten", value=roofEditValue)

            #roofLayers JSON struktur in Pandas struktur umwandeln
            for layer, (layer_name, value) in roofLayers[roofType].items():
                flat_data.append({
                "Lage": str(layer),
                "Bezeichnung": layer_name,
                "Last [kN/m²]": value
                })
            #Erzeuge DataFrame
            df = pd.DataFrame(flat_data)

            if roofEdit == True:
                #Erstelle bearbeitbaren DataFrame als Widget
                edited_df = st.data_editor(df, hide_index=True, num_rows="fixed", use_container_width=True, disabled=["Lage"])
            else:
                #Erstelle statischen DataFrame für bessere Darstellung
                st.dataframe(df, hide_index=True, use_container_width=True)
                edited_df = df

            #Aufsummieren aller Werte der Spalte "Last [kN/m²]"
            #abs() damit Negative eingaben trotzdem richtig addiert werden
            roofLayerSum = abs(edited_df["Last [kN/m²]"]).sum()
            #Auf 2 Nachkommastellen runden
            roofLayerSum = round(roofLayerSum, 2)
            st.markdown(f"Die Gesamtlast beträgt **{roofLayerSum} kN/m²**.")

        #Hinzufügen von Aufbaulasten
        roofAddedContainer = st.container()

        addButton = st.button("Eigene Last hinzufügen", type="primary", use_container_width=True, disabled=False)

        #Initialisiere Input
        col1_1, col1_2, col1_3 = st.columns([0.5, 0.3, 0.1], gap="small")
        with col1_1:
            customAdditive = st.text_input("Bezeichnung", label_visibility="collapsed", placeholder="Bezeichnung", value="")
        with col1_2:
            customValueInput = st.text_input("Last",  label_visibility="collapsed", placeholder="Last in kN/m²", value="")
            customValue = correctify_input(customValueInput)
        with col1_3:
            customColor = st.color_picker("Farbe", label_visibility="collapsed", value="#FFFFFF")

        #Counter, um Anzahl an unbenannten Lasten zu zählen
        if "additiveCounter" not in st.session_state:
            st.session_state.additiveCounter = 1

        if addButton:
            with check:
                try:
                    customAdditive, customValue, customColor = correct_input(customAdditive)
                except (ValueError, TypeError):
                    st.empty()
            try:
                #Teste ob Bezeichnugsfeld leer ist
                if customAdditive == "":
                    #Falls keine Bezeichnung eingetragen wird, wird automatisch immer ein neuer Name generiert.
                    customAdditive = "Eigene Last " + str(st.session_state.additiveCounter)
                    st.session_state.additiveCounter += 1
                    if st.session_state.reload:
                        st.session_state.reload = False
                        st.rerun()

                #Füge eigene Last dem st.session_state der Aufbaulasten mit Wert hinzu
                st.session_state.roofAdditives[customAdditive] = float(customValue)
                if customColor == "#FFFFFF":
                    #Wenn keine Farbe gewählt wurde, eigene Farbe generieren
                    customColor = "#" + secrets.token_hex(3) #Generiere random HEX Farbcode "#123456"
                st.session_state.roofColors[customAdditive] = customColor

                #Lade eigene Last in currentSelection
                if st.session_state.currentSelection == None:
                    st.session_state.currentSelection = {}
                st.session_state.currentSelection[customAdditive] = float(customValue)
                    
                # Warnung, falls Wert bei Knopfdruck keinen sinnvollen Wert bilden kann
            except (ValueError, TypeError):
                #ValueError, falls nur ein string übrigbleibt;
                #TypeError falls versucht wird float(None) zu bilden, wenn correctify_input() None ausgibt
                st.markdown(":red[Last unzulässig. Bitte Wert in [kN/m²] angeben.]")

        #Lade derzeitige Auswahl in die Standardauswahl des st.multiselect()
        if st.session_state.currentSelection == None:
            roofAdded_default = []
        else:
            roofAdded_default = list(st.session_state.currentSelection.keys())

        with roofAddedContainer:
            roofAdded = st.multiselect("Zusätzliche Dachlasten", st.session_state.roofAdditives.keys(),
                                       default=roofAdded_default, placeholder="Wähle hier zusätzliche Lasten",
                                       label_visibility="collapsed")

        if roofAdded != roofAdded_default:
            st.session_state.currentSelection = {}
            for name in roofAdded:
                st.session_state.currentSelection[name] = copy.deepcopy(st.session_state.roofAdditives[name])
                roofAdded_default = list(st.session_state.currentSelection.keys())

        #Debug Anzeige
        if debug == True:
            st.text(f"roofAdded: {roofAdded}")
            st.text(f"s_s.currentSelection: {st.session_state.currentSelection}")
            st.text(f"s_s.roofAdditives: {st.session_state.roofAdditives}")

        with st.expander("veränderliche Lasten"):
            #Initialisiere Input
            heightZoneInput = st.text_input("Geländehöhe über NN [m]", value=400 )
            heightZone = correctify_input(heightZoneInput)

            if heightZone == None:
                heightZone = print_error_and_set_default(400)

            #Falls Höhe über 1500m, wird mit 1500 gerechnet
            if int(heightZone) > 1500:
                heightZone = 1500
            
            #Iteriere durch snow_mapping bis Höhe einem Key entspricht
            for height in snow_mapping.keys():
                if int(height) >= int(heightZone):
                    snowHeight = height
                    break

            #Anpassen der maximal/mininmalwerte für Schneezonen in Bezug auf Geländehöhe
            if snow_mapping[snowHeight][0] == None:
                snowMinValue = 3
                snowMinToMax = "[3-5]"
                if snow_mapping[snowHeight][2] == None:
                    snowMinValue = 5
                    snowMinToMax = "[5]"
            else:
                snowMinValue = 1
                snowMinToMax = "[1-5]"

            #Initialisiere Input
            buildingHeightInput = st.text_input("Gebäudehöhe [m]", value=10)
            buildingHeight = correctify_input(buildingHeightInput)

            if buildingHeight == None:
                buildingHeight = print_error_and_set_default(8.50)

            #Indexwahl von wind_mapping je nach Gebäudehöhe
            if buildingHeight <= 10:
                windIndex = 0
            elif 10 < buildingHeight <= 18:
                windIndex = 1
            else:
                windIndex = 2

            col1_4, col1_5 = st.columns([0.5, 0.5], gap="small")
            with col1_4:
                windZone = st.number_input("Windlastzone [1-4]", help="Wähle Anhand der Lage auf der Karte eine der 4 Windlastzonen", step=1, value=2, min_value=1, max_value=4)
                st.image("https://raw.githubusercontent.com/oelimar/images/main/windlasten.png", caption="Windlastzonen in DE")
            with col1_5:
                snowZone = st.number_input(f"Schneelastzone {snowMinToMax}", help="Wähle Anhand der Lage auf der Karte eine der 3 Schneelastzonen", step=1, value=snowMinValue, min_value=snowMinValue, max_value=5)
                st.image("https://raw.githubusercontent.com/oelimar/images/main/schneelasten.png", caption="Schneelastzonen in DE")

        #Berechnung der Schneelast wie in Tabellenbuch S.45 (0.8 wegen Flachdach)
        snowForce = snow_mapping[snowHeight][snowZone - 1] * 0.8

        #Berechnung der Windlast wie in Tabellenbuch S.47 (0.2 wegen Flachdach)
        windForce = wind_mapping[windZone][windIndex] * 0.2

        #Dachlast aus der Aufsummierung der Dachschichten
        roofForce = roofLayerSum
        
        #Variable des Abstands des Lastenstapels zum LEF Trapez
        start_height_stack = 0.5

        #Auf Dachlast noch jede zusätzliche Auflagelast addieren
        for force in roofAdded:
            roofForce += st.session_state.roofAdditives[force]

        #Berechnung der totalen Fläcenlast des Daches
        qTotal = snowForce + windForce + roofForce
        #Berechnung der Streckenlast auf dem Träger
        qTotalField = qTotal * trussDistance

#Erstelle zweiten Abschnitt
with st.container(border=True):
    st.subheader("Fachwerk", divider="red")
    col3, col4 = st.columns(columnsParameters, gap="large")
    
    with col3:
        #Initialisiere Input
        trussType = st.selectbox("Fachwerkart", placeholder="Wähle ein Fachwerk", options=trussOptions, index=0)

        #Bei Parallelträger zusätzliche Eingabe anzeigen
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


#Erstelle dritten Abschnitt
with st.container(border=True):
    st.subheader("Querschnitte", divider="red")
    st.write("")
    
    #Initialilisier Bauteilobjekt, in dem später alle Bauteile abgespeichert werden
    struts_all_combined = {}

    querschnittContainer = st.container(border=False)
    obergurtColumn, strebenColumn, untergurtColumn = st.columns([1, 1, 1], gap="medium")
    
    with querschnittContainer:
        ALL_col_1, ALL_col_2 = st.columns(columnsParameters, gap="large")
        allOrEach = st.toggle("Individuelle Eingabe")
        
        #Ist die individuelle Eingabe deaktiviert, übertrage Materialwerte auf alle Spalten
        if allOrEach == False:
            with ALL_col_1:
                ALL_material = st.selectbox("Material", placeholder="Wähle ein Material",
                                            options=materialSelect.keys(), key="ALL_material")
            with ALL_col_2:
                ALL_profile = st.selectbox("Profil", placeholder="Wähle ein Profil",
                                           options=materialSelect[ALL_material].keys(), key="ALL_profile")
            
            OG_material = ST_material = UG_material = ALL_material
            OG_profile = ST_profile = UG_profile = ALL_profile

        with obergurtColumn:
            #Initialisiere Obergurt Spalte
            st.subheader("Obergurt")                
            OG_col_5_1, OG_col_5_2 = st.columns([0.4, 0.6], gap="small")

            if allOrEach == True:
                with OG_col_5_1:
                    OG_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="OG_material")  # key attribut, damit sich selectboxen untereinander unterscheiden
                with OG_col_5_2:
                    OG_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[OG_material].keys(), key="OG_profile")

            #Bestimmung der Randspannung für das Material
            if OG_material in sigmas:
                OG_sigma_rd = sigmas[OG_material]
            else:
                #Eingabe falls keine Randspannung gefunden werden kann
                st.markdown(":red[Zu dem Material ist keine Randspannung vorhanden.]")
                OG_sigmaInput = st.text_input("", placeholder="Randspannung in kN/cm²", key="OG_sigmaInput")
                if OG_sigmaInput:
                    OG_sigma_rd = [OG_sigmaInput, OG_sigmaInput]

            #Baue Struktur für Nachweise
            OG_stress_expander = st.expander("Spannungsnachweis")
            with OG_stress_expander:
                OG_stress_einheiten = st.container()
                OG_stress_latex = st.container()

        with strebenColumn:
            #Initialisiere Streben Spalte
            st.subheader("Streben")
                
            ST_col_5_1, ST_col_5_2 = st.columns([0.4, 0.6], gap="small")

            if allOrEach == True:
                with ST_col_5_1:
                    ST_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="ST_material")
                with ST_col_5_2:
                    ST_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[ST_material].keys(), key="ST_profile")

            #Bestimmung der Randspannung für das Material
            if ST_material in sigmas:
                ST_sigma_rd = sigmas[ST_material]
            else:
                #Eingabe falls keine Randspannung gefunden werden kann
                st.markdown(":red[Zu dem Material ist keine Randspannung vorhanden.]")
                ST_sigmaInput = st.text_input("", placeholder="Randspannung in kN/cm²", key="ST_sigmaInput")
                if ST_sigmaInput:
                    ST_sigma_rd = ST_sigmaInput

            #Baue Struktur für Nachweise
            ST_stress_expander = st.expander("Spannungsnachweis")
            with ST_stress_expander:
                ST_stress_einheiten = st.container()
                ST_stress_latex = st.container()

        with untergurtColumn:
            #Initialisiere Untergurt Spalte
            st.subheader("Untergurt")
                
            UG_col_5_1, UG_col_5_2 = st.columns([0.4, 0.6], gap="small")

            if allOrEach == True:
                with UG_col_5_1:
                    UG_material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys(), key="UG_material")
                with UG_col_5_2:
                    UG_profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[UG_material].keys(), key="UG_profile")

            #Bestimmung der Randspannung für das Material
            if UG_material in sigmas:
                UG_sigma_rd = sigmas[UG_material]
            else:
                #Eingabe falls keine Randspannung gefunden werden kann
                st.markdown(":red[Zu dem Material ist keine Randspannung vorhanden.]")
                UG_sigmaInput = st.text_input("", placeholder="Randspannung in kN/cm²", key="UG_sigmaInput")
                if UG_sigmaInput:
                    UG_sigma_rd = UG_sigmaInput

            #Baue Struktur für Nachweise
            UG_stress_expander = st.expander("Spannungsnachweis")
            with UG_stress_expander:
                UG_stress_einheiten = st.container()
                UG_stress_latex = st.container()
    
    #Baue Struktur für Stabkräfte
    kraefteContainer = st.container(border=True)
    with kraefteContainer:
        col6_1, col6_2, col6_3 = st.columns([0.3, 0.3, 0.3], gap="medium")

    #Baue Struktur für Bauteilliste
    bauteilContainer = st.container(border=False)
    with bauteilContainer:
        bauteilExpander = st.expander(f"Bauteilliste und weitere Informationen", expanded=False)



#Definiere die benötigten Funktionen
        
#Definiere Funktion zum Zeichnen der Streckenlast über dem Träger
def draw_q_over_truss(minNodeX, minNodeY, ax):
    
    #Definiere Eckpunkte des Streckenlast Rechtecks
    qNodes = [
        [minNodeX, minNodeY + trussHeight * 4/3],
        [minNodeX, minNodeY + 0.5 + trussHeight * 4/3],
        [minNodeX + trussWidth, minNodeY + 0.5 + trussHeight * 4/3],
        [minNodeX + trussWidth, minNodeY + trussHeight * 4/3]
    ]

    #Fülle Rechteck mit hellblauer Farbe und weiß gestrichelt
    ax.fill([point[0] for point in qNodes], [point[1] for point in qNodes], color="white", facecolor="lightblue", hatch="|", alpha=0.7)
    ax.annotate(f"q = {float(qTotalField):.2f} kN/m", (minNodeX + trussWidth / 2, minNodeY + 0.5 + trussHeight * 4.5/3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)

#Definiere Funktion zum Zeichnen der Maßbänder unter dem Träger
def draw_mass_band(minNodeX, minNodeY, ax):
    
    #Zeichne schwarze "+" Zeichen an den Enden des Tragwerks
    ax.plot(minNodeX, minNodeY / 2, "k+", markersize=10)
    ax.plot(minNodeX + trussWidth, minNodeY / 2, "k+", markersize=10)
    ax.plot([minNodeX, minNodeX + trussWidth], [minNodeY / 2, minNodeY / 2], "k-", linewidth=1)

    #Für Anzahl an Feldern, Zeichne schwarze "+" Zeichen entlang dem Tragwerk
    measure = 0
    while measure < fieldNumber + 1:
        ax.plot(minNodeX + measure * distanceNode, 2* minNodeY / 3, "k+", markersize=10)
        if measure < fieldNumber:
            ax.plot([minNodeX + measure * distanceNode, minNodeX + (measure + 1) * distanceNode],[2 * minNodeY / 3, 2 * minNodeY / 3], "k-", linewidth=1)
            ax.annotate(f"{float(distanceNode):.2f}m", (minNodeX + distanceNode / 2 + measure * distanceNode, 3 * minNodeY / 4), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)
        measure += 1

    #Zeichne Maßband für Höhe
    ax.plot(minNodeX / 2, minNodeY, "k+", markersize=10)
    ax.plot(minNodeX / 2, minNodeY + trussHeight, "k+", markersize=10)
    ax.plot([minNodeX / 2, minNodeX / 2], [minNodeY, minNodeY + trussHeight], "k-", linewidth=1)

    #Beschrifte Maßbänder
    ax.annotate(f"{float(trussWidth):.2f}m", (minNodeX + trussWidth / 2, minNodeY / 3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)
    ax.annotate(f"{float(trussHeight):.2f}m", (minNodeX / 3, minNodeY + trussHeight / 2), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, rotation=90, annotation_clip=False)

#Definiere Funktion zum Setzen der Plot Einstellungen
def set_ax_settings(minNodeX, minNodeY, ax):

    #Entferne Axenbeschriftung
    ax.set_xticks([])
    ax.set_yticks([])

    #Setze Limits des Plots
    ax.set_xlim([0, trussWidth + 2 * minNodeX])
    ax.set_ylim([0, trussHeight + 2 * minNodeY])

    #Setze X- und Y-Achsen Maßstabsverhältnis
    ax.set_aspect(1.5, adjustable='datalim')

    #Entferne Ränder um die Zeichenfläche
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

#Definiere Funktion zum Zeichnen des Parallelträgers
def draw_truss_parallel(strebenParallel):
    
    #Initiiere Variablen
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNodeY = minNodeY + trussHeight
    nrNode = int(fieldNumber) + 1
    nodeArray = []

    #Generiere Knotenkoordinaten
    i = 0
    while i < nrNode:
        nodeArray.append((float(minNodeX + i * distanceNode), minNodeY))
        nodeArray.append((float(minNodeX + i * distanceNode), maxNodeY))
        i += 1

    #Initiiere matplotlib Zeichenfläche
    fig, ax = plt.subplots()

    #Generiere Anfangs- und Endpunkt der Stäbe links der Mitte
    edges = []
    i = 0
    while i < fieldNumber/2:
        if strebenParallel == "Fallende Diagonalen":
            edgesFront = [
                (1 + i*2, 0 + i*2), #(Startpunkt, Endpunkt)
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

    #Generiere Anfangs- und Endpunkt der Stäbe rechts der Mitte
    while fieldNumber/2 - 1 < i < fieldNumber :
        if strebenParallel == "Fallende Diagonalen":
            edgesBack = [
                (0 + i*2, 1 + i*2), #(Startpunkt, Endpunkt)
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

    #Für jeden Stab, Zeichne rote Linie von Anfangs bis Endpunkt
    for edge in edges:
        start_node = nodeArray[edge[0]]
        end_node = nodeArray[edge[1]]
        ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)

    #Knoten an den Ecken definieren
    nodeCorner = [
        (nodeArray[0][0], nodeArray[0][1]),
        (nodeArray[-2][0], nodeArray[-2][1])
    ]

    #Zeichne schwarzen Kreis auf allen Knotenkoordinaten
    for node in nodeArray:
        ax.plot(node[0], node[1], 'ko', markersize=5)

    #Zeichne schwarzes Dreieck auf allen Eckkoordinaten
    for node in nodeCorner:
        ax.plot(node[0], node[1], "k^", markersize=10)

    #Füge Maßbänder und Streckenlast hinzu
    draw_mass_band(minNodeX, minNodeY, ax)
    draw_q_over_truss(minNodeX, minNodeY, ax)
    #Lade Einstellungen für Darstellung
    set_ax_settings(minNodeX, minNodeY, ax)

    #Zeichne Plot
    st.pyplot(fig, use_container_width=True)

    #Debug Anzeige
    if debug == True:
        st.text(nodeArray)
        st.text(len(nodeArray))

#Definiere Funktion zum Zeichnen des Strebenfachwerks
def draw_truss_strebe():

    #Initiiere Variablen
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNode = minNodeY + trussHeight
    nrNodeLower = int(fieldNumber) 
    nrNodeUpper = int(fieldNumber) + 1
    nodeArray = []
    nodeLower = []
    nodeUpper = []

    #Initiiere matplotlib Zeichenfläche
    fig, ax = plt.subplots()    

    #Generiere untere Reihe der Knoten
    nodeL = 0
    while nodeL < nrNodeLower:
        nodeLower.append((float((minNodeX + (distanceNode / 2)) + nodeL * distanceNode), minNodeY))
        nodeL += 1

    #Generiere obere Reihe der Knoten
    nodeU = 0
    while nodeU < nrNodeUpper:
        nodeUpper.append((float(minNodeX + nodeU * distanceNode), maxNode))
        nodeU += 1

    #Flechte obere und untere Reihe zusammen
    nodeArray = [item for pair in zip(nodeUpper, nodeLower) for item in pair]
    #Füge den letzten Knoten der längeren Reihe hinten an
    if len(nodeLower) < len(nodeUpper):
        nodeArray.extend(nodeUpper[len(nodeLower):])
    
    #Initialisiere ersten Teil des Tragwerks
    edges = [
        (1, 0),
        (0, 2),
        (2, 1)
    ]

    #Generiere Anfangs- und Endpunkt der Stäbe
    i = 0
    while i < fieldNumber - 1:
        edgeExtend = [
            (1 + 2 * i, 3 + 2 * i), #(Startpunkt, Endpunkt)
            (3 + 2 * i, 4 + 2 * i),
            (4 + 2 * i, 2 + 2 * i),
            (2 + 2 * i, 3 + 2 * i)
        ]
        edges.extend(edgeExtend)
        i += 1

    #Für jeden Stab, Zeichne rote Linie von Anfangs bis Endpunkt
    for edge in edges:
        start_node = nodeArray[edge[0]]
        end_node = nodeArray[edge[1]]
        ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)

    #Knoten an den Ecken definieren
    nodeCorner = [
        (nodeUpper[0][0], nodeUpper[0][1] - trussHeight),
        (nodeUpper[-1][0], nodeUpper[-1][1] - trussHeight)
    ]

    #Zeichne zusätzliche Stäbe um das Strebenfachwerk herum
    ax.plot([nodeArray[0][0], nodeCorner[0][0]], [nodeArray[0][1], nodeCorner[0][1]], "r-", linewidth=2)
    ax.plot([nodeCorner[1][0], nodeCorner[0][0]], [nodeCorner[1][1], nodeCorner[0][1]], "r-", linewidth=2)
    ax.plot([nodeArray[-1][0], nodeCorner[1][0]], [nodeArray[-1][1], nodeCorner[1][1]], "r-", linewidth=2)

    #Zeichne schwarzen Kreis auf allen Knotenkoordinaten
    for node in nodeLower:
        ax.plot(node[0], node[1], 'ko', markersize=5)
    for node in nodeUpper:
        ax.plot(node[0], node[1], "ko", markersize=5)

    #Zeichne schwarzes Dreieck auf allen Eckkoordinaten
    for node in nodeCorner:
        ax.plot(node[0], node[1], "k^", markersize=10)

    #Füge Maßbänder und Streckenlast hinzu
    draw_mass_band(minNodeX, minNodeY, ax)
    draw_q_over_truss(minNodeX, minNodeY, ax)
    #Lade Einstellungen für Darstellung
    set_ax_settings(minNodeX, minNodeY, ax)

    #Zeichne Plot
    st.pyplot(fig, use_container_width=True)

    #Debug Anzeige
    if debug == True:
        st.text(f"Lower Nodes: {nodeLower}")
        st.text(f"Upper Nodes: {nodeUpper}")
        st.text(f"Corner Nodes: {nodeCorner}")
        st.text(f"Combined Nodes: {nodeArray}")

#Definiere Funktion zum Zeichnen des Lastenstapels auf dem LEF
def lasten_stack(nodes, last, debugOutput=False):

    #Lade Anfangshöhe in st.session_state
    if "stackStartHeight" not in st.session_state:
        st.session_state.stackStartHeight = start_height_stack

    #Verändere Maximalhöhe des Stapels je nach Breite der Darstellung
    if trussDistance <= 5:
        totalHeight = trussDistance * 0.6   #Werte noch gleich
    if trussDistance > 5:
        totalHeight = trussDistance * 0.6   #Könnten geändert werden
    
    #Höhe der Last proportional zur Gesamtlast
    lastenHeight = (last / qTotal) * totalHeight

    #Definiere Eckpunkte des Stapelschichtrechtecks
    nodesStack = [
        [nodes[0][0], nodes[0][1] + st.session_state.stackStartHeight],
        [nodes[1][0], nodes[1][1] + st.session_state.stackStartHeight],
        [nodes[1][0], nodes[1][1] + st.session_state.stackStartHeight + lastenHeight],
        [nodes[0][0], nodes[0][1] + st.session_state.stackStartHeight + lastenHeight]
    ]

    #Debug Anzeige
    if debugOutput == True:
        if debug == True:
            st.text(f"fängt an bei: {st.session_state.stackStartHeight:.2f}," +
                    f"mit Höhe {lastenHeight:.2f} weiter")
            st.text(qTotal)

    #Aktualisiere stackStartHeight um letzte Lastenhöhe
    st.session_state.stackStartHeight += lastenHeight

    #Gebe Knoten für Schicht aus
    return nodesStack

#Definiere Funktion zum Zeichnend des LEFs auf dem System
def draw_LEF():

    #Initiiere Variablen
    minNodeLEF = trussDistance / 5
    minNodeLEFy = 2

    #Definiere Stäbe für Trägers mit Stütze
    edgesLEF = [
        (0, 1),
        (1, 2),
        (2, 3),
        (4, 5)
    ]

    #Definiere Knoten für Träger mit Stütze
    nodesLEF = [
        [minNodeLEF, minNodeLEFy + 2.2],
        [minNodeLEF, minNodeLEFy + 4.5],
        [minNodeLEF + 2.75, minNodeLEFy + 3],
        [minNodeLEF + 2.75, minNodeLEFy + 0.3],
        [minNodeLEF, minNodeLEFy + 4.1],
        [minNodeLEF + 2.75, minNodeLEFy + 2.6]
    ]

    #Definiere Eckpunkte der gefüllten Dachfläche
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
    
    #Definiere Dachflächen als hellblau gefüllte Parallelogramme
    #LEF_graph1 wird opaker gezeichnet, um LEF anzudeuten
    LEF_graph0 = plt.Polygon(nodesForceField[0], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.3)
    LEF_graph1 = plt.Polygon(nodesForceField[1], closed = True, edgecolor="lightblue", facecolor="lightblue", alpha=0.5)
    LEF_graph2 = plt.Polygon(nodesForceField[2], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.3)

    #Initiiere matplotlib Zeichenfläche
    fig, ax = plt.subplots()

    #Zeichne 3 mal Träger mit Stützen
    truss = 0
    while truss < 3:
        #Zeichne Stäbe als rote Linie
        edgeNr = 0
        for edge in edgesLEF:
            start_node = [nodesLEF[edge[0]][0] + truss * trussDistance, nodesLEF[edge[0]][1]]
            end_node = [nodesLEF[edge[1]][0] + truss * trussDistance, nodesLEF[edge[1]][1]]

            #Oberste Linie dicker zeichnen um Träger zu visualisieren
            if edgeNr in [1, 3]:
                ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)
            else:
                ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)
            edgeNr += 1

        #Zeichne Knoten als schwarze Kreise
        nodeNr = 0
        for node in nodesLEF:
            if nodeNr not in [1, 2]:    # dont draw the upper 2 nodes
                ax.plot(node[0] + truss * trussDistance, node[1], 'ko', markersize=5)
            nodeNr += 1
        truss += 1

    #Initiiere leeres Dictionary für alle gewählten Schichten auf Dach
    if "completeRoofAdditives" not in st.session_state:
        st.session_state.completeRoofAdditives = {}

    #Fülle completeRoofAdditives mit roofAdditive Werten, ohne selben Memory platz zu teilen
    st.session_state.completeRoofAdditives = copy.deepcopy(st.session_state.roofAdditives)

    #Erstelle Liste aller zurzeit gewählten Auflasten
    completeRoofStack = roofAdded
    
    #Füge Dach-, Schnee- und Windlast in Dictionary der Dachlasten hinzu
    st.session_state.completeRoofAdditives["Dachlast"] = roofLayerSum
    st.session_state.completeRoofAdditives["Windlast"] = round(windForce, 2)
    st.session_state.completeRoofAdditives["Schneelast"] = round(snowForce, 2)

    #Schnee und Windlast zu bestehendem Dachstapel hinzufügen
    completeRoofStack.extend(["Schneelast", "Windlast"])
    #Dachlast auf Index 0 zum bestehenden Dachstapel hinzufügen
    completeRoofStack.insert(0, "Dachlast")

    #Debug Anzeige
    if debug == True:
        st.text(f"roofAdded {roofAdded}")
        st.text(f"completeRoofStack {completeRoofStack}")
        st.text(f"st.session_state.completeRoofAdditives {st.session_state.completeRoofAdditives}")
        st.text(f"st.session_state.roofAdditives {st.session_state.roofAdditives}")
        st.text(completeRoofStack)

    #Zeichne erweiterte Ansicht
    if lastAnzeige == "Erweitert":

        #Für jeden Eintrag in aktuellen Lasten, zeichne Rechteck
        for name in completeRoofStack:
            turn = 0
            annotateNodes = []

            #Füge für jede Schicht die Eckpunkte zu Liste hinzu
            for nodes in lasten_stack(nodesForceField[1], st.session_state.completeRoofAdditives[name], debugOutput=True):
                annotateNodes.append(nodes)
                turn += 1

            #Debug Anzeige
            if debug == True:
                st.text(f"{annotateNodes}")
                st.text(f"{annotateNodes[0][0]}, {annotateNodes[2][1]}")
            
            #Text um halbe Höhe heruntersetzen
            #(höhere Y-Koordinate minus untere Y-Koordinate) / 2
            halfHeight = (annotateNodes[2][1] - annotateNodes[1][1]) / 2 

            #Füge Beschriftung der Bezeichnung hinzu
            ax.annotate(f"- {name}", (annotateNodes[1][0], annotateNodes[2][1] - halfHeight),
                        xytext=(10, 0), textcoords='offset points', va='center',
                        fontsize=8, annotation_clip=False)
            #Füge Beschriftung der Last hinzu
            ax.annotate(f"{st.session_state.completeRoofAdditives[name]}kN/m²",
                        (annotateNodes[1][0] - (trussDistance / 2), annotateNodes[2][1] - halfHeight),
                        xytext=(0, 0), textcoords='offset points', ha='center', va='center',
                        fontsize=8, annotation_clip=False, color="black")

            #Fülle Eckpunkte mit Farbe der Last
            stackPatch = plt.Polygon(annotateNodes, facecolor=st.session_state.roofColors[name], closed = True, edgecolor=st.session_state.roofColors[name], alpha=0.15, zorder=2 )
            ax.add_patch(stackPatch)

        #Füge Beschriftung für Gesamtlast hinzu
        ax.annotate(f"q = {qTotal:.2f}kN/m²", (minNodeLEF + trussDistance ,start_height_stack + minNodeLEFy + 4.5 + (st.session_state.stackStartHeight / 2)), xytext=(-100, -5), textcoords='offset points', ha="center", va='center', fontsize=8, annotation_clip=False)
        
        #Lösche Anfangshöhe aus st.session_state
        if "stackStartHeight" in st.session_state:
            del st.session_state["stackStartHeight"]

        
    #Zeichne Maßband für LEF
    measure = 0
    while measure < 3:
        ax.plot((minNodeLEF + 3) + measure * trussDistance, minNodeLEFy / 2, "k+", markersize=10)
        if measure < 2:
            ax.plot([(minNodeLEF + 3) + measure * trussDistance, (minNodeLEF + 3) + (measure + 1) * trussDistance],[minNodeLEFy / 2, minNodeLEFy / 2], "k-", linewidth=1)
            ax.annotate(f"{float(trussDistance):.2f}m", ((minNodeLEF + 3) + trussDistance / 2 + measure * trussDistance, minNodeLEFy / 3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)
        measure += 1

    #Setze Limits des Plots
    ax.set_xlim([0, 2 * trussDistance + 2 * minNodeLEF + 3])
    ax.set_ylim([0, 2 * 4 + 2 * minNodeLEF])

    #Füge Dachflächen auf Träger ein
    ax.add_patch(LEF_graph0)
    ax.add_patch(LEF_graph1)
    ax.add_patch(LEF_graph2)

    #Nicht mehr genutzte Anzeige für Last
    if lastAnzeige == "Einfach":
        ax.annotate(f"q = g + w + s\nq = {float(roofForce):.2f} kN/m² + {float(windForce):.2f} kN/m² + {float(snowForce):.2f} kN/m²\n\nq = {float(qTotal):.2f} kN/m²", ((2 * trussDistance + 2 * minNodeLEF + 3)/2, 2 * 4 + 2 * minNodeLEF- minNodeLEF), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)

    #Entferne Achsenbeschriftung
    ax.set_xticks([])
    ax.set_yticks([])

    #Entferne Ränder um die Zeichenfläche
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #Setze X- und Y-Achsen Maßstabsverhältnis
    ax.set_aspect('equal', adjustable='datalim')

    # Show the plot
    st.pyplot(fig, use_container_width=True)

    #Debug Anzeige
    if debug == True:
        st.text(f"zusätzliche Lasten: {roofAdded}")
        st.text(f"Lasten: {st.session_state.roofAdditives}")

#Definiere Funktion zum Analysieren der einzelnen Stäbe an gegebener Position
def analyze_struts(strutObergurt, strutDiagonal, strutUntergurt, strutElse, strutToCheck):
    
    #Analysiere jede Position einzeln
    if strutToCheck == "Obergurt":
        nr, length, material, profile, chosenProfile = strutObergurt
    if strutToCheck == "Streben":
        nr, length, material, profile, chosenProfile = strutDiagonal
    if strutToCheck == "Untergurt":
        nr, length, material, profile, chosenProfile = strutUntergurt

    #Erzeuge alle Werte für Bauteilliste
    materialVolume = (materialSelect[material][profile][chosenProfile][0] * length * nr)/1000
    struts_all_combined[strutToCheck] = {
        "Anzahl" : nr,
        "Länge" : length,
        "Länge gesamt" : length * nr,
        "Material" : f"{material}",
        "Profil" : f"{chosenProfile} {profile}",
        "Volumen" : materialVolume,
        "Gewicht" : materialVolume * materialDensity[material]
    }

    #Füge die undefinierten Stäbe ebenfalls der Bauteilliste zu
    if strutToCheck == "Untergurt":
        counter = 1
        for strut in strutElse:            
            nr, length, material, profile, chosenProfile = strut             
            strutName = f"Weitere Stäbe {counter}"
            materialVolume = (materialSelect[material][profile][chosenProfile][0] * length * nr)/1000
            struts_all_combined[strutName] = {
                "Anzahl" : nr,
                "Länge" : length,
                "Länge gesamt" : length * nr,
                "Material" : None,
                "Profil" : f"undefiniert",
                "Volumen" : 0,
                "Gewicht" : 0
            }
            counter += 1

#Definiere Funktion zur Angabe der Anzahl an Knoten 
def number_of_nodes(trussType):
    if trussType == "Strebenfachwerk":
        nodesNr = (fieldNumber * 2) + 3
    if trussType == "Parallelträger":
        nodesNr = (fieldNumber + 1) * 2
    return nodesNr

#Definiere Funktion zur Analyse eines Fachwerkes
def analyze_truss(strutToCheck, material, profile, chosenProfile):

    #Berechnung für Strebenfachwerk
    if trussType == "Strebenfachwerk":
        diagonalLength = math.sqrt((pow(distanceNode/2, 2)) + (pow(trussHeight, 2)))
        
        #[Anzahl, Länge der Stäbe, material, profile, chosenProfile]
        strutDiagonal = [(fieldNumber*2), diagonalLength, material, profile, chosenProfile]
        strutObergurt = [fieldNumber, distanceNode, material, profile, chosenProfile]
        strutUntergurt = [fieldNumber - 1, distanceNode, material, profile, chosenProfile]
        strutElse = [[2, trussHeight, material, profile, chosenProfile], [2, (distanceNode/2), material, profile, chosenProfile]]
        analyze_struts(strutObergurt, strutDiagonal, strutUntergurt, strutElse, strutToCheck)
        return
    
    #Berechnung für Parallelträger
    if trussType == "Parallelträger":
        diagonalLength = math.sqrt((pow(distanceNode, 2)) + (pow(trussHeight, 2)))

        #[Anzahl, Länge der Stäbe, material, profile, chosenProfile]
        strutObergurt = strutUntergurt = [fieldNumber, distanceNode, material, profile, chosenProfile]
        strutDiagonal = [fieldNumber, diagonalLength, material, profile, chosenProfile]
        strutElse = [[fieldNumber + 1, trussHeight, material, profile, chosenProfile]]
        analyze_struts(strutObergurt, strutDiagonal, strutUntergurt, strutElse, strutToCheck)
        return
    
    else:
        return False

#Definiere Funktion zum Berechnen der Stablasten im Strebenfachwerk
def calc_strebewerk(strutToCheck, print_forces=False):

    #Initiiere Variablen
    diagonalLength = math.sqrt((pow(distanceNode/2, 2)) + (pow(trussHeight, 2)))
    diagonalAlpha = math.asin(trussHeight/diagonalLength)
    qProd = 0 #Summe aller Momente durch Q
    qSum = 0 #Summe aller Q Punktlasten
    qNum = []
    forceAuflager = (qTotal*trussDistance*trussWidth)/2
    totalLast = qTotal*trussDistance*trussWidth
    punktLastAussen = totalLast/(fieldNumber * 2)

    qCount = 1
    #math.ceil() zum Aufrunden
    if math.ceil(fieldNumber/2) == 1:
        #Speichere (Q Punktlast, Entfernung zu Drehpunkt) in Tupel
        qTemp = (float((qTotal*trussDistance*trussWidth)/fieldNumber), float(qCount * (trussWidth/fieldNumber)))
        qNum.append(qTemp)
    else:
        #Speichere Punktlasten bis zum mittleren Feld
        while qCount < math.ceil(fieldNumber/2):
            #Speichere (Q Punktlast, Entfernung zu Drehpunkt) in Tupel
            qTemp = (float((qTotal*trussDistance*trussWidth)/fieldNumber), float(qCount * (trussWidth/fieldNumber)))
            qNum.append(qTemp)
            qCount += 1
        #Falls Anzahl de Felder gerade ist, füge eine Punktlast in der Mitte hinzu
        if fieldNumber % 2 == 0:
            qNum.append(((qTotal*trussDistance*trussWidth)/fieldNumber, 0))




    #Evaluiere qNum
    for num in qNum:
        #Summe der Momente
        qProd += num[0] * num[1]
        #Summe der Punktlasten
        qSum += num[0]

    #Berechne Stabkräfte im mittleren Feld
    maxForceU = ((punktLastAussen * math.ceil(fieldNumber/2) * trussWidth/fieldNumber * -1) - qProd + ((forceAuflager) * math.ceil(fieldNumber/2) * trussWidth/fieldNumber)) / trussHeight
    ForceDmiddle = ((punktLastAussen + qSum - (totalLast/2)) / math.sin(diagonalAlpha))
    maxForceO = (-maxForceU - (math.cos(diagonalAlpha)*ForceDmiddle))

    #Berechne Stabkräfte im äußeren Feld
    ForceOaussen = ((punktLastAussen * (trussWidth/(fieldNumber*2))) - (forceAuflager * (trussWidth/(fieldNumber*2)))) / trussHeight
    maxForceD = (forceAuflager - punktLastAussen) / math.sin(diagonalAlpha)

    #Entscheide welcher der Werte ausgegeben werden soll
    if strutToCheck == "Obergurt":
        maxForce = maxForceO
    if strutToCheck == "Streben":
        maxForce = maxForceD
    if strutToCheck == "Untergurt":
        maxForce = maxForceU

    #Trage Maximale Kräfte auf Seite ein
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
    
    #Debug Anzeige
    if debug == True:
            st.subheader("debug:")
            st.text(f"Diagonalstab Länge: {diagonalLength}m")
            st.text(f"Punktlast aussen: {punktLastAussen}")
            st.text(f"alpha: {math.degrees(diagonalAlpha)}")
            st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
            st.text(f"Qs generiert: {len(qNum)}\nmit Werten: {qNum}\ninsgesamt Momente: {float(qProd):.2f}")
            st.text(f"Kraft im äußeren Obergurt: {ForceOaussen} kN")

    #Gebe die maximale Kraft der gewählten Position aus
    return maxForce

#Definiere Funktion zum Berechnen der Stablasten im Parallträger
def calc_parallel(strebenParallel, strutToCheck, print_forces=False):

    #Initiiere Variablen
    diagonalLength = math.sqrt((pow(distanceNode, 2)) + (pow(trussHeight, 2)))
    diagonalAlpha = math.asin(trussHeight/diagonalLength)
    forceAuflager = (qTotal*trussDistance*trussWidth)/2
    totalLast = qTotal*trussDistance*trussWidth
    punktLastAussen = totalLast/(fieldNumber * 2)
    qProd = 0 #Summe aller Momente durch Q
    qSum = 0 #Summe aller Q Punktlasten
    qNum = []
    

    i = 1
    while i < (fieldNumber / 2):
        #Speichere (Q Punktlast, Entfernung zu Drehpunkt) in Tupel
        qTemp = (totalLast / fieldNumber, i * distanceNode)
        qNum.append(qTemp)
        i += 1
    #Füge äußerste Punktlast hinzu
    qNum.append((punktLastAussen, i * distanceNode))
    #Füge Auflagerkraft hinzu
    qNum.append((-forceAuflager, i * distanceNode))

    #Evaluiere qNum
    for num in qNum:
        #Summe der Punktlasten
        qSum += num[0]
        #Summe der Momente
        qProd += (num[0] * num[1])

    #Berechnung für mittleren Diagonalstab
    #Ist zwar nicht meistbelastet, aber für maxForceU dringend nötig
    if strebenParallel == "Fallende Diagonalen":
        #Sind die Strebend fallend, ist die Stabkraft invertiert
        ForceDmiddle = (-qSum)/math.sin(diagonalAlpha)
    else:
        ForceDmiddle = (qSum)/math.sin(diagonalAlpha)

    #Berechnung für Stabkräfte in mittlerem Feld
    maxForceO = (qProd)/trussHeight
    maxForceU = -maxForceO - (ForceDmiddle*math.cos(diagonalAlpha))

    #Berechnung für Stabkräfte in äußerem Feld
    ForceOaussen = (punktLastAussen * distanceNode) - (forceAuflager * distanceNode)
    maxForceD = (-punktLastAussen + forceAuflager) / math.sin(diagonalAlpha)

    #Sind die Strebend fallend, ist die Stabkraft invertiert
    if strebenParallel != "Fallende Diagonalen":
        maxForceD = -maxForceD    

    #Entscheide welcher der Werte ausgegeben werden soll
    if strutToCheck == "Obergurt":
        maxForce = maxForceO
    if strutToCheck == "Streben":
        maxForce = maxForceD
    if strutToCheck == "Untergurt":
        maxForce = maxForceU

    #Trage Maximale Kräfte auf Seite ein
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

    #Debug Anzeige
    if debug == True:
            st.subheader("debug:")
            st.text(f"Diagonalstab Länge: {diagonalLength}m")
            st.text(f"Punktlast aussen: {punktLastAussen}")
            st.text(f"total Last: {totalLast}")
            st.text(f"alpha: {math.degrees(diagonalAlpha)}")
            st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
            st.text(f"Qs generiert: {len(qNum)}\nmit Werten: {qNum}\ninsgesamt Momente: {float(qProd):.2f}")
            st.text(f"Kraft im äußeren Obergurt: {ForceOaussen} kN")
    
    #Gebe die maximale Kraft der gewählten Position aus
    return maxForce

#Definiere Funktion zur Berechnung nach Fachwerkart
def calc(trussType, strutToCheck, print_forces=False):
    if trussType == "Strebenfachwerk":
        maxForce = calc_strebewerk(strutToCheck, print_forces)
    if trussType == "Parallelträger":
        maxForce = calc_parallel(strebenParallel, strutToCheck, print_forces)
    return maxForce

#Definiere Funktion um numerischen Teil aus String zu extrahieren
def extract_numerical_part(key):
    #Extrahiere Numerischen Teil aus Profilbezeichnung
    #Seispiel: "8" -> 8, "12/12" -> 12
    return int(key.split('/')[0]) if '/' in key else int(key)

#Definiere Funktion um Spannungsnachweis durchzuführen
def stress_verification(material, profile, maxForce, stress_latex): # Spannungsnachweis zur Wahl des ersten Querschnitts

    #Dimensioniere maxForce mit Sicherheitsbeiwert γF = 1.4
    maxForce_d = abs(maxForce) * 1.4
    
    if maxForce < 0:
        #Bei Druckkraft, nutze erstes Sigma
        sigma_rd = sigmas[material][0]
    else:
        #Bei Zugkraft, nutze zweites Sigma
        sigma_rd = sigmas[material][1]

    #Berechnete minimale Querschnittsfläche
    areaCalc = maxForce_d/sigma_rd

    #Debug Anzeige
    if debug == True:
        st.text(f"benötigte Oberfläche: {areaCalc:.2f}cm²")
    
    #Iteriere durch jeden Querschnitt im gewählten Profil
    for profil, values in materialSelect[material][profile].items():
        area = values[0]
        #Wenn Querschnittsfläche > berechneter Fläche
        if area > areaCalc:
            #Speichere aktuelles profil
            chosenProfile = profil

            #Zeichne LaTeX Berechnungen
            with stress_latex:
                A_min = r"A_{min}"
                math_expression = r"A_{min} = \frac{{Nd}}{{\sigma_{Rd}}}"
                math_expression2 = f"{A_min} = {areaCalc:.2f} cm²"
                st.latex(math_expression)
                st.latex(math_expression2)
            
            #Debug Anzeige
            if debug == True:
                st.text(f"Profil: {chosenProfile}")
                st.text(f"Profil Oberfläche: {materialSelect[material][profile][chosenProfile][0]}cm²")

            #Gebe das gewählte Profil und das Sigma weiter
            return chosenProfile, sigma_rd
        
    #Wenn kein Querschnitt gefunden werden kann, drucke Warnmeldung
    else:
        st.markdown(f'<font color="red">Es gibt keinen passenden {profile} Querschnitt, der den Spannungstest besteht.</font>',
                    unsafe_allow_html=True)
        return False

#Definiere Funktion zum iterativen Prüfen eines Querschnittes 
def check_bend(material, min_i, A, maxForce, sigma_rd):

    #Berechne Schlankheit des aktuellen Bauteils
    lambdaCalc = (trussWidth/fieldNumber)*100/min_i

    #Iteriere durch alle Lambdas und ihre k-Werte
    for lmbda, k in lambda_values[material].items():
        #Wenn ein Lambda der Liste dem berechneten lambdaCalc entspricht dann:
        if lmbda > lambdaCalc:
            
            #Berechne maximal tragbare Spannung
            check = sigma_rd * k
        
            #Wenn bestehende Spannung geringer ist als maximal tragbare Spannung:
            if check > (-maxForce*1.4)/A:  # sigma*k > Nd/A
                # "-"maxForce weil Druckkraft aus Ritterschnitt negativ herauskommt
                math_expression = r"\sigma_{Rd} \cdot k > \frac{{Nd}}{{A}}"
                math_expression2 = f"{check:.2f} > {((-maxForce*1.4)/A):.2f}"

                #Zeichne LaTeX Berechnung für Knicknachweis
                with st.expander("Knicknachweis"):
                    st.text(f"A = {A} cm²")
                    st.text(f"k = {k}\nbei λ = {int(lambdaCalc)}")
                    
                    st.latex(math_expression)
                    st.latex(math_expression2)
                
                #Debug Anzeige
                if debug == True:
                    st.text(f"Lambda: {lambdaCalc}")
                    st.text(f"k = {k}")
                
                #Gebe Boolean "True" aus
                return True

            #Wenn kein Querschnitt den Nachweis erfüllt:
            else:
                #Gebe Boolean "False" aus
                return False

#Definiere Funktion um bemessenes Profil zu präsentieren
def profile_success(material, profile, chosenProfile, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck):

    #Ergänze LaTeX Berechnungen mit Ausnutzungsgrad
    with stress_latex:
        A_gew = r"A_{gew}"
        math_expression = f"{A_gew}({chosenProfile}) = {materialSelect[material][profile][chosenProfile][0]:.2f} cm²"
        st.latex(math_expression)
    with stress_einheiten:
        st.text(f"σ = {sigma_rd} kN/cm²\nη = {((((abs(maxForce)*1.4)/materialSelect[material][profile][chosenProfile][0]) / sigma_rd) * 100):.2f} %")
        st.text(f"Nd = Nmax * 1.4 \nNd = {(abs(maxForce)*1.4):.2f} kN")

    #große Darstellung des nachgewiesenen Profils
    st.title(f'{chosenProfile} {profile}')       
    #kleiner Hinweis dass Nachweise erfüllt wurden         
    st.markdown(f'<span style="color: green;">Der Querschnitt **{chosenProfile}** in **{material} {profile}** erfüllt die erforderlichen Nachweise!</font>',
                unsafe_allow_html=True)
    
    #Erzeugung des Suchlinks
    searchTerm = f"{chosenProfile} {profile} Profil Maße Tabelle" #Erstelle Suchquery für Querschnitt
    searchTerm_noSpaces = searchTerm.replace(" ", "+")  #Ersetze Leerzeichen durch "+"
    st.link_button(f"Kennwerte zu {chosenProfile} {profile}", url=f"https://www.google.com/search?q={searchTerm_noSpaces}", use_container_width=True)

    #Analyse für Bauteilliste
    analyze_truss(strutToCheck, material, profile, chosenProfile)

#Definiere Funktion um Knicknachweis durchzuführen
def bend_verification(material, profile, chosenProfile, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck):
    
    #Iterativer Knicknachweis
    if maxForce < 0:    #Wenn Druckkraft vorliegt, dann Knicknachweis führen
        for profil, values in materialSelect[material][profile].items():
            #Beginne Prüfung ab dem Querschnitt der Spannungsnachweis erfüllt hat
            if extract_numerical_part(profil) >= extract_numerical_part(chosenProfile):
                
                #Debug Anzeige
                if debug == True:
                    st.text(f"Teste Profil: {profil}")

                min_i = values[1]
                A = values[0]

                #Ausführung Knicknachweis
                if check_bend(material, min_i, A, maxForce, sigma_rd) == True:

                    #Wenn Knicknachweis erfüllt ist (=True), zeige Ergebnis
                    profile_success(material, profile, profil, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck)

                    #Gebe bestandenen Querschnitt weiter
                    return chosenProfile
                
        #Wenn kein Querschnitt den Nachweis erfüllt:
        else:
            st.markdown(f'<font color="red">Es gibt keinen passenden {profile} Querschnitt, der den Knicknachweis erfüllt.</font>', unsafe_allow_html=True)

    #Wenn keine Druckkraft vorliegt (=Zugkraft) dann ergibt der Spannungsnachweis den Querschnitt
    else:
        with st.expander("Knicknachweis"):
            st.markdown(f":black[**Bei Zugkräften erfolgt kein Knicknachweis.**]")

        #Zeige Ergebnis
        profile_success(material, profile, chosenProfile, maxForce, sigma_rd, stress_latex, stress_einheiten, strutToCheck)

#Definiere Funktion um Bauteilliste zu bilden
def create_bauteilliste():
    
    #Baue Struktur für Bauteilliste
    bauteil_col_1, bauteil_col_2 = st.columns([0.7, 0.3], gap="medium")

    #Erstelle Bauteilliste
    with bauteil_col_1:
        #Transformiere Dictionary aus analyze_truss() in einfache Liste
        flat_data = [{"Position": element, **attributes} for element, attributes in struts_all_combined.items()]

        #Wandle Daten in Pandas Format um
        df = pd.DataFrame(flat_data)

        #Wenn Liste nicht leer ist:
        if len(df) > 0:
            #Erzeuge Tabelle aus den eingetragenen Werten (Ein paar sind versteckt)
            st.dataframe(df, column_order=("Position", "Anzahl", "Länge", "Länge gesamt", "Profil", "Volumen"),
                         use_container_width=True, hide_index=True, column_config={
                "Anzahl": st.column_config.NumberColumn(
                    format="%d x",
                    width="small"
                ),
                "Länge": st.column_config.NumberColumn(
                    format="%.2f m"
                ),
                "Länge gesamt": st.column_config.NumberColumn(
                    format="%.2f m"
                ),
                "Volumen": st.column_config.NumberColumn(
                    format="%.2f m³"
                )
            })

        #Wenn Liste leer ist:
        else:
            st.markdown(f"Es gibt **kein Profil**, welches die Nachweise erfüllt.")

    #Erstelle Gewichtstabelle
    with bauteil_col_2:

        #Werte zusammenrechnen, die demselben "Material" angehören
        try:
            total_volumes = df.groupby("Material")["Volumen"].sum()
            total_weight = df.groupby("Material")["Gewicht"].sum()

            #Dataframes zusammenführen
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
            st.markdown(f"Zur Überprüfung wird empfohlen, eine **Eigenlast** von mindestens **{((df['Gewicht'].sum()/100)/(trussDistance*trussWidth)):.2f} kN/m²** auf das System aufzulegen.")
        
        #Zeichne leeren container falls keine Bauteilliste erstellt werden kann.
        except KeyError:
            st.write("")

    #Drucke die Anzahl an Knoten
    nodesNr = number_of_nodes(trussType)
    st.markdown(f"Es werden **{nodesNr} Knoten** konstruiert.")




#Code der Streamlit App, um alle Funktionen anzuwenden
def main():

    with col2:
        #Zeichne LEF
        draw_LEF()
    with col4:
        #Zeichne Fachwerk
        if trussType == "Strebenfachwerk":
            draw_truss_strebe()
        if trussType == "Parallelträger":
            draw_truss_parallel(strebenParallel)

    #Berechnung der Stabkräfte
    with obergurtColumn:
        strutToCheck = "Obergurt"
        #maxForce als maximale Last, die sich aus dem calc() ergibt
        OG_maxForce = calc(trussType, strutToCheck)
    with obergurtColumn:
        try:
            OG_chosenProfile, OG_sigma_rd = stress_verification(OG_material, OG_profile, OG_maxForce, OG_stress_latex)
            bend_verification(OG_material, OG_profile, OG_chosenProfile, OG_maxForce, OG_sigma_rd, OG_stress_latex, OG_stress_einheiten, strutToCheck)
        except TypeError as e:
            st.text("")

    with strebenColumn:
        strutToCheck = "Streben"
        ST_maxForce = calc(trussType, strutToCheck)
        try:
            ST_chosenProfile, ST_sigma_rd = stress_verification(ST_material, ST_profile, ST_maxForce, ST_stress_latex)
            bend_verification(ST_material, ST_profile, ST_chosenProfile, ST_maxForce, ST_sigma_rd, ST_stress_latex, ST_stress_einheiten, strutToCheck)
        except TypeError as e:
            st.text("")

    with untergurtColumn:
        strutToCheck = "Untergurt"
        UG_maxForce = calc(trussType, strutToCheck, print_forces=True)
        try:
            UG_chosenProfile, UG_sigma_rd = stress_verification(UG_material, UG_profile, UG_maxForce, UG_stress_latex)
            bend_verification(UG_material, UG_profile, UG_chosenProfile, UG_maxForce, UG_sigma_rd, UG_stress_latex, UG_stress_einheiten, strutToCheck)
        except TypeError as e:
            st.text("")

    #Erstelle Bauteilliste
    with bauteilExpander:
        create_bauteilliste()


#Teste ob Script als Hauptprogramm läuft und kein Modul ist
if __name__ == "__main__":
    main()
