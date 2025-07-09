import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, PhotoIcon, SparklesIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

const ImageGeneration = () => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [numberOfImages, setNumberOfImages] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [imageHistory, setImageHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('generate');
  const navigate = useNavigate();

  useEffect(() => {
    fetchImageProviders();
    fetchImageHistory();
  }, []);

  const fetchImageProviders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/providers/image`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProviders(data.providers);
        
        // Select first provider by default
        if (data.providers.length > 0) {
          setSelectedProvider(data.providers[0].name);
          setSelectedModel(data.providers[0].models[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching image providers:', error);
      toast.error('Failed to load image providers');
    }
  };

  const fetchImageHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generations/images`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setImageHistory(data.generations);
      }
    } catch (error) {
      console.error('Error fetching image history:', error);
    }
  };

  const handleProviderChange = (providerName) => {
    setSelectedProvider(providerName);
    const provider = providers.find(p => p.name === providerName);
    if (provider && provider.models.length > 0) {
      setSelectedModel(provider.models[0]);
    }
  };

  const handleGenerateImage = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    if (!selectedProvider || !selectedModel) {
      toast.error('Please select a provider and model');
      return;
    }

    setIsGenerating(true);
    const loadingToast = toast.loading('Generating image...');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generate/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider_name: selectedProvider,
          model: selectedModel,
          prompt: prompt,
          number_of_images: numberOfImages
        })
      });

      if (response.ok) {
        const data = await response.json();
        const newImage = {
          id: Date.now(),
          image_base64: data.image_base64,
          prompt: data.prompt,
          provider: data.provider,
          model: data.model,
          created_at: new Date().toISOString()
        };
        
        setGeneratedImages(prev => [newImage, ...prev]);
        setImageHistory(prev => [newImage, ...prev]);
        toast.success('Image generated successfully!');
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Failed to generate image');
      }
    } catch (error) {
      console.error('Error generating image:', error);
      toast.error('Failed to generate image');
    } finally {
      setIsGenerating(false);
      toast.dismiss(loadingToast);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerateImage();
    }
  };

  const clearGeneratedImages = () => {
    setGeneratedImages([]);
  };

  const downloadImage = (imageBase64, prompt) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${imageBase64}`;
    link.download = `generated-image-${Date.now()}.png`;
    link.click();
  };

  const selectedProviderData = providers.find(p => p.name === selectedProvider);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeftIcon className="h-6 w-6" />
              </button>
              <div className="flex items-center">
                <PhotoIcon className="h-8 w-8 text-purple-600 mr-3" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Image Generation Studio</h1>
                  <p className="text-sm text-gray-500">Create stunning images with AI</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('generate')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'generate'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Generate Images
              </button>
              <button
                onClick={() => setActiveTab('gallery')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'gallery'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Gallery ({imageHistory.length})
              </button>
            </nav>
          </div>
        </div>

        {activeTab === 'generate' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Panel - Controls */}
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Settings</h3>
                
                {/* Provider Selection */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Image Provider
                  </label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => handleProviderChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Select a provider</option>
                    {providers.map((provider) => (
                      <option key={provider.name} value={provider.name}>
                        {provider.name} - {provider.description}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Model Selection */}
                {selectedProviderData && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model
                    </label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {selectedProviderData.models.map((model) => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Number of Images */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Images
                  </label>
                  <select
                    value={numberOfImages}
                    onChange={(e) => setNumberOfImages(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value={1}>1 image</option>
                    <option value={2}>2 images</option>
                    <option value={3}>3 images</option>
                    <option value={4}>4 images</option>
                  </select>
                </div>

                {/* Prompt Input */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prompt
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe the image you want to generate..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    rows={4}
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateImage}
                  disabled={isGenerating || !prompt.trim() || !selectedProvider}
                  className={`w-full flex items-center justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    isGenerating || !prompt.trim() || !selectedProvider
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500'
                  } transition-colors`}
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4 mr-2" />
                      Generate Image
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Right Panel - Generated Images */}
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Generated Images</h3>
                  {generatedImages.length > 0 && (
                    <button
                      onClick={clearGeneratedImages}
                      className="text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      Clear All
                    </button>
                  )}
                </div>

                <div className="space-y-4">
                  {generatedImages.length === 0 ? (
                    <div className="text-center py-12">
                      <PhotoIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">No images generated yet</p>
                      <p className="text-sm text-gray-400 mt-1">
                        Enter a prompt and click generate to create your first image
                      </p>
                    </div>
                  ) : (
                    generatedImages.map((image) => (
                      <div key={image.id} className="border border-gray-200 rounded-lg p-4">
                        <img
                          src={`data:image/png;base64,${image.image_base64}`}
                          alt={image.prompt}
                          className="w-full h-48 object-cover rounded-lg mb-3"
                        />
                        <p className="text-sm text-gray-700 mb-2">{image.prompt}</p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{image.provider} • {image.model}</span>
                          <button
                            onClick={() => downloadImage(image.image_base64, image.prompt)}
                            className="text-purple-600 hover:text-purple-800 font-medium"
                          >
                            Download
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'gallery' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Image Gallery</h3>
            
            {imageHistory.length === 0 ? (
              <div className="text-center py-12">
                <PhotoIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No images in your gallery yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Start generating images to build your collection
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {imageHistory.map((image, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <img
                      src={`data:image/png;base64,${image.image_base64}`}
                      alt={image.prompt}
                      className="w-full h-48 object-cover rounded-lg mb-3"
                    />
                    <p className="text-sm text-gray-700 mb-2 line-clamp-2">{image.prompt}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{image.provider} • {image.model}</span>
                      <button
                        onClick={() => downloadImage(image.image_base64, image.prompt)}
                        className="text-purple-600 hover:text-purple-800 font-medium"
                      >
                        Download
                      </button>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(image.created_at).toLocaleDateString()}
                    </p>
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

export default ImageGeneration;