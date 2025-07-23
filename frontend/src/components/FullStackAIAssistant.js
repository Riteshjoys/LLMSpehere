import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  RocketLaunchIcon, 
  CpuChipIcon, 
  CircleStackIcon, 
  CloudArrowUpIcon,
  ChartBarIcon,
  CodeBracketIcon,
  BoltIcon,
  ShieldCheckIcon,
  PlayIcon,
  PauseIcon,
  TrashIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const FullStackAIAssistant = () => {
  const { user, api } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [projectForm, setProjectForm] = useState({
    name: '',
    description: '',
    target_users: '',
    expected_scale: 'medium',
    frontend_preference: 'React',
    backend_preference: 'FastAPI',
    database_requirements: 'High performance PostgreSQL with Redis caching',
    performance_requirements: {
      response_time: '<200ms',
      throughput: '10000 requests/second',
      availability: '99.9%'
    },
    security_requirements: 'standard',
    deployment_targets: ['docker', 'kubernetes'],
    timeline: '',
    budget: ''
  });
  const [capabilities, setCapabilities] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkPremiumAccess();
    fetchCapabilities();
    fetchProjects();
  }, []);

  const checkPremiumAccess = async () => {
    // This will be handled by the backend route automatically
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/fullstack-ai/capabilities`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.status === 403) {
        toast.error('Premium subscription required for Full Stack AI Assistant');
        return false;
      }

      return response.ok;
    } catch (error) {
      console.error('Error checking premium access:', error);
      return false;
    }
  };

  const fetchCapabilities = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/capabilities`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCapabilities(data);
      }
    } catch (error) {
      console.error('Error fetching capabilities:', error);
    }
  };

  const fetchProjects = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/projects`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      } else if (response.status === 403) {
        toast.error('Premium subscription required');
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const createProject = async (e) => {
    e.preventDefault();
    
    if (!projectForm.name.trim() || !projectForm.description.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/project/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(projectForm)
      });

      const data = await response.json();

      if (data.success) {
        toast.success('Project initialized successfully!');
        setIsCreatingProject(false);
        setProjectForm({
          name: '', description: '', target_users: '', expected_scale: 'medium',
          frontend_preference: 'React', backend_preference: 'FastAPI',
          database_requirements: 'High performance PostgreSQL with Redis caching',
          performance_requirements: { response_time: '<200ms', throughput: '10000 requests/second', availability: '99.9%' },
          security_requirements: 'standard', deployment_targets: ['docker', 'kubernetes'],
          timeline: '', budget: ''
        });
        fetchProjects();
        
        // Auto-select the new project
        setTimeout(() => {
          setSelectedProject(data.project_id);
          setActiveTab('project');
        }, 1000);
      } else {
        toast.error(data.message || 'Failed to create project');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const executeTask = async (projectId, taskId = null) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/project/${projectId}/execute-task`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          project_id: projectId,
          task_id: taskId,
          execution_mode: 'auto',
          force_execution: false
        })
      });

      const data = await response.json();

      if (data.success) {
        toast.success('Task execution started!');
        // Refresh project status
        fetchProjects();
      } else {
        toast.error(data.message || 'Failed to execute task');
      }
    } catch (error) {
      console.error('Error executing task:', error);
      toast.error('Failed to execute task');
    }
  };

  const pauseProject = async (projectId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/project/${projectId}/pause`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Project paused successfully');
        fetchProjects();
      } else {
        toast.error('Failed to pause project');
      }
    } catch (error) {
      console.error('Error pausing project:', error);
      toast.error('Failed to pause project');
    }
  };

  const resumeProject = async (projectId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/project/${projectId}/resume`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Project resumed successfully');
        fetchProjects();
      } else {
        toast.error('Failed to resume project');
      }
    } catch (error) {
      console.error('Error resuming project:', error);
      toast.error('Failed to resume project');
    }
  };

  const deleteProject = async (projectId) => {
    if (!window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/fullstack-ai/project/${projectId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Project deleted successfully');
        if (selectedProject === projectId) {
          setSelectedProject(null);
        }
        fetchProjects();
      } else {
        toast.error('Failed to delete project');
      }
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Failed to delete project');
    }
  };

  const getStatusIcon = (phase) => {
    switch (phase) {
      case 'planning': return <DocumentTextIcon className="h-5 w-5 text-blue-500" />;
      case 'analysis': return <ChartBarIcon className="h-5 w-5 text-purple-500" />;
      case 'design': return <CpuChipIcon className="h-5 w-5 text-green-500" />;
      case 'development': return <CodeBracketIcon className="h-5 w-5 text-orange-500" />;
      case 'testing': return <ShieldCheckIcon className="h-5 w-5 text-red-500" />;
      case 'deployment': return <CloudArrowUpIcon className="h-5 w-5 text-indigo-500" />;
      case 'completed': return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      default: return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 90) return 'bg-green-500';
    if (percentage >= 70) return 'bg-blue-500';
    if (percentage >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const currentProject = projects.find(p => p.project_id === selectedProject);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <RocketLaunchIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Full Stack AI Assistant</h1>
                <p className="mt-2 text-gray-600">
                  Build production-ready applications with AI-powered development
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {user?.is_admin && (
                <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  Admin
                </div>
              )}
              <div className="bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium">
                Premium Feature
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('projects')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'projects'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                My Projects ({projects.length})
              </button>
              <button
                onClick={() => setActiveTab('create')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'create'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Create Project
              </button>
              {currentProject && (
                <button
                  onClick={() => setActiveTab('project')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'project'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {currentProject.project_name}
                </button>
              )}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && capabilities && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Capabilities */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Assistant Capabilities</h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3 flex items-center">
                    <CpuChipIcon className="h-5 w-5 text-blue-500 mr-2" />
                    Project Management
                  </h3>
                  <ul className="space-y-2">
                    {capabilities.project_management.map((item, index) => (
                      <li key={index} className="flex items-center text-gray-600">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3 flex items-center">
                    <CodeBracketIcon className="h-5 w-5 text-green-500 mr-2" />
                    Development
                  </h3>
                  <ul className="space-y-2">
                    {capabilities.development.map((item, index) => (
                      <li key={index} className="flex items-center text-gray-600">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3 flex items-center">
                    <CircleStackIcon className="h-5 w-5 text-purple-500 mr-2" />
                    Database
                  </h3>
                  <ul className="space-y-2">
                    {capabilities.database.map((item, index) => (
                      <li key={index} className="flex items-center text-gray-600">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3 flex items-center">
                    <CloudArrowUpIcon className="h-5 w-5 text-indigo-500 mr-2" />
                    Deployment
                  </h3>
                  <ul className="space-y-2">
                    {capabilities.deployment.map((item, index) => (
                      <li key={index} className="flex items-center text-gray-600">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Supported Technologies */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Supported Technologies</h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3">Frontend</h3>
                  <div className="flex flex-wrap gap-2">
                    {capabilities.supported_technologies.frontend.map((tech, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3">Backend</h3>
                  <div className="flex flex-wrap gap-2">
                    {capabilities.supported_technologies.backend.map((tech, index) => (
                      <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3">Databases</h3>
                  <div className="flex flex-wrap gap-2">
                    {capabilities.supported_technologies.databases.map((db, index) => (
                      <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                        {db}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-3">Deployment</h3>
                  <div className="flex flex-wrap gap-2">
                    {capabilities.supported_technologies.deployment.map((deploy, index) => (
                      <span key={index} className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">
                        {deploy}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-2 flex items-center">
                  <BoltIcon className="h-5 w-5 text-yellow-500 mr-2" />
                  Production-Ready Features
                </h3>
                <ul className="text-gray-600 text-sm space-y-1">
                  <li>• Optimized for 1000M+ records and high concurrent users</li>
                  <li>• Automated testing with 90%+ coverage</li>
                  <li>• Container orchestration with Kubernetes</li>
                  <li>• Performance monitoring and alerting</li>
                  <li>• Security best practices implementation</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="space-y-6">
            {projects.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <RocketLaunchIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
                <p className="text-gray-600 mb-6">
                  Create your first full-stack project to get started with AI-powered development
                </p>
                <button
                  onClick={() => setActiveTab('create')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create First Project
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <div key={project.project_id} className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(project.current_phase)}
                        <h3 className="text-lg font-semibold text-gray-900">{project.project_name}</h3>
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => {
                            setSelectedProject(project.project_id);
                            setActiveTab('project');
                          }}
                          className="text-blue-600 hover:text-blue-800"
                          title="View Project"
                        >
                          <ChartBarIcon className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => executeTask(project.project_id)}
                          className="text-green-600 hover:text-green-800"
                          title="Execute Next Task"
                        >
                          <PlayIcon className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => deleteProject(project.project_id)}
                          className="text-red-600 hover:text-red-800"
                          title="Delete Project"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>

                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {project.description}
                    </p>

                    <div className="space-y-3">
                      {/* Progress Bar */}
                      <div>
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(project.progress_percentage)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(project.progress_percentage)}`}
                            style={{ width: `${project.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="flex justify-between text-sm text-gray-600">
                        <div className="flex items-center">
                          <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1" />
                          {project.completed_tasks} completed
                        </div>
                        <div className="flex items-center">
                          {project.failed_tasks > 0 && (
                            <>
                              <XCircleIcon className="h-4 w-4 text-red-500 mr-1" />
                              {project.failed_tasks} failed
                            </>
                          )}
                        </div>
                      </div>

                      {/* Phase and Last Activity */}
                      <div className="flex justify-between text-xs text-gray-500">
                        <span className="capitalize">{project.current_phase.replace('_', ' ')}</span>
                        <span>{formatDate(project.last_activity)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Create Project Tab */}
        {activeTab === 'create' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Create New Full-Stack Project</h2>
              
              <form onSubmit={createProject} className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Basic Information */}
                  <div className="space-y-6">
                    <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Project Name *
                      </label>
                      <input
                        type="text"
                        required
                        value={projectForm.name}
                        onChange={(e) => setProjectForm({...projectForm, name: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="My Awesome App"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description *
                      </label>
                      <textarea
                        required
                        rows={4}
                        value={projectForm.description}
                        onChange={(e) => setProjectForm({...projectForm, description: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Describe your project, its purpose, key features, and target audience..."
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Target Users
                      </label>
                      <input
                        type="text"
                        value={projectForm.target_users}
                        onChange={(e) => setProjectForm({...projectForm, target_users: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Small businesses, developers, general public"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expected Scale
                      </label>
                      <select
                        value={projectForm.expected_scale}
                        onChange={(e) => setProjectForm({...projectForm, expected_scale: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="small">Small (&lt;1K users, &lt;1M records)</option>
                        <option value="medium">Medium (&lt;100K users, &lt;100M records)</option>
                        <option value="large">Large (&lt;1M users, &lt;1B records)</option>
                        <option value="enterprise">Enterprise (&gt;1M users, &gt;1B records)</option>
                      </select>
                    </div>
                  </div>

                  {/* Technical Preferences */}
                  <div className="space-y-6">
                    <h3 className="text-lg font-medium text-gray-900">Technical Preferences</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Frontend Framework
                      </label>
                      <select
                        value={projectForm.frontend_preference}
                        onChange={(e) => setProjectForm({...projectForm, frontend_preference: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="React">React</option>
                        <option value="Vue">Vue.js</option>
                        <option value="Angular">Angular</option>
                        <option value="Next.js">Next.js</option>
                        <option value="Svelte">Svelte</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Backend Technology
                      </label>
                      <select
                        value={projectForm.backend_preference}
                        onChange={(e) => setProjectForm({...projectForm, backend_preference: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="FastAPI">FastAPI (Python)</option>
                        <option value="Node.js">Node.js</option>
                        <option value="Django">Django (Python)</option>
                        <option value="Spring Boot">Spring Boot (Java)</option>
                        <option value="Go">Go</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Database Requirements
                      </label>
                      <textarea
                        rows={3}
                        value={projectForm.database_requirements}
                        onChange={(e) => setProjectForm({...projectForm, database_requirements: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Describe your data storage needs, performance requirements, etc."
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Security Level
                      </label>
                      <select
                        value={projectForm.security_requirements}
                        onChange={(e) => setProjectForm({...projectForm, security_requirements: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="basic">Basic</option>
                        <option value="standard">Standard</option>
                        <option value="high">High</option>
                        <option value="enterprise">Enterprise</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Deployment and Timeline */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timeline (Optional)
                    </label>
                    <input
                      type="text"
                      value={projectForm.timeline}
                      onChange={(e) => setProjectForm({...projectForm, timeline: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., 3 months, ASAP, by end of quarter"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Budget (Optional)
                    </label>
                    <input
                      type="text"
                      value={projectForm.budget}
                      onChange={(e) => setProjectForm({...projectForm, budget: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., $10k, Limited, No constraints"
                    />
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex items-center justify-end space-x-4 pt-6 border-t">
                  <button
                    type="button"
                    onClick={() => setActiveTab('projects')}
                    className="text-gray-600 hover:text-gray-800 px-4 py-2"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                        <span>Creating Project...</span>
                      </>
                    ) : (
                      <>
                        <RocketLaunchIcon className="h-5 w-5" />
                        <span>Create Project</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FullStackAIAssistant;