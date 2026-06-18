import { useState, useEffect } from 'react';
import { Clock, Trash2, BookOpen, ChevronDown, ChevronUp, HelpCircle, AlertCircle } from 'lucide-react';
import { getHistory, getSession, deleteSession } from '../api';
import QuestionCard from './QuestionCard';

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [expandedData, setExpandedData] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getHistory();
      setSessions(response.data.sessions || []);
    } catch (err) {
      setError('Failed to load history. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleExpand = async (id) => {
    if (expandedId === id) {
      setExpandedId(null);
      setExpandedData(null);
      return;
    }

    try {
      setLoadingDetail(true);
      setExpandedId(id);
      const response = await getSession(id);
      setExpandedData(response.data);
    } catch (err) {
      console.error('Failed to load session details:', err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this session?')) return;
    try {
      await deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (expandedId === id) {
        setExpandedId(null);
        setExpandedData(null);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="fade-in-up">
        <div className="section-header">
          <h2 className="section-title">Generation History</h2>
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="shimmer shimmer-card" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="fade-in-up">
        <div className="section-header">
          <h2 className="section-title">Generation History</h2>
        </div>
        <div className="error-banner">
          <AlertCircle size={18} />
          {error}
        </div>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="fade-in-up">
        <div className="section-header">
          <h2 className="section-title">Generation History</h2>
        </div>
        <div className="glass-card">
          <div className="empty-state">
            <BookOpen size={48} className="empty-icon" />
            <p className="empty-title">No history yet</p>
            <p className="empty-subtitle">Generated questions will appear here</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in-up">
      <div className="section-header">
        <h2 className="section-title">Generation History</h2>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </span>
      </div>

      {sessions.map((session) => (
        <div key={session.id}>
          <div
            className="glass-card history-card"
            onClick={() => handleExpand(session.id)}
          >
            <div className="card-top">
              <div style={{ flex: 1 }}>
                <div className="history-topic">
                  {session.topic || 'Untitled Session'}
                </div>
                <p className="history-preview">{session.input_preview}</p>
                <div className="history-meta">
                  <span>
                    <HelpCircle size={14} />
                    {session.question_count} questions
                  </span>
                  <span>
                    <Clock size={14} />
                    {formatDate(session.created_at)}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <button className="btn-danger" onClick={(e) => handleDelete(e, session.id)}>
                  <Trash2 size={14} />
                </button>
                {expandedId === session.id ? (
                  <ChevronUp size={18} style={{ color: 'var(--text-muted)' }} />
                ) : (
                  <ChevronDown size={18} style={{ color: 'var(--text-muted)' }} />
                )}
              </div>
            </div>
          </div>

          {expandedId === session.id && (
            <div style={{ padding: '0 0.5rem', marginBottom: '1rem' }}>
              {loadingDetail ? (
                <div className="loading-container" style={{ padding: '2rem' }}>
                  <div className="loading-orbits">
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                  </div>
                </div>
              ) : expandedData ? (
                <div className="questions-grid" style={{ marginTop: '0.5rem' }}>
                  {expandedData.questions?.map((q, i) => (
                    <QuestionCard key={q.id || i} question={q} index={i} />
                  ))}
                </div>
              ) : null}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
