# src/rag_pipeline.py
from typing import Tuple, Optional, Dict, Any, List
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.llms import HuggingFaceHub
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.settings import get_settings, ERROR_MESSAGES
import logging
import json

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Rest of the RAGPipeline class implementation remains the same
class RAGPipeline:
    def __init__(self):
        self.settings = get_settings()
        self.setup_logging()
        self.initialize_db()
        self.initialize_model()
    
    def setup_logging(self):
    # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/rag_pipeline.log'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_db(self):
        try:
            self.client = chromadb.Client(
                ChromaSettings(
                    anonymized_telemetry=False,
                    is_persistent=False  # Use in-memory storage instead of SQLite
                )
            )
            
            # Use ChromaDB's built-in sentence-transformers embedding function
            sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.settings.EMBEDDING_MODEL
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.settings.COLLECTION_NAME,
                embedding_function=sentence_transformer_ef,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize collection with questions if empty
            if self.collection.count() == 0:
                self._load_initial_questions()
                
            self.logger.info("ChromaDB initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
            
            # Use ChromaDB's built-in sentence-transformers embedding function
            sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.settings.EMBEDDING_MODEL
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.settings.COLLECTION_NAME,
                embedding_function=sentence_transformer_ef,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize collection with questions if empty
            if self.collection.count() == 0:
                self._load_initial_questions()
                
            self.logger.info("ChromaDB initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def _load_initial_questions(self):
        """Load initial questions from question bank into ChromaDB."""
        from data.question_bank import QUESTION_BANK
        
        documents = []
        metadatas = []
        ids = []
        id_counter = 0
        
        for role, complexities in QUESTION_BANK.items():
            for complexity, questions in complexities.items():
                for question, answer in questions:
                    documents.append(question)
                    metadatas.append({
                        "role": role,
                        "complexity": complexity,
                        "correct_answer": answer
                    })
                    ids.append(f"q_{id_counter}")
                    id_counter += 1
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        self.logger.info(f"Loaded {len(documents)} questions into ChromaDB")
    
    def initialize_model(self):
        try:
            if self.settings.USE_GEMINI and self.settings.GOOGLE_API_KEY:
                self.llm = GoogleGenerativeAI(
                    model=self.settings.GEMINI_MODEL,
                    google_api_key=self.settings.GOOGLE_API_KEY
                )
            else:
                self.llm = HuggingFaceHub(
                    repo_id=self.settings.HUGGINGFACE_MODEL,
                    huggingface_api_key=self.settings.HUGGINGFACE_API_KEY
                )
            self.logger.info(f"Model initialized: {'Gemini' if self.settings.USE_GEMINI else 'HuggingFace'}")
        except Exception as e:
            self.logger.error(f"Error initializing LLM: {str(e)}")
            self.llm = None
    
    def get_question(self, role: str, complexity: float) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        try:
            # Convert complexity to integer since question bank uses integer keys
            complexity_level = int(complexity)
            
            # Direct lookup from question bank instead of using ChromaDB query
            from data.question_bank import QUESTION_BANK
            
            if role in QUESTION_BANK and complexity_level in QUESTION_BANK[role]:
                # Get questions for this role and complexity
                questions = QUESTION_BANK[role][complexity_level]
                
                # If there are questions available, return a random one
                if questions:
                    import random
                    question, answer = random.choice(questions)
                    metadata = {
                        "role": role,
                        "complexity": complexity_level,
                        "correct_answer": answer
                    }
                    return question, metadata
            
            self.logger.warning(f"No questions found for role: {role}, complexity: {complexity_level}")
            return None, None
                
        except Exception as e:
            self.logger.error(f"Error getting question: {str(e)}")
            return None, None
    
    def evaluate_answer(self, question: str, answer: str, correct_answer: str) -> Tuple[str, float, Optional[str]]:
        try:
            if not answer.strip():
                return "Please provide an answer.", 0.0, None

            prompt = f"""
            Question: {question}
            Correct Answer: {correct_answer}
            User Answer: {answer}
            
            Evaluate the user's answer and provide:
            1. A score between 0 and 1 based on accuracy
            2. Detailed, constructive feedback explaining what was correct and what could be improved
            3. A relevant follow-up question if the answer shows partial understanding (score between 0.3 and 0.7)
            
            Respond in this exact JSON format:
            {{
                "score": <float between 0 and 1>,
                "feedback": "<detailed feedback>",
                "follow_up": "<follow-up question or null>"
            }}
            """
            
            response = self.llm.predict(prompt)
            
            try:
                eval_data = json.loads(response)
                return (
                    eval_data["feedback"],
                    float(eval_data["score"]),
                    eval_data.get("follow_up")
                )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                self.logger.error(f"Error parsing LLM response: {str(e)}")
                return (
                    "Your answer has been recorded, but there was an error in generating detailed feedback. Please continue with the next question.",
                    0.5,  # Neutral score when evaluation fails
                    None
                )
                    
        except Exception as e:
            self.logger.error(f"Error evaluating answer: {str(e)}")
            return (
                "There was an error evaluating your answer. Please try again.",
                0.0,
                None
            )
