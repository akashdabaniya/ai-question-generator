export default function LoadingSpinner({ message = 'Generating questions...' }) {
  return (
    <div className="loading-container">
      <div className="loading-orbits">
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
      </div>
      <p className="loading-text">{message}</p>
    </div>
  );
}
