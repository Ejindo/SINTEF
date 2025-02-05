import streamlit as st
from disease_theory_pipeline import DiseaseTheoryPipeline
from pathlib import Path
import tempfile
from pyvis.network import Network
import streamlit.components.v1 as components
from neo4j import GraphDatabase
import networkx as nx

# Custom CSS for dark theme and styling
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    
    .header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: #2D2D2D;
        border-bottom: 1px solid #333;
        z-index: 999999;
    }
    
    .header h2 {
        font-size: 2rem;
        margin: 0;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-links a {
        color: white;
        text-decoration: none;
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .nav-links a:hover {
        color: #5A5AD2;
        background: rgba(90, 90, 210, 0.1);
        border-radius: 4px;
    }
    
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #2D2D2D;
        padding: 1rem;
        text-align: center;
        border-top: 1px solid #333;
        z-index: 999999;
    }
    
    .main-content {
        margin-top: 5rem;
        margin-bottom: 5rem;
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header (Navbar)
st.markdown("""
<div class="header">
    <h2>SINTEF Disease Theory Extractor</h2>
    <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">Discover</a>
        <a href="#">Diseases</a>
        <a href="#">Support</a>
    </div>
</div>
""", unsafe_allow_html=True)

def init_pipeline():
    """Initialize pipeline if not in session state"""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = DiseaseTheoryPipeline(verbose=True)

def get_graph_data():
    """Fetch and visualize graph data from Neo4j"""
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "upcast-llm"))
    
    with driver.session() as session:
        result = session.run("""
            MATCH (d:Disease)-[r]->(n)
            RETURN d, r, n
        """)
        
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
        
        # Track added nodes and edges
        added_nodes = set()
        edges = []
        
        # Color scheme
        color_map = {
            "Disease": "#5A5AD2",
            "Symptom": "#FFB6C1",
            "RiskFactor": "#90EE90",
            "Treatment": "#FFB347",
            "BodyPart": "#DDA0DD"
        }
        
        # Add nodes and edges
        for record in result:
            disease = record["d"]
            target = record["n"]
            
            if disease["name"] not in added_nodes:
                net.add_node(disease["name"],
                           title=disease["name"],
                           label=disease["name"],
                           color=color_map["Disease"],
                           size=25)
                added_nodes.add(disease["name"])
            
            if target and target["name"] not in added_nodes:
                node_label = next(iter(target.labels))
                net.add_node(target["name"],
                           title=target["name"],
                           label=target["name"],
                           color=color_map.get(node_label, "#FFFFFF"),
                           size=15)
                added_nodes.add(target["name"])
            
            if target:
                net.add_edge(disease["name"], 
                           target["name"],
                           title=type(record["r"]).__name__,
                           label="",  # Empty label by default
                           color="#000000",
                           width=0.5,
                           arrows="to")

        # Set options
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08,
                    "damping": 0.4,
                    "avoidOverlap": 0.5
                },
                "solver": "forceAtlas2Based",
                "stabilization": {
                    "enabled": true,
                    "iterations": 1000
                }
            },
            "edges": {
                "smooth": {
                    "type": "continuous"
                },
                "font": {
                    "size": 0,
                    "strokeWidth": 0
                }
            },
            "interaction": {
                "hover": true,
                "hideEdgesOnDrag": false,
                "navigationButtons": false,
                "keyboard": false,
                "zoomView": true
            }
        }
        """)

        # Add custom JavaScript for edge label visibility on selection
        net.html += """
        <script>
        network.on("selectNode", function(params) {
            var selectedNode = params.nodes[0];
            if (selectedNode) {
                var connectedEdges = network.getConnectedEdges(selectedNode);
                edges.update(connectedEdges.map(function(edgeId) {
                    var edge = edges.get(edgeId);
                    edge.label = edge.title;
                    return edge;
                }));
            }
        });

        network.on("deselectNode", function(params) {
            edges.update(edges.get().map(function(edge) {
                edge.label = "";
                return edge;
            }));
        });
        </script>
        """
        
        net.save_graph("network.html")
        with open("network.html", "r", encoding="utf-8") as f:
            html_string = f.read()
        
        return html_string

def display_results(filled_form):
    """Display extracted disease theory information"""
    if filled_form:
        st.subheader("Extracted Disease Information")
        for field, value in filled_form.dict().items():
            st.write(f"**{field.replace('_', ' ').title()}:** {value}")
        
        # Display graph
        st.subheader("Knowledge Graph Visualization")
        html = get_graph_data()
        components.html(html, height=600)

def main():
    # Add main content div
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.title("Disease Theory Extractor")
    
    # Initialize pipeline
    init_pipeline()
    
    # Input selection
    input_type = st.radio("Select input type:", ["Text", "Document Upload"])
    
    if input_type == "Text":
        text_input = st.text_area("Enter medical text:", height=200)
        if st.button("Process Text") and text_input:
            with st.spinner("Processing text..."):
                results = st.session_state.pipeline.process_text(text_input)
                # Add to graph
                st.session_state.pipeline.graph_builder.process_theory(results, "text_input")
                display_results(results)
    
    else:
        uploaded_file = st.file_uploader("Upload document (XML)", type=['xml'])
        if uploaded_file and st.button("Process Document"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            with st.spinner("Processing document..."):
                results = st.session_state.pipeline.process_document(tmp_path)
                # Add to graph (if not already added by process_document)
                if results:
                    st.session_state.pipeline.graph_builder.process_theory(results, uploaded_file.name)
                display_results(results)
            
            # Clean up temp file
            Path(tmp_path).unlink()
    
    # Add Neo4j visualization section
    st.subheader("Knowledge Graph")
    st.markdown("""
    Access the Neo4j browser at [localhost:7474](http://localhost:7474) to view the complete knowledge graph.
    
    Sample query to explore:
    ```cypher
    MATCH (d:Disease)-[r]->(n)
    RETURN d, r, n
    ```
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>&copy; 2025 SINTEF. All rights reserved.</p>
    <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 