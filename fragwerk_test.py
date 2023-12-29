import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from itertools import zip_longest
import math

st.set_page_config(
    page_title="Fachwerkrechner",
    layout="wide"
)

#svg_path = r"C:\Users\DerSergeant\Desktop\fragwerk\fragwerk.png"

st.image("https://raw.githubusercontent.com/oelimar/images/main/fragwerk.png", width=300)
st.title("dein Fachwerkrechner")
debug = st.toggle("Debug Mode")
st.title("")

trussOptions = [
    "Strebenfachwerk",
    "Dreiecksfachwerk",
    "Polonceau Träger"
]

roofOptions = {
    "Schwer [1]" : 1,
    "Mittelschwer [0.5]" : 0.5,
    "Leicht [0.3]" : 0.3
}

roofAdditives = {
    "intensive Dachbegrünung" : 12.8,
    "extensive Dachbegrünung" : 1.5,
    "Photovoltaik" : 0.15
}

materialSelect = {
    "Holz": {
        "KVH Kantholz" : {
            "10/10" : (100, 2.89),    # Querschnitt 10/10 : (Oberfläche A, min i)
            "12/12" : (144, 3.46),
            "14/14" : (196, 4.04),
            "16/16" : (256, 4.62),
            "18/18" : (324, 5.20),
            "20/20" : (400, 5.77),
            "22/22" : (484, 6.35),
            "24/24" : (576, 6.93)
        },
        "KVH Rundholz" : {
            "8" : (50.3, 2.00),
            "9" : (63.6, 2.25),
            "10" : (78.5, 2.50),
            "11" : (95, 2.75),
            "12" : (113, 3.00),
            "13" : (133, 3.25),
            "14" : (154, 3.50),
            "15" : (177, 3.75),
            "16" : (201, 4.00),
            "17" : (227, 4.25),
            "18" : (254, 4.50),
            "19" : (284, 4.75),
            "20" : (314, 5.00),
            "21" : (346, 5.25),
            "22" : (380, 5.50),
            "23" : (415, 5.75),
            "24" : (452, 6.00),
            "25" : (491, 6.25),
            "26" : (531, 6.50),
            "28" : (616, 7.00),
            "30" : (707, 7.50),
            "32" : (804, 8.00),
            "35" : (962, 8.75),
            "38" : (1130, 9.50),
            "40" : (1260, 10.00),
            "50" : (1960, 12.50)
        }
    },
    "Stahl" : {
        "IPB" : {
            "100" : (21.2, 2.51),
            "120" : (25.3, 3.02),
            "140" : (31.4, 3.52),
            "160" : (38.8, 3.98),
            "180" : (45.3, 4.52),
            "200" : (54.8, 4.98)
        }
    }
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


with st.container():
    st.subheader("Lasteinzugsfeld", divider="red")
    col1, col2 = st.columns([0.4, 0.6], gap="large")

    with col1:
        #st.text("Eingabe LEF")
        snow_mapping = {
            1: 1.05,
            2: 2.06,
            3: 3.07
        }
        wind_mapping = {
            1: 0.5,
            2: 0.7,
            3: 0.9,
            4: 1.2
        }

        trussDistance = float(st.text_input("Träger Abstand [m]", value="5"))

        #with st.expander("Dachaufbau"):
        if 'roofAdditives' not in st.session_state:
            st.session_state.roofAdditives = roofAdditives
        

        roofType = st.selectbox("Dachaufbau [kN/m²]", placeholder="Wähle einen Dachaufbau", index=1, options=roofOptions.keys(), help="Wähle einen voreingestellten Dachaufbau für eine Lastannahme.\nÜber 'zusätzliche Lasten' können voreingestellte Elemente ausgewählt,\noder durch drücken des roten Knopfes eigene hinzugefügt werden.")
        roofAdded = st.multiselect("Zusätzliche Dachlasten", st.session_state.roofAdditives.keys(), placeholder="Wähle hier zusätzliche Lasten", label_visibility="collapsed")
        addVal = ""
        valVal = ""

        col1_1, col1_2, col1_3 = st.columns([0.1, 0.45, 0.45], gap="small")
        with col1_1:
            addButton = st.button("", type="primary")
        with col1_2:
            customAdditive = st.text_input("Bezeichnung", label_visibility="collapsed", placeholder="Bezeichnung", value=addVal)
        with col1_3:
            customValue = st.text_input("Last",  label_visibility="collapsed", placeholder="Last in kN/m²", value=valVal)

        if addButton:
            try:
                original_string = customValue
                #substring_to_remove
                float_value = float(customValue)
                st.session_state.roofAdditives[customAdditive] = float_value
                addVal = ""
                valVal = ""
                st.experimental_rerun()
                    
            except ValueError:
                st.markdown(":red[Last unzulässig. Bitte nur Wert in [kN/m²] eingeben]")
            #return roofAdditives

        with st.expander("bewegliche Lasten"):

            col1_4, col1_5 = st.columns([0.5, 0.5], gap="small")
            with col1_4:
                windZone = st.number_input("Windlastzone", help="Wähle Anhand der Lage auf der Karte eine der 4 Windlastzonen", step=1, value=2, min_value=1, max_value=4)
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShbi3oQsR2FrAbMAkfjh-Fw-ODeuYsS9NZrAojIXYJCWXZsK65qCyQejR-QJaFzEmheEY&usqp=CAU", caption="Windlastzonen in DE")

            with col1_5:
                snowZone = st.number_input("Schneelastzone", help="Wähle Anhand der Lage auf der Karte eine der 3 Schneelastzonen", step=1, value=3, min_value=1, max_value=3)
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4A-8ZgmAVEg-fwtBN1ndVuCaCfbG3p5VOpwya0ZXY7NljUrRNvYoH4Hng9DVW0TriyDM&usqp=CAU", caption="Schneelastzonen in DE")

        snowForce = snow_mapping[snowZone] * 0.8 # berechnung wie in Tabellenbuch
        windForce = wind_mapping[windZone] * 0.2
        roofForce = roofOptions[roofType]

        for force in roofAdded:
            roofForce += st.session_state.roofAdditives[force]

        qTotal = snowForce + windForce + roofForce

    #with col2:
        #st.text("GRAPH LEF")

with st.container():
    st.subheader("Fachwerk", divider="red")
    col3, col4 = st.columns([0.4, 0.6], gap="large")
    
    with col3:
        trussType = st.selectbox("Fachwerkart", placeholder="Wähle ein Fachwerk", options=trussOptions)
        trussWidth = float(st.text_input("Spannweite [m]", value="15"))
        trussHeight = float(st.text_input("Statische Höhe [m]", value=trussWidth/10))
        fieldNumber = int(st.number_input("Anzahl an Fächern", step=1, value=5, min_value=2, max_value=20))
        distanceNode = round(trussWidth / fieldNumber, 2)

with st.container():
    st.subheader("Querschnitt", divider="red")
    col5, col6 = st.columns([0.4, 0.6], gap="large")

    with col5:
        col5_1, col5_2 = st.columns([0.5, 0.5], gap="small")
        #st.text("Eingabe Querschnitt")

        # st.text(materialSelect.keys())
        with col5_1:
            material = st.selectbox("Material", placeholder="Wähle ein Material", options=materialSelect.keys())
            # st.text(material)
        with col5_2:
            profile = st.selectbox("Profil", placeholder="Wähle ein Profil", options=materialSelect[material].keys())

        if material == "Holz":
            sigma_rd = 1.3
        elif material == "Stahl":
            sigma_rd = 21.8
        else:
            st.markdown(":red[Zu dem Material ist keine Randspannung angegeben.]")

    with col6:
        st.text("GRAPH QUERSCHNITT")


def draw_truss():
    # Define truss nodes
    minNodeX = trussWidth / 5
    minNodeY = trussWidth / 5
    maxNode = minNodeY + trussHeight
    nrNodeLower = int(fieldNumber) 
    nrNodeUpper = int(fieldNumber) + 1

    qTotalField = qTotal * trussDistance

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

    edgeVar = 0

    while edgeVar < fieldNumber - 1: #extend the points that are used with every new field in the truss
        edgeExtend = [
            (1 + 2 * edgeVar, 3 + 2 * edgeVar),
            (3 + 2 * edgeVar, 4 + 2 * edgeVar),
            (4 + 2 * edgeVar, 2 + 2 * edgeVar),
            (2 + 2 * edgeVar, 3 + 2 * edgeVar)
        ]
        #st.text(edges)
        edges.extend(edgeExtend)
        edgeVar += 1


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




    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Calculate and display truss width and height
    #truss_width = np.max(nodes[:, 0]) - np.min(nodes[:, 0])
    #truss_height = np.max(nodes[:, 1]) - np.min(nodes[:, 1])

    # create Massband Gesamtlaenge
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

    # Draw LEF Force above Truss

    qNodes = [
        [minNodeX, minNodeY + trussHeight * 4/3],
        [minNodeX, minNodeY + 0.5 + trussHeight * 4/3],
        [minNodeX + trussWidth, minNodeY + 0.5 + trussHeight * 4/3],
        [minNodeX + trussWidth, minNodeY + trussHeight * 4/3]
    ]

    ax.fill([point[0] for point in qNodes], [point[1] for point in qNodes], color="white", facecolor="lightblue", hatch="|", alpha=0.7)
    ax.annotate(f"q = {float(qTotalField):.2f} kN/m", (minNodeX + trussWidth / 2, minNodeY + 0.5 + trussHeight * 4.5/3), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)

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

    # debug to check node generation
    
    if debug == True:

        st.text(f"Lower Nodes: {nodeLower}")
        st.text(f"Upper Nodes: {nodeUpper}")
        st.text(f"Corner Nodes: {nodeCorner}")
        st.text(f"Combined Nodes: {nodeArray}")

def draw_LEF():

    minNodeLEF = trussDistance / 5
    minNodeLEFy = 2

    edgesLEF = [
        (0, 1),
        (1, 2),
        (2, 3)
    ]

    nodesLEF = [
        [minNodeLEF, minNodeLEFy + 2.2],
        [minNodeLEF, minNodeLEFy + 5],
        [minNodeLEF + 3, minNodeLEFy + 3],
        [minNodeLEF + 3, minNodeLEFy]
    ]

    nodesForce = [
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
    
    LEF_graph0 = plt.Polygon(nodesForce[0], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.3)
    LEF_graph1 = plt.Polygon(nodesForce[1], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.7)
    LEF_graph2 = plt.Polygon(nodesForce[2], closed = True, edgecolor=None, facecolor="lightblue", alpha=0.3)

    #st.write(LEF_graph)
    #st.write(nodesForce[0])
    #LEF_graph = plt.Polygon(nodesForce, closed = True, edgecolor=None, facecolor="lightblue", alpha=0.5)

        # Create a figure
    fig, ax = plt.subplots()

    truss = 0
    while truss < 3:
        for edge in edgesLEF:
            #st.text(f"Current Edge: {edge}")
            start_node = [nodesLEF[edge[0]][0] + truss * trussDistance, nodesLEF[edge[0]][1]]
            #st.text(f"Start Node: {edge}")
            end_node = [nodesLEF[edge[1]][0] + truss * trussDistance, nodesLEF[edge[1]][1]]
            #st.text(f"End Node: {edge}")
            ax.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], 'r-', linewidth=2)        
        for node in nodesLEF:
            ax.plot(node[0] + truss * trussDistance, node[1], 'ko', markersize=5)
        truss += 1

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

    ax.set_aspect('equal', adjustable='datalim')

    # Add LEF on top
    ax.add_patch(LEF_graph0)
    ax.add_patch(LEF_graph1)
    ax.add_patch(LEF_graph2)


    ax.annotate(f"q = g + w + s\nq = {float(roofForce):.2f} kN/m² + {float(windForce):.2f} kN/m² + {float(snowForce):.2f} kN/m²\n\nq = {float(qTotal):.2f} kN/m²", ((2 * trussDistance + 2 * minNodeLEF + 3)/2, 2 * 4 + 2 * minNodeLEF- minNodeLEF), xytext=(0, 0), textcoords='offset points', ha='center', va='center', fontsize=8, annotation_clip=False)


    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Show the plot
    st.pyplot(fig, use_container_width=True)

    if debug == True:
        st.text(f"zusätzliche Lasten: {roofAdded}")
        st.text(f"Lasten: {st.session_state.roofAdditives}")


