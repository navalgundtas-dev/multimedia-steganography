import React, { useState } from 'react';
import { Lock, FileText, AlertCircle, CheckCircle, Loader, Copy, Check } from 'lucide-react';
import axios from 'axios';

const TextStego = () => {
  const [mode, setMode] = useState('encode'); // 'encode' or 'decode'
  const [coverText, setCoverText] = useState('');
  const [secretText, setSecretText] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleEncode = async () => {
    if (!coverText.trim()) {
      setError('Please enter cover text');
      return;
    }
    if (!secretText.trim()) {
      setError('Please enter secret text');
      return;
    }
    if (!password.trim()) {
      setError('Please enter a password');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/encode/text', {
        cover_text: coverText,
        secret_text: secretText,
        password: password
      });

      if (response.data.success) {
        setResult({
          type: 'success',
          message: response.data.message,
          stegoText: response.data.stego_text
        });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to encode text');
    } finally {
      setLoading(false);
    }
  };

  const handleDecode = async () => {
    if (!coverText.trim()) {
      setError('Please enter stego text');
      return;
    }
    if (!password.trim()) {
      setError('Please enter a password');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/decode/text', {
        stego_text: coverText,
        password: password
      });

      if (response.data.success) {
        setResult({
          type: 'success',
          message: response.data.message,
          secretText: response.data.secret_text
        });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to decode text');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const resetForm = () => {
    setCoverText('');
    setSecretText('');
    setPassword('');
    setResult(null);
    setError('');
    setCopied(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <FileText className="w-12 h-12 text-orange-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Text Steganography</h1>
        </div>
        <p className="text-gray-600 text-lg">
          Hide and extract secret messages in text using zero-width Unicode characters
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setMode('encode')}
            className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
              mode === 'encode'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Encode Data
          </button>
          <button
            onClick={() => setMode('decode')}
            className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
              mode === 'decode'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Decode Data
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel - Input */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6 text-gray-900">
            {mode === 'encode' ? 'Hide Secret Text' : 'Extract Hidden Text'}
          </h2>

          {/* Cover Text Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {mode === 'encode' ? 'Cover Text' : 'Stego Text'}
            </label>
            <textarea
              value={coverText}
              onChange={(e) => setCoverText(e.target.value)}
              placeholder={mode === 'encode' ? 'Enter cover text to hide secret message in...' : 'Enter text with hidden message...'}
              className="input-field h-32 resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              {mode === 'encode' 
                ? 'This is the visible text that will contain the hidden message'
                : 'Paste the text that contains the hidden message'}
            </p>
          </div>

          {/* Secret Text Input (only for encode mode) */}
          {mode === 'encode' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Secret Text
              </label>
              <textarea
                value={secretText}
                onChange={(e) => setSecretText(e.target.value)}
                placeholder="Enter secret message to hide..."
                className="input-field h-32 resize-none"
              />
              <p className="text-xs text-gray-500 mt-1">
                This message will be hidden invisibly in the cover text
              </p>
            </div>
          )}

          {/* Password Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password for encryption"
                className="input-field pl-10"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={mode === 'encode' ? handleEncode : handleDecode}
              disabled={loading}
              className="btn-primary flex-1 flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  {mode === 'encode' ? (
                    <>
                      <FileText className="w-4 h-4" />
                      <span>Encode Text</span>
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      <span>Decode Text</span>
                    </>
                  )}
                </>
              )}
            </button>
            <button
              onClick={resetForm}
              className="btn-secondary px-6"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Right Panel - Results */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6 text-gray-900">Results</h2>
          
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">Error</span>
              </div>
              <p className="text-red-600 mt-1 whitespace-pre-wrap">{error}</p>
            </div>
          )}

          {result && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2 text-green-700 mb-3">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Success</span>
              </div>
              <p className="text-green-600 mb-4">{result.message}</p>
              
              {result.stegoText && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Encoded Text (with hidden message):
                    </label>
                    <button
                      onClick={() => handleCopy(result.stegoText)}
                      className="flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-700"
                    >
                      {copied ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg border">
                    <p className="text-gray-800 whitespace-pre-wrap break-all">{result.stegoText}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Note: This text looks identical to the cover text but contains hidden data. Copy and share it safely.
                  </p>
                </div>
              )}
              
              {result.secretText && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Extracted Secret Text:
                    </label>
                    <button
                      onClick={() => handleCopy(result.secretText)}
                      className="flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-700"
                    >
                      {copied ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg border">
                    <p className="text-gray-800 whitespace-pre-wrap">{result.secretText}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {!error && !result && (
            <div className="text-center text-gray-500 py-12">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Results will appear here after processing</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TextStego;

