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

st.image("https://raw.githubusercontent.com/oelimar/images/main/fragwerk.png")
st.title("dein Fachwerkrechner")
debug = st.toggle("Debug Mode")
st.title("")

trussOptions = [
    "Strebenfachwerk",
    "Dreiecksfachwerk",
    "Polonceau Träger"
]

roofOptions = {
    "Schwer [1]": 1,
    "Mittelschwer [0.5]": 0.5,
    "Leicht [0.3]": 0.3
}

roofAdditives = {
    "intensive Dachbegrünung": 12.8,
    "extensive Dachbegrünung": 1.5,
    "Photovoltaik": 0.15
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
        col1_1, col1_2, col1_3 = st.columns([0.1, 0.45, 0.45], gap="small")
        with col1_1:
            addButton = st.button("", type="primary")
        with col1_2:
            customAdditive = st.text_input("Bezeichnung", label_visibility="collapsed", placeholder="Bezeichnung")
        with col1_3:
            customValue = st.text_input("Last",  label_visibility="collapsed", placeholder="Last in kN/m²")

        if addButton:
            try:
                original_string = customValue
                #substring_to_remove
                float_value = float(customValue)
                st.session_state.roofAdditives[customAdditive] = float_value
                customAdditive = ""
                customValue = ""
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

        snowForce = snow_mapping[snowZone] * 0.8
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
        trussHeight = float(st.text_input("Statische Höhe [m]", value="1.2"))
        trussWidth = float(st.text_input("Spannweite [m]", value="15"))
        fieldNumber = int(st.number_input("Anzahl an Fächern", step=1, value=5, min_value=2, max_value=20))
        distanceNode = round(trussWidth / fieldNumber, 2)

with st.container():
    st.subheader("Querschnitt", divider="red")
    col5, col6 = st.columns([0.4, 0.6], gap="large")

    with col5:
        st.text("Eingabe Querschnitt")
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

    st.text(f"Maximale Zugkraft im Untergurt: {abs(maxForceU):.2f} kN")
    st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
    st.text(f"Maximale Druckkraft im Obergurt: {abs(maxForceO):.2f} kN")


    if debug == True:
            st.text(f"Kraft im mittleren Diagonalstab: {abs(ForceDmiddle):.2f} kN")
            st.text(f"generiert bis Fach: {math.ceil(fieldNumber/2)}")
            st.text(f"Qs generiert: {len(qNum)}\nmit Werten: {qNum}\ninsgesamt Momente: {float(qProd):.2f}")


    

def main():

    with col2:
        draw_LEF()
    # Draw the truss
    with col4:
        draw_truss()
    with col6:
        calc_strebewerk()    

if __name__ == "__main__":
    main()
