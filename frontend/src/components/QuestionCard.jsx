import { useState } from 'react';
import { ChevronDown, ChevronUp, Check } from 'lucide-react';

const TYPE_LABELS = {
  mcq: 'MCQ',
  true_false: 'True / False',
  short_answer: 'Short Answer',
};

const TYPE_BADGE_CLASS = {
  mcq: 'badge-mcq',
  true_false: 'badge-true-false',
  short_answer: 'badge-short-answer',
};

const DIFFICULTY_BADGE_CLASS = {
  easy: 'badge-easy',
  medium: 'badge-medium',
  hard: 'badge-hard',
};

const OPTION_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

export default function QuestionCard({ question, index }) {
  const [showAnswer, setShowAnswer] = useState(false);

  return (
    <div className="glass-card question-card fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="card-header">
        <span className="question-number">Question {index + 1}</span>
        <div className="question-badges">
          <span className={`badge ${DIFFICULTY_BADGE_CLASS[question.difficulty] || 'badge-medium'}`}>
            {question.difficulty}
          </span>
          <span className={`badge ${TYPE_BADGE_CLASS[question.type] || 'badge-mcq'}`}>
            {TYPE_LABELS[question.type] || question.type}
          </span>
        </div>
      </div>

      <p className="question-text">{question.question}</p>

      {question.type === 'mcq' && question.options && (
        <ul className="options-list">
          {question.options.map((option, i) => (
            <li
              key={i}
              className={`option-item ${showAnswer && option === question.answer ? 'correct' : ''}`}
            >
              <span className="option-label">
                {showAnswer && option === question.answer ? (
                  <Check size={14} />
                ) : (
                  OPTION_LETTERS[i]
                )}
              </span>
              <span>{option}</span>
            </li>
          ))}
        </ul>
      )}

      {question.type === 'true_false' && (
        <ul className="options-list">
          {['True', 'False'].map((opt) => (
            <li
              key={opt}
              className={`option-item ${showAnswer && opt === question.answer ? 'correct' : ''}`}
            >
              <span className="option-label">
                {showAnswer && opt === question.answer ? <Check size={14} /> : opt[0]}
              </span>
              <span>{opt}</span>
            </li>
          ))}
        </ul>
      )}

      <button className="btn-reveal" onClick={() => setShowAnswer(!showAnswer)}>
        {showAnswer ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {showAnswer ? 'Hide Answer' : 'Show Answer'}
      </button>

      <div className={`answer-section ${showAnswer ? 'visible' : ''}`}>
        <div className="answer-box">
          <div className="answer-label">✓ Correct Answer</div>
          <div className="answer-text">{question.answer}</div>
          {question.explanation && (
            <p className="explanation-text">{question.explanation}</p>
          )}
        </div>
      </div>
    </div>
  );
}
