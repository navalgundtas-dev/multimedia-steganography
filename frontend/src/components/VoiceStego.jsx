import React, { useState, useRef } from 'react';
import {
  Mic,
  Upload,
  Eye,
  Lock,
  FileText,
  AlertCircle,
  CheckCircle,
  Download,
  Loader,
} from 'lucide-react';
import axios from 'axios';

const VoiceStego = () => {
  const [mode, setMode] = useState('embed');
  const [voiceFile, setVoiceFile] = useState(null);
  const [secretText, setSecretText] = useState('');
  const [secretFile, setSecretFile] = useState(null);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const voiceFileRef = useRef(null);
  const secretFileRef = useRef(null);

  const handleVoiceFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVoiceFile(file);
      setError('');
      setResult(null);
      setAnalysis(null);
    }
  };

  const handleSecretFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSecretFile(file);
      setSecretText('');
    }
  };

  const validateCommonFields = ({ requireSecret }) => {
    if (!voiceFile) {
      setError('Please select a voice recording (mono WAV, 16-bit, 16kHz+).');
      return false;
    }
    if (requireSecret && !secretText && !secretFile) {
      setError('Provide secret text or attach a secret file.');
      return false;
    }
    if (!password) {
      setError('Password is required for encryption/decryption.');
      return false;
    }
    return true;
  };

  const handleEmbed = async () => {
    if (!validateCommonFields({ requireSecret: true })) {
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('voice_file', voiceFile);
      formData.append('password', password);

      if (secretText) {
        formData.append('secret_text', secretText);
      } else if (secretFile) {
        formData.append('secret_file', secretFile);
      }

      const response = await axios.post('/encode/voice', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.success) {
        setResult({
          message: response.data.message,
          downloadUrl: response.data.download_url,
          type: 'embed',
        });
        setAnalysis(response.data.analysis || null);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to embed data into voice recording.');
    } finally {
      setLoading(false);
    }
  };

  const handleExtract = async () => {
    if (!validateCommonFields({ requireSecret: false })) {
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('stego_voice', voiceFile);
      formData.append('password', password);

      const response = await axios.post('/decode/voice', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.success) {
        setResult({
          message: response.data.message,
          dataType: response.data.data_type,
          data: response.data.data,
          downloadUrl: response.data.download_url,
          type: 'extract',
        });
        setAnalysis(response.data.analysis || null);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to extract data from voice recording.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (url) => {
    if (url) {
      window.open(`http://127.0.0.1:5000${url}`, '_blank');
    }
  };

  const resetForm = () => {
    setVoiceFile(null);
    setSecretText('');
    setSecretFile(null);
    setPassword('');
    setError('');
    setResult(null);
    setAnalysis(null);
    if (voiceFileRef.current) voiceFileRef.current.value = '';
    if (secretFileRef.current) secretFileRef.current.value = '';
  };

  const renderAnalysis = () => {
    if (!analysis) return null;

    const rows = [
      { label: 'Duration', value: analysis.duration_seconds ? `${analysis.duration_seconds}s` : null },
      { label: 'Total Samples', value: analysis.total_samples },
      { label: 'Voiced Samples', value: analysis.voiced_samples },
      { label: 'Voice Density', value: analysis.voice_ratio ? `${(analysis.voice_ratio * 100).toFixed(1)}%` : null },
      { label: 'Capacity Used', value: analysis.capacity_bytes ? `${analysis.capacity_bytes} bytes` : null },
      { label: 'Payload Bytes', value: analysis.payload_bytes },
      { label: 'Recovered Bytes', value: analysis.recovered_bytes },
    ];

    return (
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center space-x-2 text-blue-800 mb-3">
          <Mic className="w-5 h-5" />
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide">Voice Analysis</p>
            <p className="text-xs text-blue-700">Technique: {analysis.technique}</p>
          </div>
        </div>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-700">
          {rows.map(
            (row) =>
              row.value !== null &&
              row.value !== undefined && (
                <div key={row.label} className="bg-white rounded-md px-3 py-2 shadow-sm">
                  <dt className="text-xs uppercase text-gray-500">{row.label}</dt>
                  <dd className="font-semibold text-gray-900">{row.value}</dd>
                </div>
              )
          )}
        </dl>
      </div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Mic className="w-12 h-12 text-red-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Voice Steganography</h1>
        </div>
        <p className="text-gray-600 text-lg max-w-3xl mx-auto">
          Hide and recover payloads inside spoken content by targeting voiced frames (detected via lightweight VAD) and
          encrypting with your password.
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Accepted format: mono WAV, 16-bit PCM, >=16 kHz sample rate.
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setMode('embed')}
            className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
              mode === 'embed' ? 'bg-white text-primary-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Embed Payload
          </button>
          <button
            onClick={() => setMode('extract')}
            className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
              mode === 'extract' ? 'bg-white text-primary-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            Extract Payload
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6 text-gray-900">
            {mode === 'embed' ? 'Hide Data in Voice' : 'Recover Hidden Data'}
          </h2>

          {/* Voice Upload */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {mode === 'embed' ? 'Cover Voice Recording' : 'Stego Voice Recording'}
            </label>
            <div className="file-drop-zone">
              <input
                ref={voiceFileRef}
                type="file"
                accept=".wav"
                onChange={handleVoiceFileChange}
                className="hidden"
              />
              <button onClick={() => voiceFileRef.current?.click()} className="w-full text-center">
                {voiceFile ? (
                  <div className="flex items-center justify-center space-x-2 text-red-600">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-medium">{voiceFile.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-2 text-gray-500">
                    <Upload className="w-8 h-8" />
                    <span>Click to select mono WAV file</span>
                    <span className="text-xs">16-bit PCM, >=16 kHz</span>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Secret Data */}
          {mode === 'embed' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Secret Data</label>
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
              <div>
                <label className="block text-xs text-gray-600 mb-1">Or Secret File</label>
                <div className="file-drop-zone">
                  <input ref={secretFileRef} type="file" onChange={handleSecretFileChange} className="hidden" />
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
                        <span className="text-sm">Click to upload a file</span>
                      </div>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Password */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Required for AES encryption"
                className="input-field pl-10"
              />
            </div>
          </div>

          {/* Actions */}
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
            <button onClick={resetForm} className="btn-secondary px-6">
              Reset
            </button>
          </div>
        </div>

        {/* Right Panel */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6 text-gray-900">Diagnostics & Results</h2>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">Error</span>
              </div>
              <p className="text-red-600 mt-2 whitespace-pre-wrap">{error}</p>
            </div>
          )}

          {renderAnalysis()}

          {result && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2 text-green-700 mb-3">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Success</span>
              </div>
              <p className="text-green-700 mb-4">{result.message}</p>

              {result.downloadUrl && (
                <button onClick={() => handleDownload(result.downloadUrl)} className="btn-primary flex items-center space-x-2">
                  <Download className="w-4 h-4" />
                  <span>Download Output</span>
                </button>
              )}

              {result.data && result.dataType === 'text' && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Extracted Text</label>
                  <div className="bg-white p-3 rounded-lg border">
                    <p className="text-gray-800 whitespace-pre-wrap">{result.data}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {!error && !result && !analysis && (
            <div className="text-center text-gray-500 py-12">
              <Mic className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Diagnostics and results will appear here after processing.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceStego;

