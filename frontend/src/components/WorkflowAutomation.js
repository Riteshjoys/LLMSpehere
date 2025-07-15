import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { PlayIcon, StopIcon, PlusIcon, DocumentDuplicateIcon, TrashIcon, EyeIcon, ClockIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import WorkflowScheduler from './WorkflowScheduler';

const WorkflowAutomation = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('workflows');
  const [workflows, setWorkflows] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    loadWorkflows();
    loadTemplates();
    loadExecutions();
  }, []);

  const loadWorkflows = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/workflows/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setWorkflows(response.data);
    } catch (error) {
      console.error('Error loading workflows:', error);
      toast.error('Failed to load workflows');
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/workflows/templates`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setTemplates(response.data);
    } catch (error) {
      console.error('Error loading templates:', error);
      toast.error('Failed to load templates');
    }
  };

  const loadExecutions = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/workflows/executions/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setExecutions(response.data);
    } catch (error) {
      console.error('Error loading executions:', error);
      toast.error('Failed to load executions');
    }
  };

  const executeWorkflow = async (workflowId, inputVariables = {}) => {
    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/workflows/${workflowId}/execute`, {
        workflow_id: workflowId,
        input_variables: inputVariables,
        run_name: `Manual run ${new Date().toLocaleString()}`
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Workflow execution started!');
      loadExecutions();
      setShowExecuteModal(false);
    } catch (error) {
      console.error('Error executing workflow:', error);
      toast.error('Failed to execute workflow');
    } finally {
      setLoading(false);
    }
  };

  const createFromTemplate = async (templateId, variables) => {
    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/workflows/from-template/${templateId}`, 
        variables, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Workflow created from template!');
      loadWorkflows();
      setShowTemplateModal(false);
    } catch (error) {
      console.error('Error creating from template:', error);
      toast.error('Failed to create workflow from template');
    } finally {
      setLoading(false);
    }
  };

  const duplicateWorkflow = async (workflowId) => {
    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/workflows/${workflowId}/duplicate`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Workflow duplicated!');
      loadWorkflows();
    } catch (error) {
      console.error('Error duplicating workflow:', error);
      toast.error('Failed to duplicate workflow');
    } finally {
      setLoading(false);
    }
  };

  const deleteWorkflow = async (workflowId) => {
    if (!window.confirm('Are you sure you want to delete this workflow?')) return;
    
    try {
      setLoading(true);
      await axios.delete(`${backendUrl}/api/workflows/${workflowId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Workflow deleted!');
      loadWorkflows();
    } catch (error) {
      console.error('Error deleting workflow:', error);
      toast.error('Failed to delete workflow');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getWorkflowTypeColor = (category) => {
    switch (category) {
      case 'marketing': return 'text-purple-600 bg-purple-100';
      case 'product': return 'text-blue-600 bg-blue-100';
      case 'development': return 'text-green-600 bg-green-100';
      case 'custom': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const renderWorkflowCard = (workflow) => (
    <div key={workflow.workflow_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{workflow.name}</h3>
          <p className="text-gray-600 text-sm mb-3">{workflow.description}</p>
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getWorkflowTypeColor(workflow.category)}`}>
              {workflow.category}
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(workflow.status)}`}>
              {workflow.status}
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{workflow.steps.length} steps</span>
            <span>{workflow.executions_count} executions</span>
            {workflow.last_execution_at && (
              <span>Last run: {new Date(workflow.last_execution_at).toLocaleDateString()}</span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setSelectedWorkflow(workflow);
              setShowExecuteModal(true);
            }}
            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            title="Execute Workflow"
          >
            <PlayIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => duplicateWorkflow(workflow.workflow_id)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Duplicate Workflow"
          >
            <DocumentDuplicateIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => deleteWorkflow(workflow.workflow_id)}
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete Workflow"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
      
      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex -space-x-2">
            {workflow.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                {tag}
              </span>
            ))}
            {workflow.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                +{workflow.tags.length - 3}
              </span>
            )}
          </div>
          <span className="text-xs text-gray-500">
            Created {new Date(workflow.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );

  const renderTemplateCard = (template) => (
    <div key={template.template_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
          <p className="text-gray-600 text-sm mb-3">{template.description}</p>
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getWorkflowTypeColor(template.category)}`}>
              {template.category}
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{template.steps.length} steps</span>
            <span>{Object.keys(template.variables).length} variables</span>
          </div>
        </div>
        <button
          onClick={() => {
            setSelectedTemplate(template);
            setShowTemplateModal(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Use Template
        </button>
      </div>
      
      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex -space-x-2">
            {template.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                {tag}
              </span>
            ))}
            {template.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                +{template.tags.length - 3}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderExecutionCard = (execution) => (
    <div key={execution.execution_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{execution.run_name}</h3>
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(execution.status)}`}>
              {execution.status}
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>Started: {new Date(execution.started_at).toLocaleString()}</span>
            {execution.duration_seconds && (
              <span>Duration: {Math.round(execution.duration_seconds)}s</span>
            )}
            <span>{execution.step_executions.length} steps</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="View Details"
          >
            <EyeIcon className="h-5 w-5" />
          </button>
          {execution.status === 'running' && (
            <button
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Stop Execution"
            >
              <StopIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>
      
      {execution.error_message && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{execution.error_message}</p>
        </div>
      )}
      
      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {execution.step_executions.map((step, index) => (
              <div
                key={index}
                className={`w-3 h-3 rounded-full ${
                  step.status === 'completed' ? 'bg-green-500' :
                  step.status === 'running' ? 'bg-blue-500' :
                  step.status === 'failed' ? 'bg-red-500' :
                  'bg-gray-300'
                }`}
                title={`Step ${index + 1}: ${step.status}`}
              />
            ))}
          </div>
          <span className="text-xs text-gray-500">
            {execution.step_executions.filter(s => s.status === 'completed').length} / {execution.step_executions.length} completed
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Workflow Automation</h1>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PlusIcon className="h-5 w-5" />
                Create Workflow
              </button>
              {user?.is_admin && (
                <button
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <ChartBarIcon className="h-5 w-5" />
                  Analytics
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'workflows', label: 'My Workflows', count: workflows.length },
              { id: 'schedules', label: 'Schedules', count: 0 },
              { id: 'templates', label: 'Templates', count: templates.length },
              { id: 'executions', label: 'Executions', count: executions.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'workflows' && (
          <div>
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">My Workflows</h2>
              <p className="text-gray-600">Create, manage, and execute your custom workflows</p>
            </div>
            
            {workflows.length === 0 ? (
              <div className="text-center py-12">
                <div className="mx-auto h-12 w-12 text-gray-400">
                  <ClockIcon className="h-12 w-12" />
                </div>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No workflows yet</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by creating your first workflow</p>
                <div className="mt-6">
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    Create Workflow
                  </button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workflows.map(renderWorkflowCard)}
              </div>
            )}
          </div>
        )}

        {activeTab === 'schedules' && (
          <WorkflowScheduler workflows={workflows} />
        )}

        {activeTab === 'templates' && (
          <div>
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Workflow Templates</h2>
              <p className="text-gray-600">Pre-built workflow templates to get you started quickly</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templates.map(renderTemplateCard)}
            </div>
          </div>
        )}

        {activeTab === 'executions' && (
          <div>
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Workflow Executions</h2>
              <p className="text-gray-600">Track the progress and history of your workflow runs</p>
            </div>
            
            {executions.length === 0 ? (
              <div className="text-center py-12">
                <div className="mx-auto h-12 w-12 text-gray-400">
                  <ChartBarIcon className="h-12 w-12" />
                </div>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No executions yet</h3>
                <p className="mt-1 text-sm text-gray-500">Execute a workflow to see the results here</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {executions.map(renderExecutionCard)}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Execute Modal */}
      {showExecuteModal && selectedWorkflow && (
        <ExecuteWorkflowModal
          workflow={selectedWorkflow}
          onClose={() => setShowExecuteModal(false)}
          onExecute={executeWorkflow}
        />
      )}

      {/* Template Modal */}
      {showTemplateModal && selectedTemplate && (
        <TemplateModal
          template={selectedTemplate}
          onClose={() => setShowTemplateModal(false)}
          onCreateFromTemplate={createFromTemplate}
        />
      )}
    </div>
  );
};

// Execute Workflow Modal Component
const ExecuteWorkflowModal = ({ workflow, onClose, onExecute }) => {
  const [variables, setVariables] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    onExecute(workflow.workflow_id, variables);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Execute Workflow</h3>
          <p className="text-gray-600 mb-4">Execute "{workflow.name}" workflow</p>
          
          <form onSubmit={handleSubmit}>
            {Object.entries(workflow.variables).map(([key, value]) => (
              <div key={key} className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {key}
                </label>
                <input
                  type="text"
                  value={variables[key] || ''}
                  onChange={(e) => setVariables({...variables, [key]: e.target.value})}
                  placeholder={typeof value === 'string' ? value : ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
            
            <div className="flex gap-3 mt-6">
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Execute
              </button>
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Template Modal Component
const TemplateModal = ({ template, onClose, onCreateFromTemplate }) => {
  const [variables, setVariables] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreateFromTemplate(template.template_id, variables);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create from Template</h3>
          <p className="text-gray-600 mb-4">Create a workflow from "{template.name}" template</p>
          
          <form onSubmit={handleSubmit}>
            {Object.entries(template.variables).map(([key, value]) => (
              <div key={key} className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {key}
                </label>
                <input
                  type="text"
                  value={variables[key] || ''}
                  onChange={(e) => setVariables({...variables, [key]: e.target.value})}
                  placeholder={typeof value === 'string' ? value : ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
            
            <div className="flex gap-3 mt-6">
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Create Workflow
              </button>
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default WorkflowAutomation;