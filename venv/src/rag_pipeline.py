from typing import Tuple, Optional, Dict, Any, List
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.llms import HuggingFaceHub
import numpy as np
import sys
import os
import logging
import json
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.settings import get_settings, ERROR_MESSAGES

class RAGPipeline:
    def __init__(self):
        self.settings = get_settings()
        self.setup_logging()
        self.initialize_db()
        self.initialize_model()
    
    def setup_logging(self):
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/rag_pipeline.log'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_db(self):
        try:
            # Initialize sentence transformer
            self.embedder = SentenceTransformer(self.settings.EMBEDDING_MODEL)
            
            # Initialize or load index
            if not self._index_exists():
                self._create_initial_index()
            else:
                self._load_index()
            
            self.logger.info("Vector store initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def _index_exists(self) -> bool:
        """Check if index files exist"""
        return (os.path.exists("vector_store/knn_index.pkl") and 
                os.path.exists("vector_store/embeddings.npy") and 
                os.path.exists("vector_store/metadata.pkl"))
    
    def _create_initial_index(self):
        """Create initial index from question bank"""
        from data.question_bank import QUESTION_BANK
        
        os.makedirs("vector_store", exist_ok=True)
        texts = []
        self.metadata_list = []
        
        for role, complexities in QUESTION_BANK.items():
            for complexity, questions in complexities.items():
                for question, answer in questions:
                    texts.append(question)
                    self.metadata_list.append({
                        "role": role,
                        "complexity": complexity,
                        "correct_answer": answer
                    })
        
        # Create embeddings
        self.embeddings = self.embedder.encode(texts)
        
        # Initialize and fit NearestNeighbors
        self.knn = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.knn.fit(self.embeddings)
        
        # Save everything
        with open("vector_store/knn_index.pkl", "wb") as f:
            pickle.dump(self.knn, f)
        np.save("vector_store/embeddings.npy", self.embeddings)
        with open("vector_store/metadata.pkl", "wb") as f:
            pickle.dump(self.metadata_list, f)
            
        self.logger.info(f"Created index with {len(texts)} questions")
    
    def _load_index(self):
        """Load existing index"""
        with open("vector_store/knn_index.pkl", "rb") as f:
            self.knn = pickle.load(f)
        self.embeddings = np.load("vector_store/embeddings.npy")
        with open("vector_store/metadata.pkl", "rb") as f:
            self.metadata_list = pickle.load(f)
    
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
            complexity_level = int(complexity)
            
            # Direct lookup from question bank for simplicity and reliability
            from data.question_bank import QUESTION_BANK
            
            if role in QUESTION_BANK and complexity_level in QUESTION_BANK[role]:
                questions = QUESTION_BANK[role][complexity_level]
                
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
                    0.5,
                    None
                )
                    
        except Exception as e:
            self.logger.error(f"Error evaluating answer: {str(e)}")
            return (
                "There was an error evaluating your answer. Please try again.",
                0.0,
                None
            )
