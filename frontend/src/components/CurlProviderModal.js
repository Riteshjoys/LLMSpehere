import React, { useState } from 'react';
import { XMarkIcon, ClipboardDocumentIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

const CurlProviderModal = ({ isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    curl_command: '',
    models: '',
    provider_type: 'text',
    is_active: true
  });

  const [isLoading, setIsLoading] = useState(false);

  const sampleCurlCommands = {
    text: {
      openai: `curl -X POST "https://api.openai.com/v1/chat/completions" \\
-H "Authorization: Bearer YOUR_API_KEY" \\
-H "Content-Type: application/json" \\
-d '{
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "Hello world"}],
  "max_tokens": 150,
  "temperature": 0.7
}'`,
      anthropic: `curl -X POST "https://api.anthropic.com/v1/messages" \\
-H "x-api-key: YOUR_API_KEY" \\
-H "Content-Type: application/json" \\
-H "anthropic-version: 2023-06-01" \\
-d '{
  "model": "claude-3-sonnet-20240229",
  "max_tokens": 150,
  "messages": [{"role": "user", "content": "Hello world"}]
}'`,
      custom: `curl -X POST "https://api.example.com/v1/generate" \\
-H "Authorization: Bearer YOUR_API_KEY" \\
-H "Content-Type: application/json" \\
-d '{
  "prompt": "Hello world",
  "model": "custom-model",
  "max_tokens": 150,
  "temperature": 0.7
}'`
    },
    image: {
      openai: `curl -X POST "https://api.openai.com/v1/images/generations" \\
-H "Authorization: Bearer YOUR_API_KEY" \\
-H "Content-Type: application/json" \\
-d '{
  "prompt": "A beautiful sunset over mountains",
  "model": "dall-e-3",
  "n": 1,
  "size": "1024x1024"
}'`,
      stable: `curl -X POST "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image" \\
-H "Authorization: Bearer YOUR_API_KEY" \\
-H "Content-Type: application/json" \\
-d '{
  "text_prompts": [{"text": "A beautiful sunset over mountains"}],
  "cfg_scale": 7,
  "height": 1024,
  "width": 1024,
  "samples": 1
}'`,
      custom: `curl -X POST "https://api.example.com/v1/generate-image" \\
-H "Authorization: Bearer YOUR_API_KEY" \\
-H "Content-Type: application/json" \\
-d '{
  "prompt": "A beautiful sunset over mountains",
  "model": "custom-image-model",
  "num_images": 1
}'`
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validate required fields
      if (!formData.name || !formData.description || !formData.curl_command || !formData.models) {
        toast.error('Please fill in all required fields');
        return;
      }

      const modelsArray = formData.models.split(',').map(model => model.trim()).filter(Boolean);
      
      const providerData = {
        ...formData,
        models: modelsArray
      };

      await onSave(providerData);
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        curl_command: '',
        models: '',
        provider_type: 'text',
        is_active: true
      });
      
      onClose();
      toast.success('Provider added successfully!');
    } catch (error) {
      toast.error(error.message || 'Failed to add provider');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const copySampleCommand = (command) => {
    navigator.clipboard.writeText(command);
    toast.success('Copied to clipboard!');
  };

  const fillSampleCommand = (command) => {
    setFormData(prev => ({
      ...prev,
      curl_command: command
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Add Provider from Curl Command</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Panel - Form */}
            <div>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="e.g., OpenAI, Claude, Custom Provider"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <input
                    type="text"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Brief description of the provider"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider Type *
                  </label>
                  <select
                    name="provider_type"
                    value={formData.provider_type}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="text">Text Generation</option>
                    <option value="image">Image Generation</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Supported Models *
                  </label>
                  <input
                    type="text"
                    name="models"
                    value={formData.models}
                    onChange={handleChange}
                    placeholder="gpt-4, gpt-3.5-turbo, claude-3-opus (comma-separated)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter model names separated by commas
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Curl Command *
                  </label>
                  <textarea
                    name="curl_command"
                    value={formData.curl_command}
                    onChange={handleChange}
                    placeholder="Paste your curl command here..."
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    The system will automatically parse headers, URL, and request body
                  </p>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">
                    Active (available for use)
                  </label>
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {isLoading ? 'Adding...' : 'Add Provider'}
                  </button>
                </div>
              </form>
            </div>

            {/* Right Panel - Sample Commands */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Sample Curl Commands</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">
                    {formData.provider_type === 'text' ? 'Text Generation' : 'Image Generation'} Examples
                  </h4>
                  
                  {Object.entries(sampleCurlCommands[formData.provider_type]).map(([key, command]) => (
                    <div key={key} className="border border-gray-200 rounded-lg p-4 mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="text-sm font-medium text-gray-900 capitalize">{key}</h5>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => copySampleCommand(command)}
                            className="text-xs text-gray-600 hover:text-gray-800 flex items-center"
                          >
                            <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                            Copy
                          </button>
                          <button
                            onClick={() => fillSampleCommand(command)}
                            className="text-xs text-blue-600 hover:text-blue-800"
                          >
                            Use This
                          </button>
                        </div>
                      </div>
                      <pre className="text-xs text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                        {command}
                      </pre>
                    </div>
                  ))}
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-800 mb-2">💡 Pro Tips:</h4>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• Replace YOUR_API_KEY with your actual API key</li>
                    <li>• The system will automatically detect prompt fields</li>
                    <li>• Standard parameters (max_tokens, temperature) are added automatically</li>
                    <li>• Make sure your API endpoint is publicly accessible</li>
                    <li>• Test your curl command in terminal first</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurlProviderModal;