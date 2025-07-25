import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Brain, 
  FileText, 
  Image, 
  Video, 
  Code, 
  Share2, 
  Presentation, 
  Sparkles,
  Settings,
  LogOut,
  User,
  BarChart3,
  Clock,
  Zap
} from 'lucide-react';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState([
    { name: 'Total Generations', value: '0', icon: Zap },
    { name: 'Active Sessions', value: '0', icon: Clock },
    { name: 'Providers Available', value: '0', icon: Brain },
    { name: 'Success Rate', value: '0%', icon: BarChart3 }
  ]);
  const [loading, setLoading] = useState(true);
  const [recentActivity, setRecentActivity] = useState([]);

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
        
        // Fetch all dashboard statistics in one call
        const response = await fetch(`${backendUrl}/api/dashboard/statistics`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data');
        }
        
        const data = await response.json();
        
        // Update stats
        setStats([
          { name: 'Total Generations', value: data.statistics.total_generations.toString(), icon: Zap },
          { name: 'Active Workflows', value: data.statistics.active_workflows.toString(), icon: Clock },
          { name: 'Providers Available', value: data.statistics.providers_available.toString(), icon: Brain },
          { name: 'Success Rate', value: `${data.statistics.success_rate}%`, icon: BarChart3 }
        ]);
        
        // Set recent activity
        setRecentActivity(data.recent_activity || []);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Keep default values on error
      } finally {
        setLoading(false);
      }
    };
    
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const tools = [
    {
      name: 'Text Generation',
      description: 'Generate high-quality text with multiple AI providers',
      icon: FileText,
      path: '/text-generation',
      color: 'bg-blue-500',
      available: true
    },
    {
      name: 'Image Generation',
      description: 'Create stunning images from text descriptions',
      icon: Image,
      path: '/image-generation',
      color: 'bg-green-500',
      available: true
    },
    {
      name: 'Video Generation',
      description: 'Generate videos from text and images',
      icon: Video,
      path: '/video-generation',
      color: 'bg-purple-500',
      available: true
    },
    {
      name: 'Code Assistant',
      description: 'AI-powered code generation and debugging',
      icon: Code,
      path: '/code-generation',
      color: 'bg-orange-500',
      available: true
    },
    {
      name: 'Social Media',
      description: 'Create engaging social media content',
      icon: Share2,
      path: '/social-media',
      color: 'bg-pink-500',
      available: true
    },
    {
      name: 'Workflow Automation',
      description: 'Create multi-step automated workflows',
      icon: Zap,
      path: '/workflows',
      color: 'bg-yellow-500',
      available: true
    },
    {
      name: 'Presentations',
      description: 'Generate professional presentations',
      icon: Presentation,
      path: '/presentations',
      color: 'bg-indigo-500',
      available: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">ContentForge</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">{user?.username}</span>
                {user?.is_admin && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    Admin
                  </span>
                )}
              </div>
              {user?.is_admin && (
                <Link to="/admin" className="btn-ghost">
                  <Settings className="h-4 w-4 mr-2" />
                  Admin
                </Link>
              )}
              <button onClick={logout} className="btn-ghost text-red-600 hover:bg-red-50">
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-600">
            Choose from our AI-powered tools to create amazing content
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Tools Grid */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Tools</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tools.map((tool) => (
              <div key={tool.name} className="card hover:shadow-md transition-shadow duration-200">
                <div className="flex items-start">
                  <div className={`flex-shrink-0 p-3 rounded-lg ${tool.color}`}>
                    <tool.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4 flex-1">
                    <h3 className="text-lg font-medium text-gray-900">{tool.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{tool.description}</p>
                    <div className="mt-4">
                      {tool.available ? (
                        <Link to={tool.path} className="btn-primary text-sm">
                          Get Started
                        </Link>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Coming Soon
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
          </div>
          {loading ? (
            <div className="text-center py-8">
              <div className="loading-dots">
                <div></div>
                <div></div>
                <div></div>
              </div>
              <p className="mt-4 text-gray-600">Loading activity...</p>
            </div>
          ) : recentActivity.length > 0 ? (
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.title}
                        </p>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          activity.type === 'text' ? 'bg-blue-100 text-blue-800' :
                          activity.type === 'image' ? 'bg-purple-100 text-purple-800' :
                          activity.type === 'video' ? 'bg-green-100 text-green-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {activity.type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1 truncate">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-2">
                        {activity.provider} • {new Date(activity.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                      activity.status === 'failed' ? 'bg-red-100 text-red-800' :
                      activity.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {activity.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No recent activity</p>
              <p className="text-sm text-gray-500 mt-2">
                Start generating content to see your activity here
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;