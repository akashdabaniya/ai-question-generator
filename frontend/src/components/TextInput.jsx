import { useState } from 'react';
import { Sparkles, BookOpen, Zap } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

export default function TextInput({ onGenerate, isLoading }) {
  const [text, setText] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionTypes, setQuestionTypes] = useState(['mcq', 'true_false', 'short_answer']);

  const isValid = text.length >= 50;

  const handleTypeToggle = (type) => {
    setQuestionTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isValid || questionTypes.length === 0) return;
    onGenerate({
      text,
      topic: topic || undefined,
      difficulty,
      num_questions: numQuestions,
      question_types: questionTypes,
    });
  };

  if (isLoading) {
    return (
      <div className="glass-card fade-in-up" style={{ marginBottom: '2rem' }}>
        <LoadingSpinner message="Analyzing text & generating questions..." />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="fade-in-up" style={{ marginBottom: '2rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <BookOpen size={22} style={{ color: 'var(--primary-light)' }} />
          <h2 style={{ fontSize: '1.2rem', fontWeight: '700' }}>Input Your Text</h2>
        </div>

        <div className="form-group">
          <label className="form-label">Source Text *</label>
          <textarea
            className="textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your text here (minimum 50 characters)... &#10;&#10;Example: Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves..."
            rows={8}
          />
          <div className={`char-count ${text.length >= 50 ? 'valid' : text.length > 0 ? 'invalid' : ''}`}>
            {text.length} / 50 min characters
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Topic (Optional)</label>
            <input
              className="input"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Machine Learning, Biology..."
            />
          </div>
          <div className="form-group">
            <label className="form-label">Number of Questions</label>
            <div className="number-input-wrapper">
              <input
                className="input"
                type="number"
                min={1}
                max={20}
                value={numQuestions}
                onChange={(e) => setNumQuestions(Math.min(20, Math.max(1, parseInt(e.target.value) || 1)))}
              />
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>1–20</span>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Difficulty</label>
          <div className="segmented-control">
            {['easy', 'medium', 'hard'].map((d) => (
              <button
                key={d}
                type="button"
                className={`segment ${difficulty === d ? 'active' : ''}`}
                onClick={() => setDifficulty(d)}
              >
                {d.charAt(0).toUpperCase() + d.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Question Types</label>
          <div className="checkbox-group">
            {[
              { value: 'mcq', label: 'Multiple Choice' },
              { value: 'true_false', label: 'True / False' },
              { value: 'short_answer', label: 'Short Answer' },
            ].map(({ value, label }) => (
              <label key={value} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={questionTypes.includes(value)}
                  onChange={() => handleTypeToggle(value)}
                />
                {label}
              </label>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
          <button
            type="submit"
            className="btn-primary btn-lg"
            disabled={!isValid || questionTypes.length === 0}
          >
            <Sparkles size={20} />
            Generate Questions
            <Zap size={16} />
          </button>
        </div>
      </div>
    </form>
  );
}
