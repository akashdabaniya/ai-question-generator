import { useState } from 'react';
import Header from './components/Header';
import TextInput from './components/TextInput';
import QuestionList from './components/QuestionList';
import History from './components/History';
import { generateQuestions } from './api';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('generate');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async (data) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await generateQuestions(data);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate questions. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="aurora-bg"></div>
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="container">
        {activeTab === 'generate' ? (
          <>
            <TextInput onGenerate={handleGenerate} isLoading={isLoading} />
            {error && <div className="error-banner">{error}</div>}
            {result && (
              <QuestionList 
                questions={result.questions} 
                keywords={result.keywords} 
                metadata={result.metadata} 
                sessionId={result.session_id} 
              />
            )}
          </>
        ) : (
          <History />
        )}
      </main>
    </div>
  );
}

export default App;
