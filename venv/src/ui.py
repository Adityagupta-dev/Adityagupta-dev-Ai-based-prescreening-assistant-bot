import streamlit as st
from rag_pipeline import RAGPipeline
from config.settings import get_settings, ERROR_MESSAGES
import time
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class PrescreeningUI:
    def __init__(self):
        self.settings = get_settings()
        self.pipeline = RAGPipeline()
        self.initialize_session_state()
        self.MAX_QUESTIONS = 10
        self.PASSING_PERCENTAGE = 50  # Changed from 75 to 50
        self.COMPLEXITY_POINTS = {1: 5, 2: 10, 3: 15}
        self.COMPLEXITY_TIMES = {1: 45, 2: 60, 3: 90}  # Increased time limits
        
    def initialize_session_state(self):
        if "initialized" not in st.session_state:
            st.session_state.update({
                "initialized": True,
                "step": "welcome",
                "role": None,
                "complexity": 1,
                "questions_asked": 0,
                "total_score": 0,
                "max_possible_score": 0,
                "current_question": None,
                "current_metadata": None,
                "follow_up": None,
                "show_follow_up": False,
                "follow_up_submitted": False,
                "timer_start": None,
                "question_expired": False,
                "answers_history": [],
                "candidate_info": None,
                "time_remaining": None,
                "question_history": set(),  # Track asked questions to avoid repetition
                "follow_up_answer": None,  # Added to store follow_up answer from user
                "partial_score": 0,  # Added to track partial scores
                "answer_submitted": False   # Flag to track if answer is submitted
            })

    def calculate_total_possible_score(self):
        # Calculate max possible score based on questions asked
        total_points = 0
        for hist in st.session_state.answers_history:
            total_points += self.COMPLEXITY_POINTS[hist['complexity']]
        return total_points
    
    def send_report_to_recruiter(self, name, email, notes):
        try:
            # Get SMTP settings from environment
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            recruiter_email = os.getenv('RECRUITER_EMAIL')
            
            if not smtp_username or not smtp_password or not recruiter_email:
                st.warning("Email configuration is incomplete. Check your .env file.")
                return False
            
            # Create email content
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = recruiter_email
            msg['Subject'] = f"Interview Results: {name} - {st.session_state.role}"
            
            # Calculate final score
            total_possible = self.calculate_total_possible_score()
            score_percentage = (st.session_state.total_score / total_possible) * 100 if total_possible > 0 else 0
            
            # Format email body
            body = f"""
            <html>
            <body>
            <h2>Technical Interview Results</h2>
            <p><strong>Candidate:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Role:</strong> {st.session_state.role}</p>
            <p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Final Score:</strong> {score_percentage:.1f}%</p>
            <p><strong>Status:</strong> {"PASSED" if score_percentage >= self.PASSING_PERCENTAGE else "FAILED"}</p>
            
            <h3>Question Summary:</h3>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Q#</th>
                    <th>Level</th>
                    <th>Score</th>
                    <th>Question</th>
                </tr>
            """
            
            # Add questions and answers
            for idx, hist in enumerate(st.session_state.answers_history, 1):
                body += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{hist['complexity']}</td>
                    <td>{hist['score']}</td>
                    <td>{hist['question']}</td>
                </tr>
                """
            
            body += """
            </table>
            
            <h3>Additional Notes:</h3>
            <p>{}</p>
            
            </body>
            </html>
            """.format(notes if notes else "None provided")
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server and send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, recruiter_email, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending report: {e}")
            return False

    def show_welcome(self):
        st.title("🤖 AI Technical Interview Assistant")
        
        # Add custom CSS for better styling
        st.markdown("""
            <style>
            .stButton>button {
                width: 100%;
                margin-top: 20px;
            }
            .info-box {
                padding: 20px;
                border-radius: 5px;
                background-color: #f0f2f6;
                margin-bottom: 20px;
            }
            </style>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        ## Welcome to Your Technical Interview!
        
        This AI-powered interview will assess your technical knowledge and problem-solving skills.
        
        ### Interview Format:
        - 10 technical questions tailored to your role
        - Adaptive difficulty based on your performance
        - Real-time feedback and scoring
        
        ### Time Limits:
        - Level 1 (Basic): 45 seconds
        - Level 2 (Intermediate): 60 seconds
        - Level 3 (Advanced): 90 seconds
        
        ### Scoring System:
        - Level 1 questions: 5 points
        - Level 2 questions: 10 points
        - Level 3 questions: 15 points
        - Passing score: 50%
        
        **Tips:**
        - Read questions carefully
        - Focus on key concepts in your answers
        - Manage your time wisely
        - No copy-pasting allowed
        """)
        
        with st.form("candidate_info_form"):
            st.write("### Start Your Interview")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
            
            with col2:
                roles = [
                    "Software Developer",
                    "Full Stack Developer",
                    "Python Developer",
                    "AI/ML Developer",
                    "Web Developer"
                ]
                role = st.selectbox("Select Your Role", roles)
                experience = st.selectbox("Years of Experience", 
                    ["0-2 years", "2-5 years", "5-8 years", "8+ years"])
            
            submitted = st.form_submit_button("Start Interview")
            
            if submitted:
                if name and email and role:
                    st.session_state.candidate_info = {
                        "name": name,
                        "email": email,
                        "experience": experience
                    }
                    st.session_state.role = role
                    st.session_state.step = "interview"
                    st.rerun()
                else:
                    st.error("Please fill in all required fields to continue.")

    def show_timer(self):
        if st.session_state.timer_start and not st.session_state.show_follow_up:
            time_limit = self.COMPLEXITY_TIMES[st.session_state.complexity]
            current_time = time.time()
            elapsed = current_time - st.session_state.timer_start
            remaining = max(0, time_limit - elapsed)
            
            st.session_state.time_remaining = remaining
            
            # Create a progress bar for the timer
            progress = remaining / time_limit
            
            # Custom color based on remaining time
            if remaining < 10:
                color = "#ff0000"  # Red
            elif remaining < 20:
                color = "#ffa500"  # Orange
            else:
                color = "#00ff00"  # Green
                
            # Display timer with color coding
            st.markdown(
                f"""
                <div style="
                    margin: 10px 0;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: {color}20;
                    text-align: center;
                ">
                    <span style="font-size: 24px; color: {color};">
                        ⏱️ {int(remaining)} seconds
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Auto-submit when time expires
            if remaining <= 0 and not st.session_state.question_expired:
                st.session_state.question_expired = True
                st.session_state.complexity = max(1, st.session_state.complexity - 1)
                st.warning("Time's up! Submitting current answer...")
                time.sleep(1)  # Give user time to see the message
                st.rerun()

    def handle_follow_up_question(self):
        st.markdown(
            f"""
            <div style="
                background-color:rgb(9, 15, 27);
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border: 3px solid #FFA500;
            ">
                <h3>Follow-up Question:</h3>
                <p style="font-size: 18px;">{st.session_state.follow_up}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        follow_up_answer = st.text_area(
            "Your Follow-up Answer:",
            key="follow_up_answer_input",
            height=100,
            max_chars=250,
            help="Provide more specific details to improve your score"
        )
        
        # Show character count for follow-up
        remaining_chars = 250 - len(follow_up_answer)
        st.markdown(f"Characters remaining: {remaining_chars}")
        
        follow_up_submitted = st.button("Submit Follow-up Answer", type="primary")
        
        if follow_up_submitted:
            with st.spinner("Evaluating your follow-up answer..."):
                # Evaluate follow-up answer
                feedback, score, _ = self.pipeline.evaluate_answer(
                    st.session_state.follow_up,
                    follow_up_answer,
                    "Expected follow-up answer"  # You might want to modify this
                )
                
                current_question_points = self.COMPLEXITY_POINTS[st.session_state.complexity]
                additional_points = (score * current_question_points) / 2  # Follow-up worth half the points
                
                # Update answer history to include follow-up
                st.session_state.answers_history[-1].update({
                    'follow_up_question': st.session_state.follow_up,
                    'follow_up_answer': follow_up_answer,
                    'follow_up_score': additional_points,
                    'follow_up_feedback': feedback
                })
                
                # Add partial points
                st.session_state.total_score += additional_points
                
                # Show feedback
                if score >= 0.75:
                    st.success(f"✨ Excellent follow-up! You earned an additional {additional_points} points!")
                elif score >= 0.3:
                    st.warning(f"👍 Good attempt! You earned {additional_points} points.")
                else:
                    st.error("❌ Your follow-up didn't provide the necessary clarification.")
                
                st.markdown(f"**Feedback:** {feedback}")
                
                # Reset for next question
                st.session_state.follow_up = None
                st.session_state.show_follow_up = False
                st.session_state.follow_up_submitted = True
                st.session_state.current_question = None
                st.session_state.questions_asked += 1
                
                time.sleep(2)  # Give time to read feedback
                st.rerun()

    def show_question(self):
        if st.session_state.questions_asked >= self.MAX_QUESTIONS:
            self.show_final_results()
            return
            
        # Show interview progress
        progress = st.session_state.questions_asked / self.MAX_QUESTIONS
        st.progress(progress, text=f"Question {st.session_state.questions_asked + 1} of {self.MAX_QUESTIONS}")
        
        # Show current stats in sidebar
        with st.sidebar:
            st.header("Interview Progress")
            st.markdown(f"""
            - **Score**: {st.session_state.total_score} points
            - **Questions Left**: {self.MAX_QUESTIONS - st.session_state.questions_asked}
            - **Current Level**: {st.session_state.complexity}
            """)
            
            # Show difficulty distribution
            st.markdown("### Question Difficulty")
            level_counts = {1: 0, 2: 0, 3: 0}
            for hist in st.session_state.answers_history:
                level_counts[hist['complexity']] += 1
            
            for level, count in level_counts.items():
                st.progress(count / self.MAX_QUESTIONS, 
                    text=f"Level {level}: {count} questions")

        # Handle follow-up question if needed
        if st.session_state.show_follow_up and st.session_state.follow_up:
            self.handle_follow_up_question()
            return

        # Get a new question if needed
        if not st.session_state.current_question:
            attempts = 0
            max_attempts = 10  # Prevent infinite loops
            
            while attempts < max_attempts:
                question, metadata = self.pipeline.get_question(
                    st.session_state.role,
                    st.session_state.complexity
                )
                
                if not question:
                    st.error(ERROR_MESSAGES["no_questions"])
                    return
                    
                # Check if question hasn't been asked before
                if question not in st.session_state.question_history:
                    st.session_state.current_question = question
                    st.session_state.current_metadata = metadata
                    st.session_state.timer_start = time.time()
                    st.session_state.question_expired = False
                    st.session_state.question_history.add(question)  # Track asked question
                    st.session_state.answer_submitted = False  # Reset submission flag
                    break
                    
                attempts += 1
            
            if attempts >= max_attempts:
                # UPDATED: If we can't find a new question after max attempts, try a different complexity level
                fallback_levels = [1, 2, 3]
                fallback_levels.remove(st.session_state.complexity)  # Remove current complexity
                
                for level in fallback_levels:
                    fallback_attempts = 0
                    while fallback_attempts < 5:  # Try 5 times with each fallback level
                        question, metadata = self.pipeline.get_question(
                            st.session_state.role,
                            level
                        )
                        
                        if question and question not in st.session_state.question_history:
                            st.session_state.current_question = question
                            st.session_state.current_metadata = metadata
                            st.session_state.timer_start = time.time()
                            st.session_state.question_expired = False
                            st.session_state.question_history.add(question)
                            st.session_state.answer_submitted = False
                            st.session_state.complexity = level  # Update complexity to match question
                            break
                        
                        fallback_attempts += 1
                    
                    if st.session_state.current_question:
                        break  # Found a question, exit the loop
                
                # If still no question found
                if not st.session_state.current_question:
                    st.error("Unable to find a new question. Please contact support.")
                    return
        
        # Show timer
        self.show_timer()
        
        # Display question with styling
        st.markdown(f"""
        <div style="
            background-color:rgb(9, 15, 27);
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        ">
            <h3>Question {st.session_state.questions_asked + 1}:</h3>
            <p style="font-size: 18px;">{st.session_state.current_question}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Custom text area with character counter
        answer = st.text_area(
            "Your Answer:",
            key=f"answer_{st.session_state.questions_asked}",
            height=150,
            max_chars=500,  # Limit answer length
            help="Type your answer here. Be concise and focus on key points."
        )
        
        # Show character count
        remaining_chars = 500 - len(answer)
        st.markdown(f"Characters remaining: {remaining_chars}")
        
        # Submit button with loading state
        submit_answer = st.button("Submit Answer", type="primary", disabled=st.session_state.answer_submitted)
        
        if submit_answer and not st.session_state.answer_submitted:
            # Set the flag to prevent multiple submissions
            st.session_state.answer_submitted = True
            
            with st.spinner("Evaluating your answer..."):
                if st.session_state.question_expired:
                    score = 0
                    feedback = "Time expired. Question marked as incorrect."
                    follow_up = None
                else:
                    feedback, score, follow_up = self.pipeline.evaluate_answer(
                        st.session_state.current_question,
                        answer,
                        st.session_state.current_metadata["correct_answer"]
                    )
                
                current_question_points = self.COMPLEXITY_POINTS[st.session_state.complexity]
                question_score = score * current_question_points
                
                # Record answer history
                st.session_state.answers_history.append({
                    'question': st.session_state.current_question,
                    'answer': answer,
                    'complexity': st.session_state.complexity,
                    'score': question_score,
                    'feedback': feedback,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Show feedback with appropriate styling
                if score >= 0.75:
                    st.success(f"✨ Excellent! You earned {question_score} points!")
                    st.session_state.total_score += question_score
                    st.session_state.complexity = min(3, st.session_state.complexity + 1)
                    # Move to next question
                    st.session_state.current_question = None
                    st.session_state.questions_asked += 1
                elif score >= 0.3:
                    st.warning(f"👍 Partially correct. You earned {question_score/2} points.")
                    st.session_state.total_score += question_score/2  # Half points for partial
                    if follow_up:
                        st.session_state.follow_up = follow_up
                        st.session_state.show_follow_up = True
                        st.session_state.partial_score = question_score/2
                        st.markdown("""
                        <div style="
                            background-color: #FFF8E1;
                            padding: 15px;
                            border-radius: 5px;
                            margin: 20px 0;
                            border-left: 5px solid #FFA000;
                        ">
                            <h4 style="color: #FF6F00;">Follow-up Available! 🔍</h4>
                            <p>Your answer was partially correct. Answer the follow-up question to earn additional points!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.session_state.complexity = max(1, st.session_state.complexity - 1)
                        # Move to next question if no follow-up
                        st.session_state.current_question = None
                        st.session_state.questions_asked += 1
                else:
                    st.error("❌ Incorrect answer.")
                    st.session_state.complexity = max(1, st.session_state.complexity - 1)
                    # Move to next question
                    st.session_state.current_question = None
                    st.session_state.questions_asked += 1
                
                st.markdown(f"**Feedback:** {feedback}")
                
                if not follow_up:
                    time.sleep(2)  # Give time to read feedback
                    st.rerun()

    def show_final_results(self):
        # Calculate final score percentage 
        total_possible = self.calculate_total_possible_score()
        score_percentage = (st.session_state.total_score / total_possible) * 100 if total_possible > 0 else 0
        
        # Show results with styling
        st.markdown("""
        <style>
        .results-header {
            text-align: center;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            background-color: #042d80;
        }
        .score-card {
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div class="results-header">
                <h1>Interview Complete! 🎉</h1>
                <h2>Final Score: {score_percentage:.1f}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Show detailed results
        st.markdown("### Performance Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Points", f"{st.session_state.total_score}")
        with col2:
            st.metric("Questions Answered", f"{self.MAX_QUESTIONS}")
        with col3:
            st.metric("Highest Level Reached", f"Level {max(h['complexity'] for h in st.session_state.answers_history)}")
        
        # Show question history
        st.markdown("### Question History")
        for idx, hist in enumerate(st.session_state.answers_history, 1):
            with st.expander(f"Question {idx} (Level {hist['complexity']})"):
                st.markdown(f"**Q:** {hist['question']}")
                st.markdown(f"**Your Answer:** {hist['answer']}")
                st.markdown(f"**Score:** {hist['score']} points")
                st.markdown(f"**Feedback:** {hist['feedback']}")
                
                # Show follow-up details if exists
                if 'follow_up_question' in hist:
                    st.markdown("---")
                    st.markdown(f"**Follow-up Question:** {hist['follow_up_question']}")
                    st.markdown(f"**Your Follow-up Answer:** {hist['follow_up_answer']}")
                    st.markdown(f"**Additional Points:** {hist['follow_up_score']} points")
                    st.markdown(f"**Follow-up Feedback:** {hist['follow_up_feedback']}")
        
        # Show pass/fail status
        if score_percentage >= self.PASSING_PERCENTAGE:
            st.success("🎉 Congratulations! You have passed the technical interview.")
            
            # Collect final information
            with st.form("final_submission"):
                st.markdown("### Submit Your Results")
                st.markdown("Please confirm your information for the final report:")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name", 
                        value=st.session_state.candidate_info["name"])
                with col2:
                    email = st.text_input("Email", 
                        value=st.session_state.candidate_info["email"])
                
                notes = st.text_area("Additional Notes (optional)", 
                    placeholder="Any comments about your interview experience?")
                
                submit_results = st.form_submit_button("Submit Results")
                
                if submit_results:
                    with st.spinner("Sending interview results..."):
                        if self.send_report_to_recruiter(name, email, notes):
                            st.success("Results submitted successfully! The recruiter will contact you soon.")
                        else:
                            st.error("There was an error submitting your results. Please contact the recruiter directly.")
        else:
            st.error("Unfortunately, you did not meet the passing criteria for this position.")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Return to Home", use_container_width=True):
                # Clear session state properly
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col2:
            if st.button("Download Results", use_container_width=True):
                # Generate results JSON
                results = {
                    "candidate": st.session_state.candidate_info,
                    "role": st.session_state.role,
                    "score": score_percentage,
                    "questions": [{
                        "question": q["question"],
                        "complexity": q["complexity"],
                        "score": q["score"],
                        "feedback": q["feedback"]
                    } for q in st.session_state.answers_history]
                }
                st.download_button(
                    "Download Results",
                    data=json.dumps(results, indent=2),
                    file_name="interview_results.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    def run(self):
        if st.session_state.step == "welcome":
            self.show_welcome()
        elif st.session_state.step == "interview":
            self.show_question()

def main():
    ui = PrescreeningUI()
    ui.run()

if __name__ == "__main__":
    main()
