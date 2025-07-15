import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { Video, Play, Download, History, Settings, ArrowLeft, Clock } from 'lucide-react';

const VideoGeneration = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('generate');
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState(null);
  const [videoHistory, setVideoHistory] = useState([]);
  const [duration, setDuration] = useState(5);
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [resolution, setResolution] = useState('720p');

  // Fetch video providers
  useEffect(() => {
    fetchProviders();
    fetchVideoHistory();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/providers/video`, {
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

  const fetchVideoHistory = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generations/videos`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setVideoHistory(data.generations || []);
      }
    } catch (error) {
      console.error('Error fetching video history:', error);
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

  const handleGenerateVideo = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    if (!selectedProvider || !selectedModel) {
      toast.error('Please select a provider and model');
      return;
    }

    setIsGenerating(true);
    setGeneratedVideo(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generate/video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          provider_name: selectedProvider,
          model: selectedModel,
          prompt: prompt,
          duration: duration,
          aspect_ratio: aspectRatio,
          resolution: resolution
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedVideo(data);
        toast.success('Video generated successfully!');
        fetchVideoHistory(); // Refresh history
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Failed to generate video');
      }
    } catch (error) {
      console.error('Error generating video:', error);
      toast.error('Failed to generate video');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadVideo = (videoBase64, filename) => {
    try {
      const byteCharacters = atob(videoBase64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'video/mp4' });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || 'generated-video.mp4';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('Video downloaded successfully!');
    } catch (error) {
      console.error('Error downloading video:', error);
      toast.error('Failed to download video');
    }
  };

  const VideoPlayer = ({ videoBase64, videoUrl, className = "" }) => {
    if (videoBase64) {
      const videoSrc = `data:video/mp4;base64,${videoBase64}`;
      return (
        <video 
          src={videoSrc} 
          controls 
          className={`w-full rounded-lg shadow-lg ${className}`}
          style={{ maxHeight: '400px' }}
        />
      );
    } else if (videoUrl) {
      return (
        <video 
          src={videoUrl} 
          controls 
          className={`w-full rounded-lg shadow-lg ${className}`}
          style={{ maxHeight: '400px' }}
        />
      );
    }
    return null;
  };

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
                <Video className="h-8 w-8 text-purple-600" />
                <h1 className="text-2xl font-bold text-gray-900">Video Generation</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg mb-8 max-w-md">
          <button
            onClick={() => setActiveTab('generate')}
            className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-colors ${
              activeTab === 'generate' 
                ? 'bg-white text-purple-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Play className="h-4 w-4" />
            <span>Generate</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md transition-colors ${
              activeTab === 'history' 
                ? 'bg-white text-purple-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <History className="h-4 w-4" />
            <span>History</span>
          </button>
        </div>

        {/* Generate Tab */}
        {activeTab === 'generate' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Controls Panel */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Video Generation</h2>
              
              {/* Provider Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={handleProviderChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {providers.map((provider) => (
                    <option key={provider.name} value={provider.name}>
                      {provider.name} - {provider.description}
                    </option>
                  ))}
                </select>
              </div>

              {/* Model Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
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

              {/* Video Settings */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Video Settings
                </h3>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Duration</label>
                    <select
                      value={duration}
                      onChange={(e) => setDuration(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value={3}>3s</option>
                      <option value={5}>5s</option>
                      <option value={10}>10s</option>
                      <option value={15}>15s</option>
                      <option value={30}>30s</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Aspect Ratio</label>
                    <select
                      value={aspectRatio}
                      onChange={(e) => setAspectRatio(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="16:9">16:9</option>
                      <option value="9:16">9:16</option>
                      <option value="1:1">1:1</option>
                      <option value="4:3">4:3</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Resolution</label>
                    <select
                      value={resolution}
                      onChange={(e) => setResolution(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="480p">480p</option>
                      <option value="720p">720p</option>
                      <option value="1080p">1080p</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Prompt Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe the video you want to generate..."
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerateVideo}
                disabled={isGenerating || !prompt.trim()}
                className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-md font-medium transition-colors ${
                  isGenerating || !prompt.trim()
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-purple-600 hover:bg-purple-700 text-white'
                }`}
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Generating Video...</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Generate Video</span>
                  </>
                )}
              </button>

              {isGenerating && (
                <div className="mt-4 text-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 inline mr-1" />
                  Video generation may take several minutes. Please wait...
                </div>
              )}
            </div>

            {/* Results Panel */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Generated Video</h2>
              
              {generatedVideo ? (
                <div className="space-y-4">
                  <VideoPlayer 
                    videoBase64={generatedVideo.video_base64}
                    videoUrl={generatedVideo.video_url}
                  />
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900 mb-2">Video Details</h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p><strong>Provider:</strong> {generatedVideo.provider}</p>
                      <p><strong>Model:</strong> {generatedVideo.model}</p>
                      <p><strong>Prompt:</strong> {generatedVideo.prompt}</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => downloadVideo(generatedVideo.video_base64, `video-${Date.now()}.mp4`)}
                    className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    <span>Download Video</span>
                  </button>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Video className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <p className="text-gray-500">Your generated video will appear here</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Video History</h2>
            
            {videoHistory.length === 0 ? (
              <div className="text-center py-12">
                <History className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                <p className="text-gray-500">No video generations yet</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {videoHistory.map((video, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4">
                    <VideoPlayer 
                      videoBase64={video.video_base64}
                      videoUrl={video.video_url}
                      className="mb-3"
                    />
                    
                    <div className="space-y-2 text-sm">
                      <p className="font-medium text-gray-900 truncate">{video.prompt}</p>
                      <p className="text-gray-600">
                        <strong>Provider:</strong> {video.provider_name}
                      </p>
                      <p className="text-gray-600">
                        <strong>Model:</strong> {video.model}
                      </p>
                      <p className="text-gray-600">
                        <strong>Created:</strong> {new Date(video.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <button
                      onClick={() => downloadVideo(video.video_base64, `video-${index + 1}.mp4`)}
                      className="w-full mt-3 flex items-center justify-center space-x-2 py-2 px-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoGeneration;