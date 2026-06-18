import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ImageStego from './components/ImageStego';
import AudioStego from './components/AudioStego';
import VideoStego from './components/VideoStego';
import TextStego from './components/TextStego';
import VoiceStego from './components/VoiceStego';
import About from './components/About';
import LsbGuide from './components/LsbGuide';
import HeroBanner from './components/HeroBanner';

function App() {
  const [activeTab, setActiveTab] = useState('image');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'image':
        return <ImageStego />;
      case 'audio':
        return <AudioStego />;
      case 'video':
        return <VideoStego />;
      case 'text':
        return <TextStego />;
      case 'voice':
        return <VoiceStego />;
      case 'about':
        return <About />;
      default:
        return <ImageStego />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
        <HeroBanner />
        <div className="animate-fade-in">
          {renderActiveTab()}
        </div>
        <LsbGuide />
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2024 Steganography Web Application. Built with React and Flask.</p>
            <p className="mt-2 text-sm">
              Hide and extract secret data in various media files using advanced steganography techniques.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;






