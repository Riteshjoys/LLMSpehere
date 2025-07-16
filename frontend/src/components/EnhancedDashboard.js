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
  Zap,
  TrendingUp,
  Activity,
  DollarSign,
  Award,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  Eye,
  PieChart,
  LineChart
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { Line, Pie, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const EnhancedDashboard = () => {
  const { user, logout, api } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [insights, setInsights] = useState([]);
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Fetch enhanced analytics
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/analytics/dashboard/enhanced?days=${timeRange}`);
        setAnalytics(response.data);
        
        // Fetch insights
        const insightsResponse = await api.get('/api/analytics/insights');
        setInsights(insightsResponse.data.insights);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchAnalytics();
    }
  }, [user, timeRange, api]);

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
      name: 'Presentations',
      description: 'Create professional presentations with AI',
      icon: Presentation,
      path: '/presentations',
      color: 'bg-indigo-500',
      available: true
    },
    {
      name: 'Workflow Automation',
      description: 'Create multi-step automated workflows',
      icon: Zap,
      path: '/workflows',
      color: 'bg-yellow-500',
      available: true
    }
  ];

  // Prepare chart data
  const prepareChartData = () => {
    if (!analytics) return null;

    const dates = Object.keys(analytics.daily_activity).sort();
    const chartData = {
      labels: dates.map(date => new Date(date).toLocaleDateString()),
      datasets: [
        {
          label: 'Total Activity',
          data: dates.map(date => analytics.daily_activity[date].total),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Text Generation',
          data: dates.map(date => analytics.daily_activity[date].text),
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Image Generation',
          data: dates.map(date => analytics.daily_activity[date].image),
          borderColor: 'rgb(139, 92, 246)',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          tension: 0.4,
        }
      ]
    };

    return chartData;
  };

  const preparePieData = () => {
    if (!analytics) return null;

    const breakdown = analytics.generation_breakdown;
    return {
      labels: Object.keys(breakdown).map(key => key.charAt(0).toUpperCase() + key.slice(1)),
      datasets: [
        {
          data: Object.values(breakdown),
          backgroundColor: [
            'rgb(59, 130, 246)',
            'rgb(16, 185, 129)',
            'rgb(139, 92, 246)',
            'rgb(245, 158, 11)',
            'rgb(239, 68, 68)',
          ],
          borderWidth: 2,
        }
      ]
    };
  };

  const exportData = async () => {
    try {
      const response = await api.get(`/api/analytics/export?format=json&days=${timeRange}`);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-dots">
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

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
                <Link to="/profile" className="text-sm font-medium text-gray-700 hover:text-primary-600">
                  {user?.username}
                </Link>
                {user?.is_admin && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    Admin
                  </span>
                )}
              </div>
              <button
                onClick={() => setShowAnalytics(!showAnalytics)}
                className="btn-ghost"
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Analytics
              </button>
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
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.username}!
            </h1>
            <p className="text-gray-600">
              Here's what's happening with your AI-powered content creation
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
              className="input-field"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <button onClick={exportData} className="btn-ghost">
              <Download className="h-4 w-4 mr-2" />
              Export
            </button>
          </div>
        </div>

        {/* Enhanced Stats Grid */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Generations</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.summary.total_generations}</p>
                </div>
                <div className="bg-blue-100 p-3 rounded-full">
                  <Zap className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-green-600">+12% from last period</span>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.summary.success_rate}%</p>
                </div>
                <div className="bg-green-100 p-3 rounded-full">
                  <Award className="h-6 w-6 text-green-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <Activity className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-green-600">Excellent performance</span>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.summary.avg_response_time}s</p>
                </div>
                <div className="bg-purple-100 p-3 rounded-full">
                  <Clock className="h-6 w-6 text-purple-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-green-600">Improved speed</span>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Estimated Cost</p>
                  <p className="text-2xl font-bold text-gray-900">${analytics.summary.estimated_cost}</p>
                </div>
                <div className="bg-yellow-100 p-3 rounded-full">
                  <DollarSign className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-gray-600">This month</span>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Section */}
        {showAnalytics && analytics && (
          <div className="mb-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Activity Chart */}
              <div className="lg:col-span-2 card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold flex items-center">
                    <LineChart className="h-5 w-5 mr-2" />
                    Daily Activity
                  </h3>
                </div>
                <div className="h-64">
                  <Line
                    data={prepareChartData()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                        },
                      },
                    }}
                  />
                </div>
              </div>

              {/* Generation Breakdown */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold flex items-center">
                    <PieChart className="h-5 w-5 mr-2" />
                    Generation Types
                  </h3>
                </div>
                <div className="h-64">
                  <Pie
                    data={preparePieData()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Insights Section */}
        {insights.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {insights.map((insight, index) => (
                <div key={index} className="card border-l-4 border-primary-500">
                  <div className="flex items-start">
                    <div className={`p-2 rounded-full mr-3 ${
                      insight.trend === 'positive' ? 'bg-green-100' : 
                      insight.trend === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'
                    }`}>
                      <TrendingUp className={`h-4 w-4 ${
                        insight.trend === 'positive' ? 'text-green-600' : 
                        insight.trend === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{insight.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

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
        {analytics && (
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
                <button className="btn-ghost text-sm">
                  <Eye className="h-4 w-4 mr-1" />
                  View All
                </button>
              </div>
            </div>
            <div className="space-y-4">
              {/* Display recent activity from analytics */}
              <div className="text-center py-8">
                <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Recent activity will appear here</p>
                <p className="text-sm text-gray-500 mt-2">
                  Start generating content to see your activity
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default EnhancedDashboard;