from neo4j import GraphDatabase
from typing import Dict, Any
from pathlib import Path
import logging
from pydantic import BaseModel

class GraphBuilder:
    """Builds and maintains a Neo4j knowledge graph of disease theories"""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="upcast-llm"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
        
    def process_theory(self, theory: BaseModel, source_id: str):
        """Process extracted disease theory into graph"""
        with self.driver.session() as session:
            # Convert Pydantic model to dict
            theory_dict = theory.model_dump()
            
            # Create or get disease node
            disease_name = theory_dict.get("disease_name", "").strip()
            if not disease_name:
                logging.warning(f"No disease name found in theory from {source_id}")
                return
                
            session.execute_write(self._create_disease_node, disease_name, theory_dict)
            
            # Process multi-value fields
            multi_value_fields = {
                "symptoms": ("Symptom", "HAS_SYMPTOM"),
                "risk_factors": ("RiskFactor", "HAS_RISK_FACTOR"),
                "treatment_approaches": ("Treatment", "HAS_TREATMENT"),
                "affected_body_parts": ("BodyPart", "AFFECTS_BODY_PART")
            }
            
            for field, (node_label, relationship) in multi_value_fields.items():
                if field in theory_dict and theory_dict[field]:
                    values = [v.strip() for v in theory_dict[field].split(",")]
                    for value in values:
                        if value:
                            session.execute_write(
                                self._create_relationship,
                                disease_name,
                                value,
                                node_label,
                                relationship
                            )
    
    def _create_disease_node(self, tx, disease_name: str, properties: Dict):
        """Create or update disease node with basic properties"""
        query = """
        MERGE (d:Disease {name: $name})
        SET d.type = $type,
            d.progression_stage = $stage,
            d.prognosis = $prognosis
        RETURN d
        """
        
        tx.run(query, {
            "name": disease_name,
            "type": properties.get("disease_type", ""),
            "stage": properties.get("progression_stage", ""),
            "prognosis": properties.get("prognosis", "")
        })
    
    def _create_relationship(self, tx, disease_name: str, target_value: str, 
                           target_label: str, relationship_type: str):
        """Create relationship between disease and a property node"""
        query = f"""
        MERGE (d:Disease {{name: $disease_name}})
        MERGE (t:{target_label} {{name: $target_value}})
        MERGE (d)-[r:{relationship_type}]->(t)
        RETURN d, r, t
        """
        
        tx.run(query, {
            "disease_name": disease_name,
            "target_value": target_value
        })
    
    def clear_graph(self):
        """Clear all nodes and relationships from graph"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
