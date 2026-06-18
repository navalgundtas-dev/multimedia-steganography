import React, { useState, useRef } from 'react';
import { Upload, Download, Eye, Lock, FileText, Video, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import axios from 'axios';

const VideoStego = () => {
  const [mode, setMode] = useState('embed'); // 'embed' or 'extract'
  const [coverVideo, setCoverVideo] = useState(null);
  const [secretText, setSecretText] = useState('');
  const [secretFile, setSecretFile] = useState(null);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  
  const coverFileRef = useRef(null);
  const secretFileRef = useRef(null);

  const handleCoverVideoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCoverVideo(file);
      setError('');
    }
  };

  const handleSecretFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSecretFile(file);
      setSecretText(''); // Clear text when file is selected
    }
  };

  const handleEmbed = async () => {
    if (!coverVideo) {
      setError('Please select a cover video file');
      return;
    }
    if (!secretText && !secretFile) {
      setError('Please provide secret text or file');
      return;
    }
    if (!password) {
      setError('Please enter a password');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('cover_video', coverVideo);
      formData.append('password', password);
      
      if (secretText) {
        formData.append('secret_text', secretText);
      } else if (secretFile) {
        formData.append('secret_file', secretFile);
      }

      const response = await axios.post('/encode/video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResult({
          type: 'success',
          message: response.data.message,
          downloadUrl: response.data.download_url
        });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to embed data');
    } finally {
      setLoading(false);
    }
  };

  const handleExtract = async () => {
    if (!coverVideo) {
      setError('Please select a stego video file');
      return;
    }
    if (!password) {
      setError('Please enter a password');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('stego_video', coverVideo);
      formData.append('password', password);

      const response = await axios.post('/decode/video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResult({
          type: 'success',
          message: response.data.message,
          dataType: response.data.data_type,
          data: response.data.data,
          downloadUrl: response.data.download_url
        });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to extract data');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (url) => {
    window.open(`http://127.0.0.1:5000${url}`, '_blank');
  };

  const resetForm = () => {
    setCoverVideo(null);
    setSecretText('');
    setSecretFile(null);
    setPassword('');
    setResult(null);
    setError('');
    if (coverFileRef.current) coverFileRef.current.value = '';
    if (secretFileRef.current) secretFileRef.current.value = '';
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Video className="w-12 h-12 text-purple-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Video Steganography</h1>
        </div>
        <p className="text-gray-600 text-lg">
          Hide and extract secret data in video files using LSB (Least Significant Bit) technique on frames
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setMode('embed')}
            className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
              mode === 'embed'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Embed Data
          </button>
          <button
            onClick={() => setMode('extract')}
            className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
              mode === 'extract'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            Extract Data
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel - Input */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6 text-gray-900">
            {mode === 'embed' ? 'Hide Secret Data' : 'Extract Hidden Data'}
          </h2>

          {/* Cover Video Upload */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {mode === 'embed' ? 'Cover Video' : 'Stego Video'}
            </label>
            <div className="file-drop-zone">
              <input
                ref={coverFileRef}
                type="file"
                accept=".mp4,.avi,.mov"
                onChange={handleCoverVideoChange}
                className="hidden"
              />
              <button
                onClick={() => coverFileRef.current?.click()}
                className="w-full text-center"
              >
                {coverVideo ? (
                  <div className="flex items-center justify-center space-x-2 text-green-600">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-medium">{coverVideo.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-2 text-gray-500">
                    <Upload className="w-8 h-8" />
                    <span>Click to upload video</span>
                    <span className="text-sm">MP4, AVI, MOV supported</span>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Secret Data Input (only for embed mode) */}
          {mode === 'embed' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Secret Data
              </label>
              
              {/* Text Input */}
              <div className="mb-4">
                <label className="block text-xs text-gray-600 mb-1">Secret Text</label>
                <textarea
                  value={secretText}
                  onChange={(e) => {
                    setSecretText(e.target.value);
                    if (e.target.value) setSecretFile(null);
                  }}
                  placeholder="Enter secret message..."
                  className="input-field h-24 resize-none"
                  disabled={!!secretFile}
                />
              </div>

              {/* File Input */}
              <div>
                <label className="block text-xs text-gray-600 mb-1">Or Secret File</label>
                <div className="file-drop-zone">
                  <input
                    ref={secretFileRef}
                    type="file"
                    onChange={handleSecretFileChange}
                    className="hidden"
                  />
                  <button
                    onClick={() => secretFileRef.current?.click()}
                    className="w-full text-center"
                    disabled={!!secretText}
                  >
                    {secretFile ? (
                      <div className="flex items-center justify-center space-x-2 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">{secretFile.name}</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center space-x-2 text-gray-500">
                        <FileText className="w-4 h-4" />
                        <span className="text-sm">Click to upload file</span>
                      </div>
                    )}
                  </button>
                </div>
              </div>
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
              onClick={mode === 'embed' ? handleEmbed : handleExtract}
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
                  {mode === 'embed' ? (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Embed Data</span>
                    </>
                  ) : (
                    <>
                      <Eye className="w-4 h-4" />
                      <span>Extract Data</span>
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
              
              {result.downloadUrl && (
                <button
                  onClick={() => handleDownload(result.downloadUrl)}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Result</span>
                </button>
              )}
              
              {result.data && result.dataType === 'text' && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Extracted Text:
                  </label>
                  <div className="bg-gray-50 p-3 rounded-lg border">
                    <p className="text-gray-800 whitespace-pre-wrap">{result.data}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {!error && !result && (
            <div className="text-center text-gray-500 py-12">
              <Video className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Results will appear here after processing</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoStego;
