import React from 'react';
import { Shield, Lock, Eye, FileText, Users, Globe } from 'lucide-react';

const About = () => {
  const features = [
    {
      icon: Shield,
      title: "Secure Encryption",
      description: "All secret data is encrypted using AES-256 encryption before being embedded into media files."
    },
    {
      icon: Eye,
      title: "Invisible Hiding",
      description: "Data is hidden in the least significant bits, making it virtually undetectable to the naked eye."
    },
    {
      icon: FileText,
      title: "Multiple Formats",
      description: "Support for various media formats including images, audio, video, and voice recordings."
    },
    {
      icon: Lock,
      title: "Password Protected",
      description: "All embedded data is protected with user-defined passwords for maximum security."
    }
  ];

  const useCases = [
    "Digital watermarking for copyright protection",
    "Covert communication channels",
    "Data backup and archival",
    "Intellectual property protection",
    "Secure document transmission",
    "Anti-tampering mechanisms"
  ];

  const technicalDetails = [
    {
      title: "Image Steganography",
      technique: "LSB (Least Significant Bit)",
      description: "Hides data by modifying the least significant bits of pixel values in RGB channels."
    },
    {
      title: "Audio Steganography",
      technique: "Echo Hiding & Spread Spectrum",
      description: "Uses audio echo hiding and spread spectrum techniques for imperceptible data hiding."
    },
    {
      title: "Video Steganography",
      technique: "Frame-based LSB",
      description: "Manipulates individual video frames using LSB techniques for high capacity hiding."
    },
    {
      title: "Voice Steganography",
      technique: "Phoneme-based Hiding",
      description: "Uses voice activity detection and phoneme manipulation for speech-specific hiding."
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          About Steganography
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Steganography is the practice of hiding secret information within ordinary, non-secret files 
          or messages to avoid detection. Unlike cryptography, which makes a message unreadable, 
          steganography makes the existence of a message undetectable.
        </p>
      </div>

      {/* What is Steganography */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          What is Steganography?
        </h2>
        <div className="prose prose-lg max-w-none text-gray-700">
          <p className="mb-4">
            The word "steganography" comes from the Greek words "steganos" (meaning "covered" or "concealed") 
            and "graphy" (meaning "writing"). It is the art and science of hiding information in plain sight.
          </p>
          <p className="mb-4">
            While cryptography scrambles a message so it cannot be understood, steganography hides the 
            message so it cannot be seen. A steganographic message appears to be something else: an image, 
            an article, a shopping list, or some other message. This apparent message is called the "cover" 
            or "carrier" text, image, or audio.
          </p>
          <p>
            The advantage of steganography over cryptography alone is that messages do not attract attention 
            to themselves. Plainly visible encrypted messages—no matter how unbreakable—will arouse suspicion, 
            and may in themselves be incriminating in countries where encryption is illegal.
          </p>
        </div>
      </div>

      {/* Features */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          Application Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Technical Implementation */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          Technical Implementation
        </h2>
        <div className="space-y-6">
          {technicalDetails.map((detail, index) => (
            <div key={index} className="border-l-4 border-primary-500 pl-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {detail.title}
              </h3>
              <p className="text-primary-600 font-medium mb-2">
                Technique: {detail.technique}
              </p>
              <p className="text-gray-600">
                {detail.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Real-world Applications */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          Real-world Applications
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Globe className="w-5 h-5 mr-2 text-blue-600" />
              Commercial Uses
            </h3>
            <ul className="space-y-2 text-gray-600">
              {useCases.slice(0, 3).map((useCase, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  {useCase}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-green-600" />
              Security Applications
            </h3>
            <ul className="space-y-2 text-gray-600">
              {useCases.slice(3).map((useCase, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  {useCase}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Security Notice */}
      <div className="card bg-yellow-50 border-yellow-200">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Important Security Notice
        </h2>
        <div className="text-gray-700 space-y-3">
          <p>
            <strong>Legal Compliance:</strong> This application is intended for educational and legitimate 
            purposes only. Users are responsible for ensuring compliance with local laws and regulations 
            regarding data hiding and encryption.
          </p>
          <p>
            <strong>Data Security:</strong> While we implement strong encryption, users should always 
            use strong, unique passwords and consider additional security measures for highly sensitive data.
          </p>
          <p>
            <strong>Detection Risk:</strong> Advanced steganalysis techniques may be able to detect 
            hidden data. This tool is not intended for high-security applications where detection 
            resistance is critical.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About;




















