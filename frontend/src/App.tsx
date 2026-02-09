import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar/Sidebar';
import SearchPage from './components/SearchPage/SearchPage';
import KnowledgeBase from './components/KnowledgeBase/KnowledgeBase';
import { ChatPage } from './components/ChatPage/ChatPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/search" replace />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/knowledge-base" element={<KnowledgeBase />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
