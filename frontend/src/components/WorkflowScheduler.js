import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { 
  CalendarIcon, 
  PlayIcon, 
  PauseIcon, 
  TrashIcon, 
  PencilIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';

const WorkflowScheduler = ({ workflows = [] }) => {
  const { user } = useAuth();
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  useEffect(() => {
    loadSchedules();
  }, []);
  
  const loadSchedules = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${backendUrl}/api/workflow-schedules/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setSchedules(response.data);
    } catch (error) {
      console.error('Error loading schedules:', error);
      toast.error('Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };
  
  const createSchedule = async (scheduleData) => {
    try {
      setLoading(true);
      const response = await axios.post(`${backendUrl}/api/workflow-schedules/`, scheduleData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Schedule created successfully!');
      loadSchedules();
      setShowCreateModal(false);
    } catch (error) {
      console.error('Error creating schedule:', error);
      toast.error(error.response?.data?.detail || 'Failed to create schedule');
    } finally {
      setLoading(false);
    }
  };
  
  const updateSchedule = async (scheduleId, updateData) => {
    try {
      setLoading(true);
      const response = await axios.put(`${backendUrl}/api/workflow-schedules/${scheduleId}`, updateData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Schedule updated successfully!');
      loadSchedules();
      setShowEditModal(false);
    } catch (error) {
      console.error('Error updating schedule:', error);
      toast.error(error.response?.data?.detail || 'Failed to update schedule');
    } finally {
      setLoading(false);
    }
  };
  
  const deleteSchedule = async (scheduleId) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return;
    
    try {
      setLoading(true);
      await axios.delete(`${backendUrl}/api/workflow-schedules/${scheduleId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Schedule deleted successfully!');
      loadSchedules();
    } catch (error) {
      console.error('Error deleting schedule:', error);
      toast.error('Failed to delete schedule');
    } finally {
      setLoading(false);
    }
  };
  
  const pauseSchedule = async (scheduleId) => {
    try {
      setLoading(true);
      await axios.post(`${backendUrl}/api/workflow-schedules/${scheduleId}/pause`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Schedule paused successfully!');
      loadSchedules();
    } catch (error) {
      console.error('Error pausing schedule:', error);
      toast.error('Failed to pause schedule');
    } finally {
      setLoading(false);
    }
  };
  
  const resumeSchedule = async (scheduleId) => {
    try {
      setLoading(true);
      await axios.post(`${backendUrl}/api/workflow-schedules/${scheduleId}/resume`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      toast.success('Schedule resumed successfully!');
      loadSchedules();
    } catch (error) {
      console.error('Error resuming schedule:', error);
      toast.error('Failed to resume schedule');
    } finally {
      setLoading(false);
    }
  };
  
  const validateCronExpression = async (expression) => {
    try {
      const response = await axios.get(`${backendUrl}/api/workflow-schedules/validate/cron?expression=${encodeURIComponent(expression)}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error validating cron expression:', error);
      return { valid: false, next_runs: [] };
    }
  };
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'paused': return <PauseIcon className="h-5 w-5 text-yellow-500" />;
      case 'completed': return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      case 'failed': return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default: return <ExclamationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };
  
  const formatNextRun = (nextRunAt) => {
    if (!nextRunAt) return 'Not scheduled';
    const date = new Date(nextRunAt);
    return date.toLocaleString();
  };
  
  const renderScheduleCard = (schedule) => {
    const workflow = workflows.find(w => w.workflow_id === schedule.workflow_id);
    
    return (
      <div key={schedule.schedule_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{schedule.name}</h3>
            <p className="text-gray-600 text-sm mb-3">{schedule.description}</p>
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(schedule.status)}`}>
                <span className="flex items-center gap-1">
                  {getStatusIcon(schedule.status)}
                  {schedule.status}
                </span>
              </span>
              {workflow && (
                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                  {workflow.name}
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
              <div>
                <span className="font-medium">Cron: </span>
                <code className="bg-gray-100 px-2 py-1 rounded text-xs">{schedule.cron_expression}</code>
              </div>
              <div>
                <span className="font-medium">Next Run: </span>
                {formatNextRun(schedule.next_run_at)}
              </div>
              <div>
                <span className="font-medium">Runs: </span>
                {schedule.runs_count} {schedule.max_runs && `/ ${schedule.max_runs}`}
              </div>
              <div>
                <span className="font-medium">Last Run: </span>
                {schedule.last_run_at ? new Date(schedule.last_run_at).toLocaleString() : 'Never'}
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            {schedule.status === 'active' ? (
              <button
                onClick={() => pauseSchedule(schedule.schedule_id)}
                className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                title="Pause Schedule"
              >
                <PauseIcon className="h-5 w-5" />
              </button>
            ) : schedule.status === 'paused' ? (
              <button
                onClick={() => resumeSchedule(schedule.schedule_id)}
                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                title="Resume Schedule"
              >
                <PlayIcon className="h-5 w-5" />
              </button>
            ) : null}
            <button
              onClick={() => {
                setSelectedSchedule(schedule);
                setShowEditModal(true);
              }}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Edit Schedule"
            >
              <PencilIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => deleteSchedule(schedule.schedule_id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Delete Schedule"
            >
              <TrashIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Workflow Schedules</h2>
          <p className="text-gray-600">Automate your workflows with scheduled execution</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5" />
          New Schedule
        </button>
      </div>
      
      {/* Schedules Grid */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : schedules.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <CalendarIcon className="h-12 w-12" />
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No schedules yet</h3>
          <p className="mt-1 text-sm text-gray-500">Create your first workflow schedule to get started</p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Create Schedule
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schedules.map(renderScheduleCard)}
        </div>
      )}
      
      {/* Create Schedule Modal */}
      {showCreateModal && (
        <CreateScheduleModal
          workflows={workflows}
          onClose={() => setShowCreateModal(false)}
          onSubmit={createSchedule}
          validateCron={validateCronExpression}
        />
      )}
      
      {/* Edit Schedule Modal */}
      {showEditModal && selectedSchedule && (
        <EditScheduleModal
          schedule={selectedSchedule}
          workflows={workflows}
          onClose={() => setShowEditModal(false)}
          onSubmit={(updateData) => updateSchedule(selectedSchedule.schedule_id, updateData)}
          validateCron={validateCronExpression}
        />
      )}
    </div>
  );
};

// Create Schedule Modal Component
const CreateScheduleModal = ({ workflows, onClose, onSubmit, validateCron }) => {
  const [formData, setFormData] = useState({
    workflow_id: '',
    name: '',
    description: '',
    cron_expression: '',
    timezone: 'UTC',
    input_variables: {},
    max_runs: ''
  });
  const [cronValidation, setCronValidation] = useState({ valid: false, next_runs: [] });
  const [loading, setLoading] = useState(false);
  
  const commonCronExpressions = [
    { label: 'Every day at 9 AM', value: '0 9 * * *' },
    { label: 'Every Monday at 9 AM', value: '0 9 * * MON' },
    { label: 'Every hour', value: '0 * * * *' },
    { label: 'Every 30 minutes', value: '*/30 * * * *' },
    { label: 'Every weekday at 6 PM', value: '0 18 * * MON-FRI' },
    { label: 'Every first day of month at 10 AM', value: '0 10 1 * *' }
  ];
  
  const handleCronChange = async (expression) => {
    setFormData({...formData, cron_expression: expression});
    if (expression) {
      const validation = await validateCron(expression);
      setCronValidation(validation);
    } else {
      setCronValidation({ valid: false, next_runs: [] });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cronValidation.valid) {
      toast.error('Please enter a valid cron expression');
      return;
    }
    
    setLoading(true);
    try {
      const submitData = {
        ...formData,
        max_runs: formData.max_runs ? parseInt(formData.max_runs) : null
      };
      await onSubmit(submitData);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Create New Schedule</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Workflow *
              </label>
              <select
                value={formData.workflow_id}
                onChange={(e) => setFormData({...formData, workflow_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select a workflow</option>
                {workflows.map(workflow => (
                  <option key={workflow.workflow_id} value={workflow.workflow_id}>
                    {workflow.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Schedule Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cron Expression *
              </label>
              <input
                type="text"
                value={formData.cron_expression}
                onChange={(e) => handleCronChange(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  formData.cron_expression && !cronValidation.valid ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="0 9 * * *"
                required
              />
              {formData.cron_expression && (
                <div className="mt-2">
                  {cronValidation.valid ? (
                    <div className="text-green-600 text-sm">
                      ✓ Valid cron expression
                      {cronValidation.next_runs.length > 0 && (
                        <div className="mt-1 text-xs text-gray-600">
                          Next runs: {cronValidation.next_runs.slice(0, 3).map(run => 
                            new Date(run).toLocaleString()
                          ).join(', ')}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-red-600 text-sm">
                      ✗ Invalid cron expression
                    </div>
                  )}
                </div>
              )}
              
              <div className="mt-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Common Patterns
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {commonCronExpressions.map((expr, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => handleCronChange(expr.value)}
                      className="text-left p-2 text-sm bg-gray-50 hover:bg-gray-100 rounded border"
                    >
                      <div className="font-medium">{expr.label}</div>
                      <div className="text-xs text-gray-500">{expr.value}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Runs (optional)
              </label>
              <input
                type="number"
                value={formData.max_runs}
                onChange={(e) => setFormData({...formData, max_runs: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Leave empty for unlimited"
              />
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                type="submit"
                disabled={loading || !cronValidation.valid}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Schedule'}
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

// Edit Schedule Modal Component
const EditScheduleModal = ({ schedule, workflows, onClose, onSubmit, validateCron }) => {
  const [formData, setFormData] = useState({
    name: schedule.name,
    description: schedule.description,
    cron_expression: schedule.cron_expression,
    timezone: schedule.timezone,
    input_variables: schedule.input_variables,
    max_runs: schedule.max_runs || ''
  });
  const [cronValidation, setCronValidation] = useState({ valid: true, next_runs: [] });
  const [loading, setLoading] = useState(false);
  
  const handleCronChange = async (expression) => {
    setFormData({...formData, cron_expression: expression});
    if (expression) {
      const validation = await validateCron(expression);
      setCronValidation(validation);
    } else {
      setCronValidation({ valid: false, next_runs: [] });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cronValidation.valid) {
      toast.error('Please enter a valid cron expression');
      return;
    }
    
    setLoading(true);
    try {
      const submitData = {
        ...formData,
        max_runs: formData.max_runs ? parseInt(formData.max_runs) : null
      };
      await onSubmit(submitData);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Edit Schedule</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Schedule Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cron Expression *
              </label>
              <input
                type="text"
                value={formData.cron_expression}
                onChange={(e) => handleCronChange(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  formData.cron_expression && !cronValidation.valid ? 'border-red-300' : 'border-gray-300'
                }`}
                required
              />
              {formData.cron_expression && (
                <div className="mt-2">
                  {cronValidation.valid ? (
                    <div className="text-green-600 text-sm">
                      ✓ Valid cron expression
                      {cronValidation.next_runs.length > 0 && (
                        <div className="mt-1 text-xs text-gray-600">
                          Next runs: {cronValidation.next_runs.slice(0, 3).map(run => 
                            new Date(run).toLocaleString()
                          ).join(', ')}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-red-600 text-sm">
                      ✗ Invalid cron expression
                    </div>
                  )}
                </div>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Runs (optional)
              </label>
              <input
                type="number"
                value={formData.max_runs}
                onChange={(e) => setFormData({...formData, max_runs: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Leave empty for unlimited"
              />
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                type="submit"
                disabled={loading || !cronValidation.valid}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Updating...' : 'Update Schedule'}
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

export default WorkflowScheduler;