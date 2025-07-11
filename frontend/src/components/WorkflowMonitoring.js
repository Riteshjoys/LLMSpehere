import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { 
  ChartBarIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon,
  PlayIcon,
  PauseIcon,
  CalendarIcon,
  CogIcon,
  ChartLineIcon,
  EyeIcon,
  ArrowRefreshIcon
} from '@heroicons/react/24/outline';

const WorkflowMonitoring = () => {
  const { user } = useAuth();
  const [dashboardMetrics, setDashboardMetrics] = useState(null);
  const [realtimeStatus, setRealtimeStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [workflowAnalytics, setWorkflowAnalytics] = useState(null);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);

  const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    loadDashboardMetrics();
    loadRealtimeStatus();
    
    // Set up auto-refresh
    const interval = setInterval(() => {
      if (autoRefresh) {
        loadRealtimeStatus();
      }
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const loadDashboardMetrics = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/workflow-monitoring/dashboard`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setDashboardMetrics(response.data);
    } catch (error) {
      console.error('Error loading dashboard metrics:', error);
      toast.error('Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  const loadRealtimeStatus = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/workflow-monitoring/real-time-status`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setRealtimeStatus(response.data);
    } catch (error) {
      console.error('Error loading real-time status:', error);
    }
  };

  const loadWorkflowAnalytics = async (workflowId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/workflow-monitoring/workflows/${workflowId}/analytics`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setWorkflowAnalytics(response.data);
      setShowAnalyticsModal(true);
    } catch (error) {
      console.error('Error loading workflow analytics:', error);
      toast.error('Failed to load workflow analytics');
    } finally {
      setLoading(false);
    }
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning': return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'critical': return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default: return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0s';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const MetricCard = ({ title, value, subtitle, icon: Icon, color = "blue" }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
        {Icon && <Icon className={`h-8 w-8 text-${color}-500`} />}
      </div>
    </div>
  );

  const StatusCard = ({ title, items, emptyMessage }) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      {items.length === 0 ? (
        <p className="text-gray-500 text-sm">{emptyMessage}</p>
      ) : (
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-gray-900">{item.name || item.run_name}</p>
                <p className="text-sm text-gray-600">{item.description || item.workflow_id}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  item.status === 'running' || item.status === 'active' ? 'text-green-600 bg-green-100' :
                  item.status === 'completed' ? 'text-blue-600 bg-blue-100' :
                  item.status === 'failed' ? 'text-red-600 bg-red-100' :
                  'text-gray-600 bg-gray-100'
                }`}>
                  {item.status}
                </span>
                {item.next_run_at && (
                  <span className="text-xs text-gray-500">
                    {new Date(item.next_run_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (loading && !dashboardMetrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Workflow Monitoring</h2>
          <p className="text-gray-600">Monitor and analyze your workflow performance</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="auto-refresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="auto-refresh" className="text-sm text-gray-700">
              Auto-refresh
            </label>
          </div>
          <button
            onClick={() => {
              loadDashboardMetrics();
              loadRealtimeStatus();
            }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowRefreshIcon className="h-5 w-5" />
            Refresh
          </button>
        </div>
      </div>

      {/* System Health */}
      {dashboardMetrics?.system_health && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
            <div className="flex items-center gap-2">
              {getHealthStatusIcon(dashboardMetrics.system_health.status)}
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(dashboardMetrics.system_health.status)}`}>
                {dashboardMetrics.system_health.status}
              </span>
              <span className="text-sm text-gray-600">
                Score: {dashboardMetrics.system_health.score}/100
              </span>
            </div>
          </div>
          
          {dashboardMetrics.system_health.issues.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-2">Issues:</h4>
              <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                {dashboardMetrics.system_health.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
          
          {dashboardMetrics.system_health.recommendations.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Recommendations:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {dashboardMetrics.system_health.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Key Metrics */}
      {dashboardMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Workflows"
            value={dashboardMetrics.total_workflows}
            icon={CogIcon}
            color="blue"
          />
          <MetricCard
            title="Total Executions"
            value={dashboardMetrics.total_executions}
            subtitle={`${dashboardMetrics.today_executions} today`}
            icon={PlayIcon}
            color="green"
          />
          <MetricCard
            title="Active Schedules"
            value={dashboardMetrics.active_schedules}
            subtitle={`${dashboardMetrics.total_schedules} total`}
            icon={CalendarIcon}
            color="purple"
          />
          <MetricCard
            title="Success Rate"
            value={`${dashboardMetrics.execution_metrics?.success_rate || 0}%`}
            subtitle={`Avg: ${formatDuration(dashboardMetrics.avg_execution_time)}`}
            icon={ChartBarIcon}
            color="indigo"
          />
        </div>
      )}

      {/* Real-time Status */}
      {realtimeStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Activity</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Running Executions</span>
                <span className="font-semibold text-green-600">{realtimeStatus.running_executions}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Active Schedules</span>
                <span className="font-semibold text-blue-600">{realtimeStatus.active_schedules}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">System Load</span>
                <span className="font-semibold text-purple-600">{realtimeStatus.system_load?.load_percentage || 0}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Next Execution</h3>
            {realtimeStatus.next_execution ? (
              <div className="space-y-2">
                <p className="font-medium text-gray-900">{realtimeStatus.next_execution.name}</p>
                <p className="text-sm text-gray-600">
                  {new Date(realtimeStatus.next_execution.next_run_at).toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">
                  {realtimeStatus.next_execution.cron_expression}
                </p>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No scheduled executions</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Load</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Current</span>
                <span className="font-semibold">{realtimeStatus.system_load?.current_executions || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Max Concurrent</span>
                <span className="font-semibold">{realtimeStatus.system_load?.max_concurrent || 10}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${realtimeStatus.system_load?.load_percentage || 0}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Activity Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StatusCard
          title="Recent Executions"
          items={dashboardMetrics?.recent_executions || []}
          emptyMessage="No recent executions"
        />
        <StatusCard
          title="Upcoming Schedules"
          items={dashboardMetrics?.upcoming_schedules || []}
          emptyMessage="No upcoming schedules"
        />
      </div>

      {/* Workflow Usage */}
      {dashboardMetrics?.workflow_usage && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Workflow Usage</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Workflow
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Executions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dashboardMetrics.workflow_usage.map((workflow, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{workflow.name}</div>
                        <div className="text-sm text-gray-500">{workflow.category}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{workflow.executions}</div>
                      <div className="text-sm text-gray-500">
                        {workflow.successful} successful, {workflow.failed} failed
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        workflow.success_rate >= 90 ? 'bg-green-100 text-green-800' :
                        workflow.success_rate >= 70 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {workflow.success_rate}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => loadWorkflowAnalytics(workflow.workflow_id)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Analytics
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Workflow Analytics Modal */}
      {showAnalyticsModal && workflowAnalytics && (
        <WorkflowAnalyticsModal
          analytics={workflowAnalytics}
          onClose={() => setShowAnalyticsModal(false)}
        />
      )}
    </div>
  );
};

// Workflow Analytics Modal Component
const WorkflowAnalyticsModal = ({ analytics, onClose }) => {
  const formatDuration = (seconds) => {
    if (!seconds) return '0s';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900">{analytics.workflow_info.name} - Analytics</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircleIcon className="h-6 w-6" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Total Executions</h4>
              <p className="text-2xl font-bold text-blue-600">{analytics.execution_metrics.total}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Success Rate</h4>
              <p className="text-2xl font-bold text-green-600">{analytics.execution_metrics.success_rate}%</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Avg Duration</h4>
              <p className="text-2xl font-bold text-purple-600">{formatDuration(analytics.execution_metrics.avg_duration)}</p>
            </div>
          </div>

          {analytics.step_analytics.step_breakdown.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Step Performance</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Step
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Executions
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Success Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Duration
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analytics.step_analytics.step_breakdown.map((step, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {step.step_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {step.total_executions}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            step.success_rate >= 90 ? 'bg-green-100 text-green-800' :
                            step.success_rate >= 70 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {step.success_rate}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDuration(step.avg_duration)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowMonitoring;