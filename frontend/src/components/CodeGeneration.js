import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CodeBracketIcon, DocumentTextIcon, BugAntIcon, CogIcon, EyeIcon, DocumentCheckIcon, BeakerIcon, BookOpenIcon, CubeIcon } from '@heroicons/react/24/outline';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import toast from 'react-hot-toast';

const CodeGeneration = () => {
  const { user } = useAuth();
  const [providers, setProviders] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [requestTypes, setRequestTypes] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [selectedRequestType, setSelectedRequestType] = useState('generate');
  const [prompt, setPrompt] = useState('');
  const [maxTokens, setMaxTokens] = useState(4000);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('generate');

  useEffect(() => {
    fetchProviders();
    fetchLanguages();
    fetchRequestTypes();
    fetchHistory();
  }, []);

  const fetchProviders = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/code/providers`);
      const data = await response.json();
      setProviders(data);
      if (data.length > 0) {
        setSelectedProvider(data[0].provider);
        setSelectedModel(data[0].models[0].id);
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const fetchLanguages = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/code/languages`);
      const data = await response.json();
      setLanguages(data);
    } catch (error) {
      console.error('Error fetching languages:', error);
    }
  };

  const fetchRequestTypes = async () => {
    try {
      const response = await fetch('/api/code/request-types');
      const data = await response.json();
      setRequestTypes(data);
    } catch (error) {
      console.error('Error fetching request types:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/code/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setLoading(true);
    setResponse('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/code/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          provider: selectedProvider,
          model: selectedModel,
          request_type: selectedRequestType,
          language: selectedLanguage,
          prompt: prompt,
          max_tokens: maxTokens
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setResponse(data.response);
        toast.success('Code generated successfully!');
        fetchHistory(); // Refresh history
      } else {
        toast.error(data.detail || 'Generation failed');
      }
    } catch (error) {
      console.error('Error generating code:', error);
      toast.error('Generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleClearResponse = () => {
    setResponse('');
  };

  const handleCopyResponse = () => {
    navigator.clipboard.writeText(response);
    toast.success('Response copied to clipboard!');
  };

  const getRequestTypeIcon = (type) => {
    const icons = {
      generate: CodeBracketIcon,
      debug: BugAntIcon,
      optimize: CogIcon,
      refactor: CubeIcon,
      review: EyeIcon,
      documentation: DocumentTextIcon,
      test: BeakerIcon,
      explain: BookOpenIcon,
      architecture: DocumentCheckIcon
    };
    return icons[type] || CodeBracketIcon;
  };

  const getLanguageDisplayName = (langId) => {
    const lang = languages.find(l => l.id === langId);
    return lang ? lang.name : langId;
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const currentProvider = providers.find(p => p.provider === selectedProvider);
  const currentModels = currentProvider ? currentProvider.models : [];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Code Generation Assistant</h1>
              <p className="mt-2 text-gray-600">
                Generate, debug, optimize, and analyze code with AI assistance
              </p>
            </div>
            {user?.is_admin && (
              <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                Admin
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('generate')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'generate'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Generate Code
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                History
              </button>
            </nav>
          </div>
        </div>

        {activeTab === 'generate' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Panel - Configuration */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration</h2>
                
                {/* Provider Selection */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    AI Provider
                  </label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => {
                      setSelectedProvider(e.target.value);
                      const provider = providers.find(p => p.provider === e.target.value);
                      if (provider && provider.models.length > 0) {
                        setSelectedModel(provider.models[0].id);
                      }
                    }}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {providers.map((provider) => (
                      <option key={provider.provider} value={provider.provider}>
                        {provider.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Model Selection */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {currentModels.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                  {currentModels.find(m => m.id === selectedModel) && (
                    <p className="text-sm text-gray-500 mt-1">
                      {currentModels.find(m => m.id === selectedModel).description}
                    </p>
                  )}
                </div>

                {/* Request Type */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Request Type
                  </label>
                  <select
                    value={selectedRequestType}
                    onChange={(e) => setSelectedRequestType(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {requestTypes.map((type) => (
                      <option key={type.id} value={type.id}>
                        {type.name}
                      </option>
                    ))}
                  </select>
                  {requestTypes.find(t => t.id === selectedRequestType) && (
                    <p className="text-sm text-gray-500 mt-1">
                      {requestTypes.find(t => t.id === selectedRequestType).description}
                    </p>
                  )}
                </div>

                {/* Language Selection */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Programming Language
                  </label>
                  <select
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {languages.map((language) => (
                      <option key={language.id} value={language.id}>
                        {language.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Max Tokens */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Tokens: {maxTokens}
                  </label>
                  <input
                    type="range"
                    min="1000"
                    max="8000"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-1">
                    <span>1000</span>
                    <span>8000</span>
                  </div>
                </div>
              </div>

              {/* Prompt Input */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Prompt</h2>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your code generation request..."
                  className="w-full h-40 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
                <div className="mt-4 flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    {prompt.length} characters
                  </span>
                  <button
                    onClick={handleGenerate}
                    disabled={loading || !prompt.trim()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                        <span>Generating...</span>
                      </>
                    ) : (
                      <>
                        <CodeBracketIcon className="h-4 w-4" />
                        <span>Generate Code</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Right Panel - Response */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Response</h2>
                  {response && (
                    <div className="flex space-x-2">
                      <button
                        onClick={handleCopyResponse}
                        className="text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded-lg border border-gray-300 hover:bg-gray-50"
                      >
                        Copy
                      </button>
                      <button
                        onClick={handleClearResponse}
                        className="text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded-lg border border-gray-300 hover:bg-gray-50"
                      >
                        Clear
                      </button>
                    </div>
                  )}
                </div>
                
                {loading && (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
                  </div>
                )}
                
                {!loading && !response && (
                  <div className="h-64 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-500">
                    Generated code will appear here
                  </div>
                )}
                
                {response && (
                  <div className="border rounded-lg overflow-hidden">
                    <SyntaxHighlighter
                      language={selectedLanguage}
                      style={atomOneDark}
                      customStyle={{
                        margin: 0,
                        borderRadius: 0,
                        fontSize: '14px',
                        lineHeight: '1.4'
                      }}
                    >
                      {response}
                    </SyntaxHighlighter>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Generation History</h2>
            {history.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No code generations found. Start by generating some code!
              </div>
            ) : (
              <div className="space-y-4">
                {history.map((item) => {
                  const RequestTypeIcon = getRequestTypeIcon(item.request_type);
                  return (
                    <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <RequestTypeIcon className="h-5 w-5 text-gray-500" />
                          <span className="font-medium text-gray-900">
                            {requestTypes.find(t => t.id === item.request_type)?.name || item.request_type}
                          </span>
                          <span className="text-sm text-gray-500">
                            {getLanguageDisplayName(item.language)}
                          </span>
                          <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                            {item.provider}
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {formatTimestamp(item.created_at)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                        {item.prompt}
                      </p>
                      <div className="bg-gray-50 rounded p-3">
                        <SyntaxHighlighter
                          language={item.language}
                          style={atomOneDark}
                          customStyle={{
                            margin: 0,
                            borderRadius: 4,
                            fontSize: '12px',
                            lineHeight: '1.3',
                            maxHeight: '200px',
                            overflow: 'auto'
                          }}
                        >
                          {item.response}
                        </SyntaxHighlighter>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeGeneration;