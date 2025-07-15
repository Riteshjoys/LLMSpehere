import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { 
  Share2, 
  ArrowLeft, 
  Copy, 
  Download, 
  Hash, 
  Sparkles,
  Settings,
  History,
  BarChart3,
  RefreshCw,
  Twitter,
  Instagram,
  Linkedin,
  MessageCircle,
  Users,
  TrendingUp
} from 'lucide-react';

const SocialMediaGeneration = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('generate');
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('twitter');
  const [contentType, setContentType] = useState('post');
  const [prompt, setPrompt] = useState('');
  const [tone, setTone] = useState('professional');
  const [targetAudience, setTargetAudience] = useState('general');
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [hashtagCount, setHashtagCount] = useState(5);
  const [includeEmojis, setIncludeEmojis] = useState(true);
  const [includeCallToAction, setIncludeCallToAction] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentHistory, setContentHistory] = useState([]);
  const [platformConfigs, setPlatformConfigs] = useState({});
  const [templates, setTemplates] = useState({});
  const [analytics, setAnalytics] = useState({});

  // Platform icons mapping
  const platformIcons = {
    twitter: Twitter,
    instagram: Instagram,
    linkedin: Linkedin,
    facebook: MessageCircle,
    tiktok: TrendingUp,
    youtube: Users
  };

  useEffect(() => {
    fetchProviders();
    fetchPlatformConfigs();
    fetchContentHistory();
    fetchAnalytics();
  }, []);

  useEffect(() => {
    if (selectedPlatform) {
      fetchTemplates(selectedPlatform);
      updateContentType();
    }
  }, [selectedPlatform]);

  const fetchProviders = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/providers/text`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProviders(data.providers || []);
        if (data.providers.length > 0) {
          setSelectedProvider(data.providers[0].name);
          setSelectedModel(data.providers[0].models[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const fetchPlatformConfigs = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-media/platforms`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlatformConfigs(data.platforms || {});
      }
    } catch (error) {
      console.error('Error fetching platform configs:', error);
    }
  };

  const fetchTemplates = async (platform) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-media/templates?platform=${platform}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || {});
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchContentHistory = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-media/generations`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContentHistory(data.generations || []);
      }
    } catch (error) {
      console.error('Error fetching content history:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-media/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const updateContentType = () => {
    const platformConfig = platformConfigs[selectedPlatform];
    if (platformConfig && platformConfig.content_types.length > 0) {
      const currentType = platformConfig.content_types.includes(contentType) 
        ? contentType 
        : platformConfig.content_types[0];
      setContentType(currentType);
    }
  };

  const handleProviderChange = (e) => {
    const providerName = e.target.value;
    setSelectedProvider(providerName);
    
    const provider = providers.find(p => p.name === providerName);
    if (provider && provider.models.length > 0) {
      setSelectedModel(provider.models[0]);
    }
  };

  const handleGenerateContent = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    if (!selectedProvider || !selectedModel) {
      toast.error('Please select a provider and model');
      return;
    }

    setIsGenerating(true);
    setGeneratedContent(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-media/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          provider_name: selectedProvider,
          model: selectedModel,
          platform: selectedPlatform,
          content_type: contentType,
          prompt: prompt,
          tone: tone,
          target_audience: targetAudience,
          include_hashtags: includeHashtags,
          hashtag_count: hashtagCount,
          include_emojis: includeEmojis,
          include_call_to_action: includeCallToAction
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedContent(data);
        toast.success('Content generated successfully!');
        fetchContentHistory(); // Refresh history
        fetchAnalytics(); // Refresh analytics
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Failed to generate content');
      }
    } catch (error) {
      console.error('Error generating content:', error);
      toast.error('Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const downloadContent = (content, filename) => {
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename || 'social-media-content.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Content downloaded!');
  };

  const formatHashtags = (hashtags) => {
    return hashtags.map(tag => tag.startsWith('#') ? tag : `#${tag}`).join(' ');
  };

  const currentPlatformConfig = platformConfigs[selectedPlatform];
  const currentContentTypes = currentPlatformConfig?.content_types || [];
  const PlatformIcon = platformIcons[selectedPlatform];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                Back to Dashboard
              </button>
              <div className="flex items-center space-x-2">
                <Share2 className="h-8 w-8 text-pink-600" />
                <h1 className="text-2xl font-bold text-gray-900">Social Media Generator</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg mb-8 max-w-lg">
          <button
            onClick={() => setActiveTab('generate')}
            className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-colors ${
              activeTab === 'generate' 
                ? 'bg-white text-pink-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Sparkles className="h-4 w-4" />
            <span>Generate</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-colors ${
              activeTab === 'history' 
                ? 'bg-white text-pink-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <History className="h-4 w-4" />
            <span>History</span>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-colors ${
              activeTab === 'analytics' 
                ? 'bg-white text-pink-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            <span>Analytics</span>
          </button>
        </div>

        {/* Generate Tab */}
        {activeTab === 'generate' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Settings Panel */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <Settings className="h-5 w-5 mr-2" />
                  Generation Settings
                </h2>

                {/* Platform Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Platform
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.keys(platformConfigs).map((platform) => {
                      const Icon = platformIcons[platform];
                      return (
                        <button
                          key={platform}
                          onClick={() => setSelectedPlatform(platform)}
                          className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-md border transition-colors ${
                            selectedPlatform === platform
                              ? 'bg-pink-100 border-pink-500 text-pink-700'
                              : 'bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100'
                          }`}
                        >
                          <Icon className="h-4 w-4" />
                          <span className="text-sm capitalize">{platform}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Content Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content Type
                  </label>
                  <select
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                  >
                    {currentContentTypes.map((type) => (
                      <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Provider Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    AI Provider
                  </label>
                  <select
                    value={selectedProvider}
                    onChange={handleProviderChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                  >
                    {providers.map((provider) => (
                      <option key={provider.name} value={provider.name}>
                        {provider.name} - {provider.description}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Model Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                  >
                    {providers
                      .find(p => p.name === selectedProvider)
                      ?.models.map((model) => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))}
                  </select>
                </div>

                {/* Tone */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tone
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="formal">Formal</option>
                    <option value="humorous">Humorous</option>
                  </select>
                </div>

                {/* Target Audience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    placeholder="e.g., entrepreneurs, designers, students"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                  />
                </div>

                {/* Advanced Options */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700">Include Hashtags</label>
                    <input
                      type="checkbox"
                      checked={includeHashtags}
                      onChange={(e) => setIncludeHashtags(e.target.checked)}
                      className="h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded"
                    />
                  </div>

                  {includeHashtags && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Hashtag Count: {hashtagCount}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="15"
                        value={hashtagCount}
                        onChange={(e) => setHashtagCount(parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700">Include Emojis</label>
                    <input
                      type="checkbox"
                      checked={includeEmojis}
                      onChange={(e) => setIncludeEmojis(e.target.checked)}
                      className="h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700">Include Call-to-Action</label>
                    <input
                      type="checkbox"
                      checked={includeCallToAction}
                      onChange={(e) => setIncludeCallToAction(e.target.checked)}
                      className="h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded"
                    />
                  </div>
                </div>

                {/* Platform Info */}
                {currentPlatformConfig && (
                  <div className="bg-gray-50 p-3 rounded-lg text-sm">
                    <div className="flex items-center space-x-2 mb-2">
                      <PlatformIcon className="h-4 w-4 text-gray-600" />
                      <span className="font-medium text-gray-700 capitalize">{selectedPlatform}</span>
                    </div>
                    <div className="space-y-1 text-gray-600">
                      <p>Max length: {currentPlatformConfig.max_length} characters</p>
                      <p>Content types: {currentPlatformConfig.content_types.join(', ')}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Content Generation Panel */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Content Generation</h2>

                {/* Prompt Input */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content Prompt
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe what you want to create content about..."
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateContent}
                  disabled={isGenerating || !prompt.trim()}
                  className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-md font-medium transition-colors ${
                    isGenerating || !prompt.trim()
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-pink-600 hover:bg-pink-700 text-white'
                  }`}
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Generating Content...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5" />
                      <span>Generate Content</span>
                    </>
                  )}
                </button>

                {/* Generated Content */}
                {generatedContent && (
                  <div className="mt-8 space-y-6">
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Content</h3>
                      
                      {/* Content Display */}
                      <div className="bg-gray-50 p-4 rounded-lg mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <PlatformIcon className="h-4 w-4 text-gray-600" />
                            <span className="text-sm font-medium text-gray-700 capitalize">
                              {generatedContent.platform} {generatedContent.content_type}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => copyToClipboard(generatedContent.content)}
                              className="text-gray-500 hover:text-gray-700"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => downloadContent(generatedContent.content, 'social-media-content.txt')}
                              className="text-gray-500 hover:text-gray-700"
                            >
                              <Download className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        <div className="whitespace-pre-wrap text-gray-800">
                          {generatedContent.content}
                        </div>
                      </div>

                      {/* Hashtags */}
                      {generatedContent.hashtags && generatedContent.hashtags.length > 0 && (
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-900 flex items-center">
                              <Hash className="h-4 w-4 mr-2 text-blue-600" />
                              Hashtags ({generatedContent.hashtags.length})
                            </h4>
                            <button
                              onClick={() => copyToClipboard(formatHashtags(generatedContent.hashtags))}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                          </div>
                          <div className="text-blue-800">
                            {formatHashtags(generatedContent.hashtags)}
                          </div>
                        </div>
                      )}

                      {/* Metadata */}
                      <div className="text-sm text-gray-500 space-y-1">
                        <p><strong>Provider:</strong> {generatedContent.provider}</p>
                        <p><strong>Model:</strong> {generatedContent.model}</p>
                        <p><strong>Generated:</strong> {new Date(generatedContent.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Content History</h2>
              <button
                onClick={fetchContentHistory}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </button>
            </div>
            
            {contentHistory.length === 0 ? (
              <div className="text-center py-12">
                <History className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                <p className="text-gray-500">No content generated yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {contentHistory.map((item, index) => {
                  const PlatformIcon = platformIcons[item.platform];
                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <PlatformIcon className="h-4 w-4 text-gray-600" />
                          <span className="text-sm font-medium text-gray-700 capitalize">
                            {item.platform} {item.content_type}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(item.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => copyToClipboard(item.generated_content)}
                            className="text-gray-500 hover:text-gray-700"
                          >
                            <Copy className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => downloadContent(item.generated_content, `${item.platform}-${item.content_type}-${index + 1}.txt`)}
                            className="text-gray-500 hover:text-gray-700"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        <strong>Prompt:</strong> {item.prompt}
                      </div>
                      <div className="bg-gray-50 p-3 rounded text-sm whitespace-pre-wrap">
                        {item.generated_content}
                      </div>
                      {item.hashtags && item.hashtags.length > 0 && (
                        <div className="mt-2 text-sm text-blue-600">
                          {formatHashtags(item.hashtags)}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Total Generations */}
              <div className="bg-pink-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Sparkles className="h-8 w-8 text-pink-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-pink-600">Total Generations</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.total_generations || 0}</p>
                  </div>
                </div>
              </div>

              {/* By Platform */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">By Platform</h3>
                <div className="space-y-1">
                  {(analytics.by_platform || []).map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-blue-700 capitalize">{item.platform}</span>
                      <span className="text-blue-900 font-medium">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* By Content Type */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-medium text-green-900 mb-2">By Content Type</h3>
                <div className="space-y-1">
                  {(analytics.by_content_type || []).map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-green-700 capitalize">{item.content_type}</span>
                      <span className="text-green-900 font-medium">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialMediaGeneration;