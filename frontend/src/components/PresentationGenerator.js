import React, { useState, useEffect } from 'react';
import { 
  PresentationChartBarIcon, 
  DocumentTextIcon, 
  CloudDownloadIcon, 
  EyeIcon, 
  CogIcon, 
  PlusIcon,
  TrashIcon,
  PencilIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const PresentationGenerator = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [templates, setTemplates] = useState([]);
  const [presentations, setPresentations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [presentationData, setPresentationData] = useState({
    title: '',
    topic: '',
    slides: [],
    templateId: ''
  });
  const [previewPresentation, setPreviewPresentation] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    loadTemplates();
    loadPresentations();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/presentations/templates`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Error loading templates:', error);
      toast.error('Failed to load templates');
    }
  };

  const loadPresentations = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/presentations/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setPresentations(data.presentations || []);
    } catch (error) {
      console.error('Error loading presentations:', error);
      toast.error('Failed to load presentations');
    }
  };

  const handleCreatePresentation = async () => {
    if (!presentationData.title || !presentationData.topic || !selectedTemplate) {
      toast.error('Please fill in all required fields and select a template');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/presentations/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          title: presentationData.title,
          data: {
            topic: presentationData.topic,
            slides: presentationData.slides
          }
        })
      });

      const result = await response.json();
      
      if (response.ok) {
        toast.success('Presentation created successfully!');
        setPresentationData({ title: '', topic: '', slides: [], templateId: '' });
        setSelectedTemplate(null);
        loadPresentations();
      } else {
        throw new Error(result.detail || 'Failed to create presentation');
      }
    } catch (error) {
      console.error('Error creating presentation:', error);
      toast.error(error.message || 'Failed to create presentation');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPresentation = async (presentationId, format) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/presentations/${presentationId}/export/${format}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (format === 'google-slides') {
        const data = await response.json();
        window.open(data.url, '_blank');
        toast.success('Presentation exported to Google Slides!');
      } else {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `presentation.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        toast.success(`Presentation exported as ${format.toUpperCase()}!`);
      }
    } catch (error) {
      console.error('Error exporting presentation:', error);
      toast.error('Failed to export presentation');
    }
  };

  const handleDeletePresentation = async (presentationId) => {
    if (!window.confirm('Are you sure you want to delete this presentation?')) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/presentations/${presentationId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        toast.success('Presentation deleted successfully!');
        loadPresentations();
      } else {
        throw new Error('Failed to delete presentation');
      }
    } catch (error) {
      console.error('Error deleting presentation:', error);
      toast.error('Failed to delete presentation');
    }
  };

  const handlePreviewPresentation = async (presentationId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/presentations/${presentationId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        const presentation = await response.json();
        setPreviewPresentation(presentation);
        setShowPreview(true);
      } else {
        throw new Error('Failed to load presentation');
      }
    } catch (error) {
      console.error('Error loading presentation:', error);
      toast.error('Failed to load presentation');
    }
  };

  const TemplateCard = ({ template }) => (
    <div 
      className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
        selectedTemplate?.id === template.id 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={() => setSelectedTemplate(template)}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-gray-800">{template.name}</h3>
        <PresentationChartBarIcon className="w-5 h-5 text-gray-500" />
      </div>
      <p className="text-sm text-gray-600 mb-3">{template.description}</p>
      <div className="flex items-center justify-between">
        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
          {template.type}
        </span>
        <span className="text-xs text-gray-500">
          {template.slides?.length || 0} slides
        </span>
      </div>
    </div>
  );

  const PresentationCard = ({ presentation }) => (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800 truncate">{presentation.title}</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => handlePreviewPresentation(presentation.id)}
            className="p-1 text-gray-500 hover:text-blue-500 transition-colors"
            title="Preview"
          >
            <EyeIcon className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleDeletePresentation(presentation.id)}
            className="p-1 text-gray-500 hover:text-red-500 transition-colors"
            title="Delete"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {presentation.data?.topic || 'No topic specified'}
      </p>
      
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
          {presentation.slides?.length || 0} slides
        </span>
        <span className="text-xs text-gray-500">
          {new Date(presentation.created_at).toLocaleDateString()}
        </span>
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={() => handleExportPresentation(presentation.id, 'pptx')}
          className="flex-1 bg-blue-500 text-white text-xs py-2 px-3 rounded hover:bg-blue-600 transition-colors"
        >
          Export PPTX
        </button>
        <button
          onClick={() => handleExportPresentation(presentation.id, 'pdf')}
          className="flex-1 bg-green-500 text-white text-xs py-2 px-3 rounded hover:bg-green-600 transition-colors"
        >
          Export PDF
        </button>
      </div>
    </div>
  );

  const PreviewModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800">
            {previewPresentation?.title}
          </h2>
          <button
            onClick={() => setShowPreview(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-6">
          {previewPresentation?.slides?.map((slide, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-800">
                  Slide {index + 1}: {slide.title}
                </h3>
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {slide.layout}
                </span>
              </div>
              <div className="text-gray-600">
                {slide.content || 'No content specified'}
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={() => handleExportPresentation(previewPresentation.id, 'pptx')}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Export PPTX
          </button>
          <button
            onClick={() => handleExportPresentation(previewPresentation.id, 'pdf')}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
          >
            Export PDF
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <PresentationChartBarIcon className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold text-gray-800">Presentation Generator</h1>
        </div>
        <p className="text-gray-600">
          Create professional presentations with AI-powered content generation and templates
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6">
        <button
          onClick={() => setActiveTab('create')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'create'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Create Presentation
        </button>
        <button
          onClick={() => setActiveTab('library')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'library'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          My Presentations
        </button>
      </div>

      {activeTab === 'create' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Template Selection */}
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Choose Template</h2>
            <div className="grid grid-cols-1 gap-4 max-h-96 overflow-y-auto">
              {templates.map(template => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>
          </div>

          {/* Presentation Details */}
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Presentation Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  value={presentationData.title}
                  onChange={(e) => setPresentationData({
                    ...presentationData,
                    title: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter presentation title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic *
                </label>
                <textarea
                  value={presentationData.topic}
                  onChange={(e) => setPresentationData({
                    ...presentationData,
                    topic: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe the main topic of your presentation"
                  rows="3"
                />
              </div>

              {selectedTemplate && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Template: {selectedTemplate.name}
                  </label>
                  <p className="text-sm text-gray-600 mb-2">
                    {selectedTemplate.description}
                  </p>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Template includes {selectedTemplate.slides?.length || 0} slides:
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {selectedTemplate.slides?.map((slide, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                          <span>{slide.title}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <button
                onClick={handleCreatePresentation}
                disabled={loading || !selectedTemplate}
                className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
                  loading || !selectedTemplate
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {loading ? 'Creating...' : 'Create Presentation'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'library' && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">My Presentations</h2>
            <div className="text-sm text-gray-500">
              {presentations.length} presentation{presentations.length !== 1 ? 's' : ''}
            </div>
          </div>

          {presentations.length === 0 ? (
            <div className="text-center py-12">
              <PresentationChartBarIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">No presentations found</p>
              <button
                onClick={() => setActiveTab('create')}
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
              >
                Create Your First Presentation
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {presentations.map(presentation => (
                <PresentationCard key={presentation.id} presentation={presentation} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && <PreviewModal />}
    </div>
  );
};

export default PresentationGenerator;