def calc_strebewerk():

    diagonalLength = math.sqrt((pow(distanceNode/2, 2)) + (pow(trussHeight, 2)))
    diagonalAlpha = math.asin(trussHeight/diagonalLength)
    qProd = 0
    qSum = 0
    qNum = []
    qCount = 1
    if math.ceil(fieldNumber/2) == 1:
        qTemp = (float((qTotal*trussDistance*trussWidth)/fieldNumber), float(qCount * (trussWidth/fieldNumber)))  # store Q Value and Q distance in array just for debugging purposes
        qNum.append(qTemp)
    else:
        while qCount < math.ceil(fieldNumber/2):    # draw forces exactly until the middle pole
            qTemp = (float((qTotal*trussDistance*trussWidth)/fieldNumber), float(qCount * (trussWidth/fieldNumber)))  # store Q Value and Q distance in array just for debugging purposes
            qNum.append(qTemp)
            qCount += 1

    # add all different qMomentums together
    for num in qNum:
        qProd += num[0] * num[1]
    for num in qNum:
        qSum += num[0]

    # calculate U force 
    maxForceU = ((((qTotal*trussDistance*trussWidth)/(2*fieldNumber)) * math.ceil(fieldNumber/2) * trussWidth/fieldNumber * -1) - qProd + (((qTotal*trussDistance*trussWidth)/2) * math.ceil(fieldNumber/2) * trussWidth/fieldNumber)) / trussHeight
    ForceDmiddle = (((qTotal*trussDistance*trussWidth)/(2*fieldNumber) + qSum - ((qTotal*trussDistance*trussWidth)/2)) / math.sin(diagonalAlpha))
    maxForceO = (-maxForceU - (math.cos(diagonalAlpha)*ForceDmiddle))

    global maxForce
    maxForce = maxForceO

    st.text(f"Maximale Zugkraft im Untergurt: {abs(maxForceU):.2f} kN")
    st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
    st.text(f"Maximale Druckkraft im Obergurt: {abs(maxForceO):.2f} kN")


    if debug == True:
            st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
            st.text(f"generiert bis Fach: {math.ceil(fieldNumber/2)}")
            st.text(f"Qs generiert: {len(qNum)}\nmit Werten: {qNum}\ninsgesamt Momente: {float(qProd):.2f}")
            # Mathematical expression in LaTeX format
            math_expression = r"\frac{5}{4} + \frac{\sqrt{a^2 + b^2}}{c}"

            # Display the mathematical expression using st.latex
            st.latex(math_expression)

    return maxForce

def extract_numerical_part(key):
    # This function extracts the numerical part from a string key
    # Example: "8" -> 8, "12/12" -> 12
    return int(key.split('/')[0]) if '/' in key else int(key)


def stress_verification(): # Spannungsnachweis zur Wahl des ersten Querschnitts
    
    global maxForce
    
    maxForce_d = -maxForce * 1.4
    
    areaCalc = maxForce_d/sigma_rd

    global chosenProfile

    if debug == True:
        with col5:
            st.text(f"benötigte Oberfläche: {areaCalc:.2f}cm²")
    
    for profil, values in materialSelect[material][profile].items():
        area = values[0]
        if area > areaCalc:
            chosenProfile = profil
            if debug == True:
                with col5:
                    st.text(f"Profil: {chosenProfile}")
                    st.text(f"Profil Oberfläche: {materialSelect[material][profile][chosenProfile][0]}cm²")
            return chosenProfile
    else:
        st.markdown(f'<font color="red">Es gibt keinen passenden {profile} Querschnitt, der den Spannungstest besteht.</font>', unsafe_allow_html=True)
        return False
    
    
    
    
    

def check_bend(min_i):

    global maxForce
    global chosenProfile

    lambdaCalc = (trussWidth/fieldNumber)*100/min_i

    for lmbda, k in lambda_values[material].items():
        if lmbda > lambdaCalc:

            check = sigma_rd * k
        
            if check > (-maxForce*1.4)/materialSelect[material][profile][chosenProfile][0]:  # sigma*k > Nd/A
        
                if debug == True:
                    st.text(f"Lambda: {lambdaCalc}")
                    st.text(f"k = {k}")
                    math_expression = f"sigma_r \\cdot k > \\frac{{Nd}}{{A}}"
                    math_expression2 = f"{check:.2f} > {(-maxForce*1.4)/materialSelect[material][profile][chosenProfile][0]:.2f}"

                    # Display the mathematical expression using st.latex
                    st.latex(math_expression)
                    st.latex(math_expression2)
                
                return True

            else:
                return False



def bend_verification():
    # iterativer Knicknachweis
    global chosenProfile

    for profil, values in materialSelect[material][profile].items():
        if extract_numerical_part(profil) >= extract_numerical_part(chosenProfile):
            if debug == True:
                st.text(f"{profil} ist größer als {chosenProfile}")
            min_i = values[1]
            if check_bend(min_i) == True:
                chosenProfile = profil
                st.title(f"{chosenProfile} {profile}")
                st.markdown(f'<font color="green">Der Querschnitt {chosenProfile} in {material} {profile} besteht den Knicktest!</font>', unsafe_allow_html=True)
                
                return chosenProfile
        #else:
            #st.text(f"{profil} ist nicht größer als {chosenProfile}")
    else:
        st.markdown(f'<font color="red">Es gibt keinen passenden {profile} Querschnitt, der den Knicktest besteht.</font>', unsafe_allow_html=True)
        #st.markdown(":red[Es gibt keinen passenden Querschnitt für]")






def main():

    with col2:
        draw_LEF()
    # Draw the truss
    with col4:
        draw_truss()
    with col6:
        calc_strebewerk()
    with col5:
        if stress_verification() != False:
            bend_verification()


if __name__ == "__main__":
    main()
