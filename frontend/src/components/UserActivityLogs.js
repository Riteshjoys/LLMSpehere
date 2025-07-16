import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  Activity, 
  Clock, 
  Filter, 
  Search, 
  Download,
  Eye,
  Calendar,
  User,
  Globe,
  Monitor,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const UserActivityLogs = () => {
  const { user, api } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const logsPerPage = 20;

  useEffect(() => {
    fetchLogs();
  }, [currentPage, filterType]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * logsPerPage;
      const response = await api.get(`/api/user/activity-logs?limit=${logsPerPage}&skip=${skip}`);
      setLogs(response.data);
      // Calculate total pages (mock calculation)
      setTotalPages(Math.ceil(response.data.length / logsPerPage) || 1);
    } catch (error) {
      console.error('Error fetching activity logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'login':
        return <User className="h-4 w-4" />;
      case 'profile_update':
        return <User className="h-4 w-4" />;
      case 'generation':
        return <Activity className="h-4 w-4" />;
      case 'preferences_update':
        return <Monitor className="h-4 w-4" />;
      case 'password_update':
        return <User className="h-4 w-4" />;
      case 'email_update':
        return <User className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'login':
        return 'bg-green-100 text-green-600';
      case 'profile_update':
        return 'bg-blue-100 text-blue-600';
      case 'generation':
        return 'bg-purple-100 text-purple-600';
      case 'preferences_update':
        return 'bg-yellow-100 text-yellow-600';
      case 'password_update':
        return 'bg-red-100 text-red-600';
      case 'email_update':
        return 'bg-indigo-100 text-indigo-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesSearch = log.activity_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.activity_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || log.activity_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const exportLogs = () => {
    const dataStr = JSON.stringify(filteredLogs, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `activity-logs-${new Date().toISOString().split('T')[0]}.json`;
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
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
          <p className="mt-4 text-gray-600">Loading activity logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-primary-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Activity Logs</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={exportLogs}
                className="btn-ghost"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search activities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input-field"
            >
              <option value="all">All Activities</option>
              <option value="login">Login</option>
              <option value="profile_update">Profile Updates</option>
              <option value="generation">Generation</option>
              <option value="preferences_update">Preferences</option>
              <option value="password_update">Password Changes</option>
              <option value="email_update">Email Changes</option>
            </select>
          </div>
        </div>

        {/* Activity Logs */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold">Activity History</h2>
            <p className="text-sm text-gray-600">
              Showing {filteredLogs.length} of {logs.length} activities
            </p>
          </div>
          
          {filteredLogs.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No activity logs found</p>
              <p className="text-sm text-gray-500 mt-2">
                Try adjusting your search or filter criteria
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredLogs.map((log) => (
                <div key={log.activity_id} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 p-2 rounded-full ${getActivityColor(log.activity_type)}`}>
                        {getActivityIcon(log.activity_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <p className="text-sm font-medium text-gray-900">
                            {log.activity_description}
                          </p>
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {log.activity_type.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <div className="flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            {new Date(log.timestamp).toLocaleString()}
                          </div>
                          {log.ip_address && (
                            <div className="flex items-center">
                              <Globe className="h-3 w-3 mr-1" />
                              {log.ip_address}
                            </div>
                          )}
                        </div>
                        {log.metadata && Object.keys(log.metadata).length > 0 && (
                          <div className="mt-2 text-xs text-gray-600">
                            <details className="cursor-pointer">
                              <summary className="font-medium hover:text-primary-600">
                                View Details
                              </summary>
                              <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                                <pre className="whitespace-pre-wrap">
                                  {JSON.stringify(log.metadata, null, 2)}
                                </pre>
                              </div>
                            </details>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <div className="flex items-center text-sm text-gray-700">
                Showing page {currentPage} of {totalPages}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="btn-ghost disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="btn-ghost disabled:opacity-50"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserActivityLogs;