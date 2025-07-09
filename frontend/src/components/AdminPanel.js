import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import CurlProviderModal from './CurlProviderModal';
import { 
  ArrowLeftIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  CheckCircleIcon,
  XCircleIcon,
  CodeBracketIcon,
  ServerIcon,
  GlobeAltIcon,
  CogIcon,
  CommandLineIcon
} from '@heroicons/react/24/outline';

const AdminPanel = () => {
  const { api, user } = useAuth();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showCurlModal, setShowCurlModal] = useState(false);
  const [editingProvider, setEditingProvider] = useState(null);
  const [activeTab, setActiveTab] = useState('providers');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    base_url: '',
    headers: '{"Content-Type": "application/json", "Authorization": "Bearer YOUR_API_KEY"}',
    request_body_template: '{"model": "{model}", "messages": [{"role": "user", "content": "{prompt}"}], "max_tokens": {max_tokens}, "temperature": {temperature}}',
    response_parser: '{"content_path": "choices.0.message.content"}',
    models: '',
    provider_type: 'text',
    is_active: true
  });

  useEffect(() => {
    if (user && !user.is_admin) {
      toast.error('Admin access required');
      return;
    }
    loadProviders();
  }, [user, loadProviders]);

  const loadProviders = useCallback(async () => {
    try {
      const response = await api.get('/api/admin/providers');
      setProviders(response.data.providers);
    } catch (error) {
      console.error('Error loading providers:', error);
      toast.error('Failed to load providers');
    } finally {
      setLoading(false);
    }
  }, [api]);

  const handleAddProvider = async (e) => {
    e.preventDefault();
    try {
      const modelsArray = formData.models.split(',').map(m => m.trim()).filter(Boolean);
      
      const providerData = {
        ...formData,
        headers: JSON.parse(formData.headers),
        request_body_template: JSON.parse(formData.request_body_template),
        response_parser: JSON.parse(formData.response_parser),
        models: modelsArray
      };

      if (editingProvider) {
        await api.put(`/api/admin/providers/${editingProvider.provider_id}`, providerData);
        toast.success('Provider updated successfully');
      } else {
        await api.post('/api/admin/providers', providerData);
        toast.success('Provider added successfully');
      }

      setShowAddForm(false);
      setEditingProvider(null);
      resetForm();
      loadProviders();
    } catch (error) {
      console.error('Error saving provider:', error);
      toast.error('Failed to save provider');
    }
  };

  const handleAddCurlProvider = async (curlData) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/providers/curl`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(curlData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add provider');
      }

      loadProviders();
    } catch (error) {
      throw error;
    }
  };

  const handleDeleteProvider = async (providerId) => {
    if (window.confirm('Are you sure you want to delete this provider?')) {
      try {
        await api.delete(`/api/admin/providers/${providerId}`);
        toast.success('Provider deleted successfully');
        loadProviders();
      } catch (error) {
        console.error('Error deleting provider:', error);
        toast.error('Failed to delete provider');
      }
    }
  };

  const handleEditProvider = (provider) => {
    setEditingProvider(provider);
    setFormData({
      name: provider.name,
      description: provider.description,
      base_url: provider.base_url,
      headers: JSON.stringify(provider.headers, null, 2),
      request_body_template: JSON.stringify(provider.request_body_template, null, 2),
      response_parser: JSON.stringify(provider.response_parser, null, 2),
      models: provider.models.join(', '),
      provider_type: provider.provider_type || 'text',
      is_active: provider.is_active
    });
    setShowAddForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      base_url: '',
      headers: '{"Content-Type": "application/json", "Authorization": "Bearer YOUR_API_KEY"}',
      request_body_template: '{"model": "{model}", "messages": [{"role": "user", "content": "{prompt}"}], "max_tokens": {max_tokens}, "temperature": {temperature}}',
      response_parser: '{"content_path": "choices.0.message.content"}',
      models: '',
      provider_type: 'text',
      is_active: true
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const presetTemplates = {
    text: {
      openai: {
        name: 'OpenAI',
        description: 'OpenAI GPT models',
        base_url: 'https://api.openai.com/v1/chat/completions',
        headers: '{"Authorization": "Bearer YOUR_OPENAI_API_KEY", "Content-Type": "application/json"}',
        request_body_template: '{"model": "{model}", "messages": [{"role": "user", "content": "{prompt}"}], "max_tokens": {max_tokens}, "temperature": {temperature}}',
        response_parser: '{"content_path": "choices.0.message.content"}',
        models: 'gpt-4o, gpt-4o-mini, gpt-3.5-turbo'
      },
      claude: {
        name: 'Claude',
        description: 'Anthropic Claude models',
        base_url: 'https://api.anthropic.com/v1/messages',
        headers: '{"x-api-key": "YOUR_ANTHROPIC_API_KEY", "Content-Type": "application/json", "anthropic-version": "2023-06-01"}',
        request_body_template: '{"model": "{model}", "max_tokens": {max_tokens}, "messages": [{"role": "user", "content": "{prompt}"}]}',
        response_parser: '{"content_path": "content.0.text"}',
        models: 'claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307'
      },
      gemini: {
        name: 'Gemini',
        description: 'Google Gemini models',
        base_url: 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=YOUR_GOOGLE_API_KEY',
        headers: '{"Content-Type": "application/json"}',
        request_body_template: '{"contents": [{"parts": [{"text": "{prompt}"}]}], "generationConfig": {"temperature": {temperature}, "maxOutputTokens": {max_tokens}}}',
        response_parser: '{"content_path": "candidates.0.content.parts.0.text"}',
        models: 'gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro'
      }
    },
    image: {
      openai: {
        name: 'DALL-E',
        description: 'OpenAI DALL-E image generation',
        base_url: 'https://api.openai.com/v1/images/generations',
        headers: '{"Authorization": "Bearer YOUR_OPENAI_API_KEY", "Content-Type": "application/json"}',
        request_body_template: '{"prompt": "{prompt}", "model": "{model}", "n": {number_of_images}, "size": "1024x1024"}',
        response_parser: '{"content_path": "data.0.url"}',
        models: 'dall-e-3, dall-e-2'
      },
      stability: {
        name: 'Stable Diffusion',
        description: 'Stability AI Stable Diffusion',
        base_url: 'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
        headers: '{"Authorization": "Bearer YOUR_STABILITY_API_KEY", "Content-Type": "application/json"}',
        request_body_template: '{"text_prompts": [{"text": "{prompt}"}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": {number_of_images}}',
        response_parser: '{"content_path": "artifacts.0.base64"}',
        models: 'stable-diffusion-xl-1024-v1-0, stable-diffusion-v1-6'
      }
    }
  };

  const fillPresetTemplate = (template) => {
    setFormData(prev => ({
      ...prev,
      ...template
    }));
  };

  const textProviders = providers.filter(p => p.provider_type === 'text' || !p.provider_type);
  const imageProviders = providers.filter(p => p.provider_type === 'image');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-gray-400 hover:text-gray-600 mr-4">
                <ArrowLeftIcon className="h-6 w-6" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <CogIcon className="h-8 w-8 text-blue-600 mr-3" />
                Admin Panel
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAddForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Provider
              </button>
              <button
                onClick={() => setShowCurlModal(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center"
              >
                <CommandLineIcon className="h-4 w-4 mr-2" />
                Add from Curl
              </button>
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
                onClick={() => setActiveTab('providers')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'providers'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                All Providers ({providers.length})
              </button>
              <button
                onClick={() => setActiveTab('text')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'text'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Text Providers ({textProviders.length})
              </button>
              <button
                onClick={() => setActiveTab('image')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'image'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Image Providers ({imageProviders.length})
              </button>
            </nav>
          </div>
        </div>

        {/* Provider List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              {activeTab === 'providers' ? 'All Providers' : 
               activeTab === 'text' ? 'Text Generation Providers' : 
               'Image Generation Providers'}
            </h3>
            
            {(() => {
              let displayProviders = providers;
              if (activeTab === 'text') displayProviders = textProviders;
              if (activeTab === 'image') displayProviders = imageProviders;

              return displayProviders.length === 0 ? (
                <div className="text-center py-12">
                  <ServerIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No providers</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Get started by adding a new provider
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {displayProviders.map((provider) => (
                    <div key={provider.provider_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-lg font-medium text-gray-900">{provider.name}</h4>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            provider.provider_type === 'image' 
                              ? 'bg-purple-100 text-purple-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {provider.provider_type === 'image' ? 'Image' : 'Text'}
                          </span>
                          {provider.is_active ? (
                            <CheckCircleIcon className="h-5 w-5 text-green-500" />
                          ) : (
                            <XCircleIcon className="h-5 w-5 text-red-500" />
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{provider.description}</p>
                      <div className="flex items-center text-sm text-gray-500 mb-3">
                        <GlobeAltIcon className="h-4 w-4 mr-1" />
                        <span className="truncate">{provider.base_url}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          {provider.models?.length || 0} models
                        </span>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEditProvider(provider)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteProvider(provider.provider_id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Add/Edit Provider Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingProvider ? 'Edit Provider' : 'Add New Provider'}
              </h2>
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setEditingProvider(null);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircleIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Panel - Form */}
                <div>
                  <form onSubmit={handleAddProvider} className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Provider Name
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                      </label>
                      <input
                        type="text"
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Provider Type
                      </label>
                      <select
                        name="provider_type"
                        value={formData.provider_type}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="text">Text Generation</option>
                        <option value="image">Image Generation</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Base URL
                      </label>
                      <input
                        type="url"
                        name="base_url"
                        value={formData.base_url}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Models (comma-separated)
                      </label>
                      <input
                        type="text"
                        name="models"
                        value={formData.models}
                        onChange={handleInputChange}
                        placeholder="gpt-4, gpt-3.5-turbo, claude-3-opus"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Headers (JSON)
                      </label>
                      <textarea
                        name="headers"
                        value={formData.headers}
                        onChange={handleInputChange}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Request Body Template (JSON)
                      </label>
                      <textarea
                        name="request_body_template"
                        value={formData.request_body_template}
                        onChange={handleInputChange}
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Response Parser (JSON)
                      </label>
                      <textarea
                        name="response_parser"
                        value={formData.response_parser}
                        onChange={handleInputChange}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        required
                      />
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        name="is_active"
                        checked={formData.is_active}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Active
                      </label>
                    </div>

                    <div className="flex justify-end space-x-4">
                      <button
                        type="button"
                        onClick={() => {
                          setShowAddForm(false);
                          setEditingProvider(null);
                          resetForm();
                        }}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                      >
                        {editingProvider ? 'Update' : 'Add'} Provider
                      </button>
                    </div>
                  </form>
                </div>

                {/* Right Panel - Preset Templates */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Start Templates</h3>
                  <div className="space-y-4">
                    {Object.entries(presetTemplates[formData.provider_type]).map(([key, template]) => (
                      <div key={key} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-md font-medium text-gray-900">{template.name}</h4>
                          <button
                            type="button"
                            onClick={() => fillPresetTemplate(template)}
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            Use Template
                          </button>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                        <div className="text-xs text-gray-500">
                          Models: {template.models}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-800 mb-2">💡 Template Variables</h4>
                    <div className="text-xs text-blue-700 space-y-1">
                      <p>• <code>{`{prompt}`}</code> - User's input prompt</p>
                      <p>• <code>{`{model}`}</code> - Selected model name</p>
                      <p>• <code>{`{max_tokens}`}</code> - Maximum tokens to generate</p>
                      <p>• <code>{`{temperature}`}</code> - Temperature setting</p>
                      {formData.provider_type === 'image' && (
                        <p>• <code>{`{number_of_images}`}</code> - Number of images to generate</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Curl Provider Modal */}
      <CurlProviderModal
        isOpen={showCurlModal}
        onClose={() => setShowCurlModal(false)}
        onSave={handleAddCurlProvider}
      />
    </div>
  );
};

export default AdminPanel;