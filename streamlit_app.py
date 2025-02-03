import streamlit as st

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx

# Custom CSS for dark theme and styling
st.markdown("""
    <style>
    body {
        background-color: black;
        color: white;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background: black;
        color: white;
    }
    .nav-links {
        display: flex;
        gap: 20px;
    }
    .nav-links a {
        color: white;
        text-decoration: none;
    }
    .footer {
        background: black;
        padding: 20px;
        text-align: center;
        color: white;
    }
    .footer a {
        color: white;
        text-decoration: none;
        margin: 0 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Header (Navbar)
st.markdown("""
<div class="header">
    <h2>SINTEF</h2>
    <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">Discover</a>
        <a href="#">Diseases</a>
        <a href="#">Support</a>
        <a href="#">Login</a>
        <button style="background-color: #5A5AD2; color: white; border: none; padding: 5px 15px; border-radius: 10px;">Sign Up</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Network Graph Visualization
st.subheader("Network Visualization of Diseases and Habits")

# Create Network Graph
G = nx.Graph()
nodes = ["Habits MOD", "Smoking", "Exercise", "Diet", "Stress", "Alcohol", "Mental Health"]
edges = [("Habits MOD", node) for node in nodes]

G.add_nodes_from(nodes)
G.add_edges_from(edges)

# Pyvis Network
net = Network(height="400px", width="100%", bgcolor="#000000", font_color="white")
for node in G.nodes():
    net.add_node(node, label=node, color="#5A5AD2" if node == "Habits MOD" else "#FFFFFF")

for edge in G.edges():
    net.add_edge(edge[0], edge[1], color="#5A5AD2")

net.save_graph("network.html")

# Display Network Graph in Streamlit
HtmlFile = open("network.html", "r", encoding="utf-8")
components.html(HtmlFile.read(), height=450)

# Footer
st.markdown("""
<div class="footer">
    <p>&copy; 2025 SINTEF. All rights reserved.</p>
    <a href="#">Facebook</a> | <a href="#">Twitter</a> | <a href="#">Instagram</a>
</div>
""", unsafe_allow_html=True)

