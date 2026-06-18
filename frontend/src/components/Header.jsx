import { Brain, Sparkles, Clock } from 'lucide-react';

export default function Header({ activeTab, onTabChange }) {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <Brain size={28} className="icon" />
          <span className="navbar-title">AI Question Generator</span>
        </div>
        <div className="navbar-tabs">
          <button
            className={`nav-tab ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => onTabChange('generate')}
          >
            <Sparkles size={16} />
            Generate
          </button>
          <button
            className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => onTabChange('history')}
          >
            <Clock size={16} />
            History
          </button>
        </div>
      </div>
    </nav>
  );
}
