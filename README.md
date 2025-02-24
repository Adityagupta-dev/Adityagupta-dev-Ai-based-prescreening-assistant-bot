# AI-Based Pre-Screening Assistant Bot

## Overview
The **AI-Based Pre-Screening Assistant Bot** is an AI-driven technical interview assistant designed to evaluate candidates based on predefined questions and adaptive scoring. It leverages **Retrieval-Augmented Generation (RAG)** for intelligent question selection and evaluation.

## Features
- **Adaptive Interviewing**: Questions adjust based on candidate responses.
- **Real-time Feedback**: Immediate scoring and evaluation.
- **Follow-up Questioning**: Additional queries for partially correct answers.
- **Timer-Based Assessment**: Time-bound questions to simulate real interviews.
- **Automated Report Generation**: Summary reports for recruiters.
- **Email Notification**: Sends final results to recruiters.
- **Streamlit UI**: Interactive and intuitive user interface.

## Tech Stack
- **Programming Language**: Python
- **Framework**: Streamlit
- **Machine Learning**: RAGPipeline
- **Database**: JSON-based session storage
- **Email Notifications**: SMTP (Gmail)

## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- pip

### Clone the Repository
```bash
git clone https://github.com/Adityagupta-dev/Ai-based-prescreening-assistant-bot.git
cd Ai-based-prescreening-assistant-bot
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
streamlit run ui.py
```

## Usage
1. Launch the Streamlit app.
2. Enter candidate details and select the role.
3. Answer technical questions in a timed session.
4. Receive real-time feedback and follow-up questions if applicable.
5. Generate and send interview reports to recruiters.

## Future Improvements
- Integration with **FAISS / Pinecone** for enhanced vector search.
- Improved NLP for better question understanding.
- Deployment using **Docker & Cloud Platforms**.
- Expansion of question database for broader assessments.

## Contributions
Contributions are welcome! Feel free to **fork the repository**, make improvements, and submit a pull request.

## License
This project is licensed under the **MIT License**.

## Contact
For inquiries or collaboration, reach out to [**Aditya Gupta**](https://www.linkedin.com/in/aditya-gupta-062478250/) via LinkedIn.

---
*Star the repo if you find it useful!* ⭐

