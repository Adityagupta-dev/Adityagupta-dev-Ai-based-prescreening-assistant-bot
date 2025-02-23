import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Timer, ChevronRight, Award, AlertTriangle } from 'lucide-react';

const TechnicalInterviewApp = () => {
  // State management
  const [step, setStep] = useState('welcome');
  const [candidateInfo, setCandidateInfo] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [followUpQuestion, setFollowUpQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [questionsAsked, setQuestionsAsked] = useState(0);
  const [score, setScore] = useState(0);
  const [complexity, setComplexity] = useState(1);
  const [answersHistory, setAnswersHistory] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Constants
  const MAX_QUESTIONS = 10;
  const COMPLEXITY_TIMES = { 1: 45, 2: 60, 3: 90 };
  const COMPLEXITY_POINTS = { 1: 5, 2: 10, 3: 15 };
  const PASSING_PERCENTAGE = 75;

  // Timer management
  useEffect(() => {
    let timer;
    if (currentQuestion && timeRemaining > 0 && !isSubmitting) {
      timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleTimeUp();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [currentQuestion, timeRemaining, isSubmitting]);

  // Handle time up
  const handleTimeUp = useCallback(() => {
    if (!isSubmitting) {
      setIsSubmitting(true);
      handleSubmitAnswer(true);
    }
  }, [isSubmitting]);

  // Handle answer submission
  const handleSubmitAnswer = async (isTimeout = false) => {
    setIsSubmitting(true);
    
    // Simulate answer evaluation
    const evaluation = await evaluateAnswer(answer, currentQuestion);
    const questionPoints = COMPLEXITY_POINTS[complexity];
    const earnedPoints = evaluation.score * questionPoints;

    // Update history
    const historyEntry = {
      question: currentQuestion.text,
      answer,
      complexity,
      score: earnedPoints,
      feedback: evaluation.feedback
    };
    setAnswersHistory(prev => [...prev, historyEntry]);

    // Handle scoring and complexity adjustment
    if (evaluation.score >= 0.75) {
      setScore(prev => prev + questionPoints);
      setComplexity(prev => Math.min(3, prev + 1));
      showSuccess(earnedPoints);
    } else if (evaluation.score >= 0.3 && evaluation.followUp) {
      setFollowUpQuestion(evaluation.followUp);
    } else {
      setComplexity(prev => Math.max(1, prev - 1));
      showError();
    }

    if (!evaluation.followUp) {
      moveToNextQuestion();
    }
    setIsSubmitting(false);
  };

  // Move to next question
  const moveToNextQuestion = useCallback(() => {
    if (questionsAsked + 1 >= MAX_QUESTIONS) {
      setStep('results');
    } else {
      setQuestionsAsked(prev => prev + 1);
      setCurrentQuestion(getNextQuestion());
      setAnswer('');
      setTimeRemaining(COMPLEXITY_TIMES[complexity]);
      setFollowUpQuestion(null);
    }
  }, [questionsAsked, complexity]);

  // Question display component
  const QuestionDisplay = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Progress value={(questionsAsked / MAX_QUESTIONS) * 100} className="w-2/3" />
        <div className="flex items-center gap-2">
          <Timer className="w-5 h-5" />
          <span className={`font-bold ${timeRemaining < 10 ? 'text-red-500' : ''}`}>
            {timeRemaining}s
          </span>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            Question {questionsAsked + 1} of {MAX_QUESTIONS}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg mb-4">{currentQuestion?.text}</p>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-2 border rounded-md h-32"
            placeholder="Type your answer here..."
            disabled={isSubmitting}
          />
          <Button 
            onClick={() => handleSubmitAnswer()} 
            disabled={isSubmitting || !answer.trim()}
            className="mt-4"
          >
            Submit Answer
          </Button>
        </CardContent>
      </Card>

      {followUpQuestion && (
        <Alert>
          <AlertTriangle className="w-4 h-4" />
          <AlertDescription>{followUpQuestion}</AlertDescription>
        </Alert>
      )}
    </div>
  );

  // Results display component
  const ResultsDisplay = () => {
    const scorePercentage = (score / (MAX_QUESTIONS * COMPLEXITY_POINTS[2])) * 100;
    const passed = scorePercentage >= PASSING_PERCENTAGE;

    return (
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-6 h-6" />
            Final Results
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold mb-2">
              {scorePercentage.toFixed(1)}%
            </h2>
            {passed ? (
              <Alert className="bg-green-50 border-green-200">
                <AlertDescription className="text-green-700">
                  Congratulations! You've passed the technical interview.
                </AlertDescription>
              </Alert>
            ) : (
              <Alert className="bg-red-50 border-red-200">
                <AlertDescription className="text-red-700">
                  Unfortunately, you didn't meet the passing criteria.
                </AlertDescription>
              </Alert>
            )}
          </div>

          <div className="space-y-4">
            {answersHistory.map((hist, idx) => (
              <Card key={idx} className="bg-gray-50">
                <CardContent className="pt-4">
                  <p className="font-semibold">Question {idx + 1} (Level {hist.complexity})</p>
                  <p className="mt-2">{hist.question}</p>
                  <p className="mt-2 text-gray-600">Your answer: {hist.answer}</p>
                  <p className="mt-2">Score: {hist.score} points</p>
                  <p className="mt-2 text-gray-600">{hist.feedback}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {step === 'welcome' && (
        <WelcomeScreen 
          onStart={(info) => {
            setCandidateInfo(info);
            setStep('interview');
            setCurrentQuestion(getNextQuestion());
            setTimeRemaining(COMPLEXITY_TIMES[1]);
          }} 
        />
      )}
      
      {step === 'interview' && <QuestionDisplay />}
      {step === 'results' && <ResultsDisplay />}
    </div>
  );
};

// Placeholder functions (to be implemented with actual backend)
const evaluateAnswer = async (answer, question) => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock evaluation
  const score = Math.random();
  return {
    score,
    feedback: score >= 0.75 ? "Excellent answer!" : "Partially correct.",
    followUp: score >= 0.3 && score < 0.75 ? "Can you explain more about...?" : null
  };
};

const getNextQuestion = () => ({
  text: "Sample technical question...",
  // Add other question metadata
});

// Welcome screen component
const WelcomeScreen = ({ onStart }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'Software Developer',
    experience: '0-2 years'
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Technical Interview Assistant</CardTitle>
      </CardHeader>
      <CardContent>
        <form 
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            onStart(formData);
          }}
        >
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Full Name"
              className="p-2 border rounded"
              required
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            />
            <input
              type="email"
              placeholder="Email"
              className="p-2 border rounded"
              required
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            />
            <select
              className="p-2 border rounded"
              value={formData.role}
              onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
            >
              <option>Software Developer</option>
              <option>Full Stack Developer</option>
              <option>Python Developer</option>
              <option>AI/ML Developer</option>
            </select>
            <select
              className="p-2 border rounded"
              value={formData.experience}
              onChange={(e) => setFormData(prev => ({ ...prev, experience: e.target.value }))}
            >
              <option>0-2 years</option>
              <option>2-5 years</option>
              <option>5-8 years</option>
              <option>8+ years</option>
            </select>
          </div>
          <Button type="submit" className="w-full">
            Start Interview <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default TechnicalInterviewApp;