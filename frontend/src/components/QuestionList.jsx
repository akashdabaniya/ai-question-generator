import { useState } from 'react';
import { Download, Filter, Zap, Clock, HelpCircle } from 'lucide-react';
import QuestionCard from './QuestionCard';
import { exportSession } from '../api';

const FILTER_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'mcq', label: 'MCQ' },
  { value: 'true_false', label: 'True/False' },
  { value: 'short_answer', label: 'Short Answer' },
];

export default function QuestionList({ questions, keywords, metadata, sessionId }) {
  const [activeFilter, setActiveFilter] = useState('all');

  const filtered =
    activeFilter === 'all'
      ? questions
      : questions.filter((q) => q.type === activeFilter);

  const handleExport = async () => {
    try {
      const response = await exportSession(sessionId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `questions_${sessionId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const mcqCount = questions.filter((q) => q.type === 'mcq').length;
  const tfCount = questions.filter((q) => q.type === 'true_false').length;
  const saCount = questions.filter((q) => q.type === 'short_answer').length;

  return (
    <div className="fade-in-up">
      {/* Keywords */}
      {keywords && keywords.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Zap size={16} style={{ color: 'var(--primary-light)' }} />
            <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Extracted Keywords
            </span>
          </div>
          <div className="keywords-scroll">
            {keywords.map((kw, i) => (
              <span key={i} className="keyword-chip">
                {kw.keyword}
                <span className="keyword-score">{(kw.score * 100).toFixed(0)}%</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Stats Bar */}
      <div className="stats-bar">
        <div className="stat-item">
          <HelpCircle size={16} style={{ color: 'var(--primary-light)' }} />
          <span className="stat-value">{metadata?.total || questions.length}</span>
          <span>Questions</span>
        </div>
        <div className="stat-item">
          <Clock size={16} style={{ color: 'var(--accent)' }} />
          <span className="stat-value">{metadata?.processing_time?.toFixed(2) || '—'}s</span>
          <span>Processing</span>
        </div>
        {mcqCount > 0 && (
          <div className="stat-item">
            <span className="badge badge-mcq" style={{ padding: '0.15rem 0.5rem' }}>MCQ</span>
            <span className="stat-value">{mcqCount}</span>
          </div>
        )}
        {tfCount > 0 && (
          <div className="stat-item">
            <span className="badge badge-true-false" style={{ padding: '0.15rem 0.5rem' }}>T/F</span>
            <span className="stat-value">{tfCount}</span>
          </div>
        )}
        {saCount > 0 && (
          <div className="stat-item">
            <span className="badge badge-short-answer" style={{ padding: '0.15rem 0.5rem' }}>SA</span>
            <span className="stat-value">{saCount}</span>
          </div>
        )}
        <div style={{ marginLeft: 'auto' }}>
          <button className="btn-secondary" onClick={handleExport}>
            <Download size={16} />
            Export JSON
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <Filter size={16} style={{ color: 'var(--text-muted)' }} />
        {FILTER_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            className={`btn-secondary ${activeFilter === opt.value ? 'active' : ''}`}
            onClick={() => setActiveFilter(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Questions Grid */}
      {filtered.length > 0 ? (
        <div className="questions-grid">
          {filtered.map((q, i) => (
            <QuestionCard key={q.id || i} question={q} index={i} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <HelpCircle size={48} className="empty-icon" />
          <p className="empty-title">No questions match this filter</p>
          <p className="empty-subtitle">Try selecting a different question type</p>
        </div>
      )}
    </div>
  );
}
