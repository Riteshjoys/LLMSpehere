import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { 
  ArrowLeft, 
  Send, 
  Copy, 
  Download, 
  Trash2, 
  MessageSquare,
  Settings,
  Zap,
  Brain,
  RefreshCw
} from 'lucide-react';

const TextGeneration = () => {
  const { api } = useAuth();
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [conversation, setConversation] = useState([]);
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [settings, setSettings] = useState({
    maxTokens: 1000,
    temperature: 0.7
  });

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await api.get('/api/providers');
      setProviders(response.data.providers);
      
      if (response.data.providers.length > 0) {
        setSelectedProvider(response.data.providers[0].name);
        setSelectedModel(response.data.providers[0].models[0] || '');
      }
    } catch (error) {
      toast.error('Failed to load providers');
    } finally {
      setLoadingProviders(false);
    }
  };

  const handleProviderChange = (providerName) => {
    const provider = providers.find(p => p.name === providerName);
    setSelectedProvider(providerName);
    setSelectedModel(provider?.models[0] || '');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || !selectedProvider || !selectedModel) return;

    setLoading(true);
    try {
      const response = await api.post('/api/generate/text', {
        provider_name: selectedProvider,
        model: selectedModel,
        prompt: prompt,
        max_tokens: settings.maxTokens,
        temperature: settings.temperature,
        session_id: sessionId
      });

      setConversation(prev => [
        ...prev,
        { role: 'user', content: prompt, timestamp: new Date().toISOString() },
        { role: 'assistant', content: response.data.generated_content, timestamp: new Date().toISOString() }
      ]);

      setSessionId(response.data.session_id);
      setPrompt('');
      toast.success('Text generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate text');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const handleDownload = (text) => {
    const element = document.createElement('a');
    const file = new Blob([text], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `generated-text-${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Downloaded successfully!');
  };

  const clearConversation = () => {
    setConversation([]);
    setSessionId('');
    toast.success('Conversation cleared');
  };

  const selectedProviderData = providers.find(p => p.name === selectedProvider);

  if (loadingProviders) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="loading-dots">
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="mt-4 text-gray-600">Loading providers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="btn-ghost mr-4">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Brain className="h-8 w-8 text-primary-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">Text Generation</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {providers.length} provider{providers.length !== 1 ? 's' : ''} available
              </span>
              <button onClick={loadProviders} className="btn-ghost">
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="card space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  <Settings className="inline h-5 w-5 mr-2" />
                  Configuration
                </h3>
                
                {/* Provider Selection */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    AI Provider
                  </label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => handleProviderChange(e.target.value)}
                    className="input-field"
                  >
                    {providers.map(provider => (
                      <option key={provider.name} value={provider.name}>
                        {provider.name}
                      </option>
                    ))}
                  </select>
                  
                  {selectedProviderData && (
                    <p className="text-xs text-gray-500">
                      {selectedProviderData.description}
                    </p>
                  )}
                </div>

                {/* Model Selection */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="input-field"
                  >
                    {selectedProviderData?.models.map(model => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Settings */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Max Tokens: {settings.maxTokens}
                  </label>
                  <input
                    type="range"
                    min="100"
                    max="4000"
                    value={settings.maxTokens}
                    onChange={(e) => setSettings(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                    className="w-full"
                  />
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Temperature: {settings.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={settings.temperature}
                    onChange={(e) => setSettings(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                </div>
              </div>

              {conversation.length > 0 && (
                <div className="pt-4 border-t border-gray-200">
                  <button
                    onClick={clearConversation}
                    className="btn-secondary w-full text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear Conversation
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="card h-full">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900">
                  <MessageSquare className="inline h-5 w-5 mr-2" />
                  Conversation
                </h2>
              </div>

              {/* Conversation Area */}
              <div className="flex-1 overflow-y-auto mb-4" style={{ height: '400px' }}>
                {conversation.length === 0 ? (
                  <div className="text-center py-12">
                    <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Start a conversation</p>
                    <p className="text-sm text-gray-500 mt-2">
                      Enter your prompt below to generate text
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {conversation.map((message, index) => (
                      <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-3xl ${message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100'} rounded-lg px-4 py-3`}>
                          <div className="whitespace-pre-wrap">{message.content}</div>
                          {message.role === 'assistant' && (
                            <div className="flex items-center justify-end space-x-2 mt-2">
                              <button
                                onClick={() => handleCopy(message.content)}
                                className="text-gray-500 hover:text-gray-700"
                              >
                                <Copy className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDownload(message.content)}
                                className="text-gray-500 hover:text-gray-700"
                              >
                                <Download className="h-4 w-4" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Input Form */}
              <form onSubmit={handleSubmit} className="border-t border-gray-200 pt-4">
                <div className="flex space-x-4">
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter your prompt here..."
                    className="textarea-field flex-1 min-h-[60px] max-h-[120px]"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !prompt.trim() || !selectedProvider || !selectedModel}
                    className="btn-primary self-end"
                  >
                    {loading ? (
                      <div className="loading-dots">
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextGeneration;