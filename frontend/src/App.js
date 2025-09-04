import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { EnhancedChat } from "./components/Chat/EnhancedChat";
import { Chat } from "./components/Chat/Chat";
import { KnowledgeManager } from "./components/Knowledge/KnowledgeManager";
import { AdvancedKnowledgeManager } from "./components/Knowledge/AdvancedKnowledgeManager";
import { ImageUploader } from "./components/Upload/ImageUploader";
import { AudioBooks } from "./components/AudioBooks/AudioBooks";
import { Contact } from "./components/Contact/Contact";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/enhanced" element={<EnhancedChat />} />
          <Route path="/knowledge" element={<KnowledgeManager />} />
          <Route path="/advanced" element={<AdvancedKnowledgeManager />} />
          <Route path="/upload" element={<ImageUploader />} />
          <Route path="/audiobooks" element={<AudioBooks />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;