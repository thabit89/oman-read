import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Chat } from "./components/Chat/Chat";
import { KnowledgeManager } from "./components/Knowledge/KnowledgeManager";
import { AdvancedKnowledgeManager } from "./components/Knowledge/AdvancedKnowledgeManager";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/knowledge" element={<KnowledgeManager />} />
          <Route path="/advanced" element={<AdvancedKnowledgeManager />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;