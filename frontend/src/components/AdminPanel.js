import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { 
  ArrowLeft, 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Settings, 
  Brain,
  CheckCircle,
  XCircle,
  Code,
  Database,
  Globe
} from 'lucide-react';

const AdminPanel = () => {
  const { api, user } = useAuth();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProvider, setEditingProvider] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    base_url: '',
    headers: '{"Content-Type": "application/json", "Authorization": "Bearer YOUR_API_KEY"}',
    request_body_template: '{"model": "{model}", "messages": [{"role": "user", "content": "{prompt}"}], "max_tokens": {max_tokens}, "temperature": {temperature}}',
    response_parser: '{"content_path": "choices.0.message.content"}',
    models: '',
    is_active: true
  });

  useEffect(() => {
    if (user && !user.is_admin) {
      toast.error('Admin access required');
      return;
    }
    loadProviders();
  }, [user]);

  const loadProviders = async () => {
    try {
      const response = await api.get('/api/admin/providers');
      setProviders(response.data.providers);
    } catch (error) {
      toast.error('Failed to load providers');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
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
      is_active: true
    });
    setShowAddForm(false);
    setEditingProvider(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Validate JSON fields
      JSON.parse(formData.headers);
      JSON.parse(formData.request_body_template);
      JSON.parse(formData.response_parser);
    } catch (error) {
      toast.error('Invalid JSON format in configuration');
      return;
    }

    const payload = {
      ...formData,
      headers: JSON.parse(formData.headers),
      request_body_template: JSON.parse(formData.request_body_template),
      response_parser: JSON.parse(formData.response_parser),
      models: formData.models.split(',').map(m => m.trim()).filter(m => m)
    };

    try {
      if (editingProvider) {
        await api.put(`/api/admin/providers/${editingProvider.provider_id}`, payload);
        toast.success('Provider updated successfully');
      } else {
        await api.post('/api/admin/providers', payload);
        toast.success('Provider added successfully');
      }
      
      resetForm();
      loadProviders();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save provider');
    }
  };

  const handleEdit = (provider) => {
    setFormData({
      name: provider.name,
      description: provider.description,
      base_url: provider.base_url,
      headers: JSON.stringify(provider.headers, null, 2),
      request_body_template: JSON.stringify(provider.request_body_template, null, 2),
      response_parser: JSON.stringify(provider.response_parser, null, 2),
      models: provider.models.join(', '),
      is_active: provider.is_active
    });
    setEditingProvider(provider);
    setShowAddForm(true);
  };

  const handleDelete = async (providerId) => {
    if (!window.confirm('Are you sure you want to delete this provider?')) return;

    try {
      await api.delete(`/api/admin/providers/${providerId}`);
      toast.success('Provider deleted successfully');
      loadProviders();
    } catch (error) {
      toast.error('Failed to delete provider');
    }
  };

  const presetTemplates = [
    {
      name: 'OpenAI ChatGPT',
      description: 'OpenAI ChatGPT API integration',
      base_url: 'https://api.openai.com/v1/chat/completions',
      headers: '{"Content-Type": "application/json", "Authorization": "Bearer YOUR_OPENAI_API_KEY"}',
      request_body_template: '{"model": "{model}", "messages": [{"role": "user", "content": "{prompt}"}], "max_tokens": {max_tokens}, "temperature": {temperature}}',
      response_parser: '{"content_path": "choices.0.message.content"}',
      models: 'gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview'
    },
    {
      name: 'Anthropic Claude',
      description: 'Anthropic Claude API integration',
      base_url: 'https://api.anthropic.com/v1/messages',
      headers: '{"Content-Type": "application/json", "x-api-key": "YOUR_ANTHROPIC_API_KEY", "anthropic-version": "2023-06-01"}',
      request_body_template: '{"model": "{model}", "max_tokens": {max_tokens}, "messages": [{"role": "user", "content": "{prompt}"}]}',
      response_parser: '{"content_path": "content.0.text"}',
      models: 'claude-3-haiku-20240307, claude-3-sonnet-20240229, claude-3-opus-20240229'
    },
    {
      name: 'Google Gemini',
      description: 'Google Gemini API integration',
      base_url: 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
      headers: '{"Content-Type": "application/json"}',
      request_body_template: '{"contents": [{"parts": [{"text": "{prompt}"}]}], "generationConfig": {"temperature": {temperature}, "maxOutputTokens": {max_tokens}}}',
      response_parser: '{"content_path": "candidates.0.content.parts.0.text"}',
      models: 'gemini-pro, gemini-pro-vision'
    }
  ];

  const usePreset = (preset) => {
    setFormData({
      ...formData,
      ...preset,
      is_active: true
    });
  };

  if (!user?.is_admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">Access Denied</h2>
          <p className="text-gray-600 mt-2">You need admin privileges to access this page</p>
          <Link to="/" className="btn-primary mt-4">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="loading-dots">
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="mt-4 text-gray-600">Loading admin panel...</p>
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
              <Settings className="h-8 w-8 text-primary-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">Admin Panel</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {providers.length} provider{providers.length !== 1 ? 's' : ''} configured
              </span>
              <button
                onClick={() => setShowAddForm(true)}
                className="btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Provider
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Add/Edit Provider Form */}
        {showAddForm && (
          <div className="card mb-8">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingProvider ? 'Edit Provider' : 'Add New Provider'}
              </h3>
              <button onClick={resetForm} className="btn-ghost">
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Preset Templates */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Quick Start Templates</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {presetTemplates.map((preset) => (
                  <button
                    key={preset.name}
                    onClick={() => usePreset(preset)}
                    className="text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="font-medium text-gray-900">{preset.name}</div>
                    <div className="text-sm text-gray-600 mt-1">{preset.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="input-field"
                    placeholder="e.g., OpenAI GPT-4"
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
                    className="input-field"
                    placeholder="Brief description of the provider"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Globe className="inline h-4 w-4 mr-1" />
                  Base URL
                </label>
                <input
                  type="url"
                  name="base_url"
                  value={formData.base_url}
                  onChange={handleInputChange}
                  required
                  className="input-field"
                  placeholder="https://api.provider.com/v1/chat/completions"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available Models (comma-separated)
                </label>
                <input
                  type="text"
                  name="models"
                  value={formData.models}
                  onChange={handleInputChange}
                  required
                  className="input-field"
                  placeholder="gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Database className="inline h-4 w-4 mr-1" />
                  HTTP Headers (JSON)
                </label>
                <textarea
                  name="headers"
                  value={formData.headers}
                  onChange={handleInputChange}
                  rows={4}
                  className="textarea-field font-mono text-sm"
                  placeholder='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_API_KEY"}'
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Code className="inline h-4 w-4 mr-1" />
                  Request Body Template (JSON)
                </label>
                <textarea
                  name="request_body_template"
                  value={formData.request_body_template}
                  onChange={handleInputChange}
                  rows={6}
                  className="textarea-field font-mono text-sm"
                  placeholder='{"model": "{model}", "messages": [{"role": "user", "content": "{prompt}"}], "max_tokens": {max_tokens}, "temperature": {temperature}}'
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use variables: {'{model}'}, {'{prompt}'}, {'{max_tokens}'}, {'{temperature}'}, {'{messages}'}
                </p>
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
                  className="textarea-field font-mono text-sm"
                  placeholder='{"content_path": "choices.0.message.content"}'
                />
                <p className="text-xs text-gray-500 mt-1">
                  Specify the JSONPath to extract the generated content from the response
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                <label className="text-sm font-medium text-gray-700">
                  Active (available for users)
                </label>
              </div>

              <div className="flex justify-end space-x-4">
                <button type="button" onClick={resetForm} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  <Save className="h-4 w-4 mr-2" />
                  {editingProvider ? 'Update' : 'Add'} Provider
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Providers List */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">
              <Brain className="inline h-5 w-5 mr-2" />
              Configured Providers
            </h3>
          </div>

          {providers.length === 0 ? (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No providers configured</p>
              <p className="text-sm text-gray-500 mt-2">
                Add your first AI provider to get started
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Provider</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Models</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Created</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {providers.map((provider) => (
                    <tr key={provider.provider_id} className="border-b border-gray-100">
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium text-gray-900">{provider.name}</div>
                          <div className="text-sm text-gray-600">{provider.description}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-wrap gap-1">
                          {provider.models.slice(0, 3).map((model) => (
                            <span key={model} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {model}
                            </span>
                          ))}
                          {provider.models.length > 3 && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              +{provider.models.length - 3} more
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {provider.is_active ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <XCircle className="h-3 w-3 mr-1" />
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {new Date(provider.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => handleEdit(provider)}
                            className="btn-ghost text-blue-600 hover:bg-blue-50"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(provider.provider_id)}
                            className="btn-ghost text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;