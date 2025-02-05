from pathlib import Path
from document_loader import DocumentLoader
from context_shortening import Retrieval
from form_filling import SequentialFormFiller
from graph_builder import GraphBuilder
from model_init import initialize_llm
from metadata_schemas.disease_theory_schema import DiseaseTheory
import outlines

class DiseaseTheoryPipeline:
    """Pipeline for extracting disease theories from documents"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        
        # Initialize retriever
        self.retriever = Retrieval(
            chunk_info_to_compare="keybert",
            field_info_to_compare="description",
            include_choice_every=1,
            embedding_model_id="all-MiniLM-L6-v2",
            n_keywords=5,
            top_k=5,
            chunk_size=200,
            chunk_overlap=50,
            pydantic_form=DiseaseTheory
        )
        
        # Initialize LLM and form filler
        llm = initialize_llm()
        self.form_filler = SequentialFormFiller(
            outlines_llm=llm,
            outlines_sampler=outlines.samplers.GreedySampler(),
            pydantic_form=DiseaseTheory
        )
        
        # Initialize graph builder
        self.graph_builder = GraphBuilder()
        
    def process_document(self, file_path: str):
        """Process a single document through the pipeline"""
        if self.verbose:
            print("\n=== Starting Document Processing ===")
        
        # Load document
        document = DocumentLoader.load_xml(file_path)
        if not document:
            return False
            
        if self.verbose:
            print(f"\nLoaded document: {Path(file_path).name}")
            
        # Set document for retrieval
        self.retriever.set_document(document)
        
        # Extract information using form filler
        filled_form = self.form_filler.forward(self.retriever)
        
        # Build knowledge graph
        self.graph_builder.process_theory(filled_form, Path(file_path).stem)
        
        return filled_form

    def process_text(self, text: str):
        """Process raw text through the pipeline"""
        if self.verbose:
            print("\n=== Starting Text Processing ===")
            
        # Set text for retrieval
        self.retriever.set_document(text)
        
        # Extract information using form filler
        filled_form = self.form_filler.forward(self.retriever)
        
        return filled_form