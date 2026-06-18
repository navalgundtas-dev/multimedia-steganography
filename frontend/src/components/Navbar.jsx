import React from 'react';
import { Image, Music, Video, Mic, Info, FileText } from 'lucide-react';

const Navbar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'image', label: 'Image', icon: Image, color: 'text-blue-600' },
    { id: 'audio', label: 'Audio', icon: Music, color: 'text-green-600' },
    { id: 'video', label: 'Video', icon: Video, color: 'text-purple-600' },
    { id: 'text', label: 'Text', icon: FileText, color: 'text-orange-600' },
    { id: 'voice', label: 'Voice', icon: Mic, color: 'text-red-600' },
    { id: 'about', label: 'About', icon: Info, color: 'text-gray-600' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-gray-900">
                Steganography
              </h1>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                    ${isActive 
                      ? 'bg-primary-100 text-primary-700 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-primary-600' : tab.color}`} />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;






