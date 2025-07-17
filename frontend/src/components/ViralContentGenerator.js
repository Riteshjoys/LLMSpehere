import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
    FireIcon, 
    SparklesIcon, 
    ChartBarIcon, 
    EyeIcon,
    HeartIcon,
    ChatBubbleBottomCenterIcon,
    ShareIcon,
    ArrowTrendingUpIcon,
    DocumentTextIcon,
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const ViralContentGenerator = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('generate');
    const [loading, setLoading] = useState(false);
    const [platforms, setPlatforms] = useState([]);
    const [contentTypes, setContentTypes] = useState([]);
    const [templates, setTemplates] = useState([]);
    const [trends, setTrends] = useState([]);
    const [generatedContent, setGeneratedContent] = useState(null);
    const [contentHistory, setContentHistory] = useState([]);
    const [stats, setStats] = useState(null);
    const [trendingHashtags, setTrendingHashtags] = useState([]);

    // Form state
    const [formData, setFormData] = useState({
        topic: '',
        platform: 'tiktok',
        content_type: 'video',
        target_audience: 'general',
        tone: 'engaging',
        template_id: '',
        include_hashtags: true,
        include_trending_elements: true,
        max_length: null,
        custom_requirements: {}
    });

    // Trend analysis form
    const [trendAnalysisForm, setTrendAnalysisForm] = useState({
        platforms: ['tiktok', 'instagram'],
        categories: [],
        region: 'global',
        timeframe: '24h',
        include_hashtags: true,
        include_sounds: true,
        include_effects: true
    });

    useEffect(() => {
        fetchPlatforms();
        fetchContentTypes();
        fetchTemplates();
        fetchTrendingHashtags();
        fetchContentHistory();
        fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchPlatforms = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/viral/platforms`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setPlatforms(response.data.platforms || []);
        } catch (error) {
            console.error('Error fetching platforms:', error);
        }
    };

    const fetchContentTypes = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/viral/content-types`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setContentTypes(response.data.content_types || []);
        } catch (error) {
            console.error('Error fetching content types:', error);
        }
    };

    const fetchTemplates = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/viral/templates`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setTemplates(response.data.templates || []);
        } catch (error) {
            console.error('Error fetching templates:', error);
        }
    };

    const fetchTrendingHashtags = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/viral/trending-hashtags`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setTrendingHashtags(response.data.hashtags || []);
        } catch (error) {
            console.error('Error fetching trending hashtags:', error);
        }
    };

    const fetchContentHistory = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/viral/content?limit=10`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setContentHistory(response.data.content || []);
        } catch (error) {
            console.error('Error fetching content history:', error);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/viral/stats`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setStats(response.data.stats || null);
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    const analyzeTrends = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/viral/analyze-trends`, 
                trendAnalysisForm, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setTrends(response.data.trends || []);
            toast.success('Trends analyzed successfully!');
        } catch (error) {
            console.error('Error analyzing trends:', error);
            toast.error('Failed to analyze trends');
        } finally {
            setLoading(false);
        }
    };

    const generateViralContent = async () => {
        if (!formData.topic.trim()) {
            toast.error('Please enter a topic');
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/viral/generate`, 
                formData, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setGeneratedContent(response.data);
            toast.success('Viral content generated successfully!');
            fetchContentHistory(); // Refresh history
        } catch (error) {
            console.error('Error generating content:', error);
            toast.error('Failed to generate viral content');
        } finally {
            setLoading(false);
        }
    };

    const adaptContentCrossPlatform = async (content, originalPlatform) => {
        const targetPlatforms = platforms
            .filter(p => p.name !== originalPlatform)
            .map(p => p.name);

        try {
            const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/viral/adapt-cross-platform`, {
                content,
                original_platform: originalPlatform,
                target_platforms: targetPlatforms
            }, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            
            toast.success('Content adapted for all platforms!');
            return response.data;
        } catch (error) {
            console.error('Error adapting content:', error);
            toast.error('Failed to adapt content');
        }
    };

    const renderTrendAnalysis = () => (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
                <TrendingUpIcon className="h-8 w-8 text-blue-500 mr-3" />
                <h2 className="text-2xl font-bold text-gray-800">Trend Analysis</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Platforms</label>
                    <div className="space-y-2">
                        {platforms.map(platform => (
                            <label key={platform.name} className="flex items-center">
                                <input
                                    type="checkbox"
                                    checked={trendAnalysisForm.platforms.includes(platform.name)}
                                    onChange={(e) => {
                                        const platforms = e.target.checked
                                            ? [...trendAnalysisForm.platforms, platform.name]
                                            : trendAnalysisForm.platforms.filter(p => p !== platform.name);
                                        setTrendAnalysisForm({...trendAnalysisForm, platforms});
                                    }}
                                    className="mr-2"
                                />
                                <span className="text-sm text-gray-700">{platform.display_name}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Timeframe</label>
                    <select
                        value={trendAnalysisForm.timeframe}
                        onChange={(e) => setTrendAnalysisForm({...trendAnalysisForm, timeframe: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="24h">Last 24 hours</option>
                        <option value="7d">Last 7 days</option>
                        <option value="30d">Last 30 days</option>
                    </select>
                </div>
            </div>

            <button
                onClick={analyzeTrends}
                disabled={loading}
                className="w-full bg-blue-500 text-white py-3 px-4 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
                {loading ? (
                    <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Analyzing Trends...
                    </>
                ) : (
                    <>
                        <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                        Analyze Trends
                    </>
                )}
            </button>

            {trends.length > 0 && (
                <div className="mt-8">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Current Trends</h3>
                    <div className="space-y-4">
                        {trends.map((trend, index) => (
                            <div key={index} className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="font-semibold text-gray-800">{trend.title}</h4>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                                        trend.viral_potential === 'viral' ? 'bg-red-100 text-red-800' :
                                        trend.viral_potential === 'high' ? 'bg-orange-100 text-orange-800' :
                                        'bg-green-100 text-green-800'
                                    }`}>
                                        {trend.viral_potential}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-600 mb-3">{trend.description}</p>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <span className="text-sm text-gray-500">
                                            Engagement: {(trend.engagement_rate * 100).toFixed(1)}%
                                        </span>
                                        <span className="text-sm text-gray-500">
                                            Growth: {(trend.growth_rate * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-1">
                                        {trend.hashtags.slice(0, 3).map((hashtag, idx) => (
                                            <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                                {hashtag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );

    const renderContentGenerator = () => (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
                <FireIcon className="h-8 w-8 text-red-500 mr-3" />
                <h2 className="text-2xl font-bold text-gray-800">Generate Viral Content</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Topic *</label>
                    <input
                        type="text"
                        value={formData.topic}
                        onChange={(e) => setFormData({...formData, topic: e.target.value})}
                        placeholder="Enter your content topic..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Platform</label>
                    <select
                        value={formData.platform}
                        onChange={(e) => setFormData({...formData, platform: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        {platforms.map(platform => (
                            <option key={platform.name} value={platform.name}>
                                {platform.display_name}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
                    <select
                        value={formData.content_type}
                        onChange={(e) => setFormData({...formData, content_type: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        {contentTypes.map(type => (
                            <option key={type.name} value={type.name}>
                                {type.display_name}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Target Audience</label>
                    <input
                        type="text"
                        value={formData.target_audience}
                        onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
                        placeholder="e.g., millennials, entrepreneurs, fitness enthusiasts"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tone</label>
                    <select
                        value={formData.tone}
                        onChange={(e) => setFormData({...formData, tone: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="engaging">Engaging</option>
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="humorous">Humorous</option>
                        <option value="inspirational">Inspirational</option>
                        <option value="educational">Educational</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Template (Optional)</label>
                    <select
                        value={formData.template_id}
                        onChange={(e) => setFormData({...formData, template_id: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">No template</option>
                        {templates.map(template => (
                            <option key={template.template_id} value={template.template_id}>
                                {template.name} - {template.platform}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="flex items-center space-x-4 mb-6">
                <label className="flex items-center">
                    <input
                        type="checkbox"
                        checked={formData.include_hashtags}
                        onChange={(e) => setFormData({...formData, include_hashtags: e.target.checked})}
                        className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Include hashtags</span>
                </label>
                <label className="flex items-center">
                    <input
                        type="checkbox"
                        checked={formData.include_trending_elements}
                        onChange={(e) => setFormData({...formData, include_trending_elements: e.target.checked})}
                        className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Include trending elements</span>
                </label>
            </div>

            <button
                onClick={generateViralContent}
                disabled={loading}
                className="w-full bg-red-500 text-white py-3 px-4 rounded-md hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
                {loading ? (
                    <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Generating...
                    </>
                ) : (
                    <>
                        <SparklesIcon className="h-5 w-5 mr-2" />
                        Generate Viral Content
                    </>
                )}
            </button>

            {generatedContent && (
                <div className="mt-8 bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Generated Content</h3>
                    
                    <div className="bg-white rounded-lg p-4 mb-4">
                        <h4 className="font-medium text-gray-800 mb-2">Content</h4>
                        <p className="text-gray-700 whitespace-pre-wrap">{generatedContent.content}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="bg-white rounded-lg p-4">
                            <h4 className="font-medium text-gray-800 mb-2">Hashtags</h4>
                            <div className="flex flex-wrap gap-2">
                                {generatedContent.hashtags.map((hashtag, index) => (
                                    <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                                        {hashtag}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="bg-white rounded-lg p-4">
                            <h4 className="font-medium text-gray-800 mb-2">Optimal Post Time</h4>
                            <p className="text-gray-700">
                                {new Date(generatedContent.optimal_post_time).toLocaleString()}
                            </p>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg p-4 mb-4">
                        <h4 className="font-medium text-gray-800 mb-2">Engagement Prediction</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="text-center">
                                <EyeIcon className="h-6 w-6 text-blue-500 mx-auto mb-1" />
                                <p className="text-sm text-gray-600">Views</p>
                                <p className="font-semibold">{generatedContent.engagement_prediction.predicted_views.toLocaleString()}</p>
                            </div>
                            <div className="text-center">
                                <HeartIcon className="h-6 w-6 text-red-500 mx-auto mb-1" />
                                <p className="text-sm text-gray-600">Likes</p>
                                <p className="font-semibold">{generatedContent.engagement_prediction.predicted_likes.toLocaleString()}</p>
                            </div>
                            <div className="text-center">
                                <ChatBubbleBottomCenterIcon className="h-6 w-6 text-green-500 mx-auto mb-1" />
                                <p className="text-sm text-gray-600">Comments</p>
                                <p className="font-semibold">{generatedContent.engagement_prediction.predicted_comments.toLocaleString()}</p>
                            </div>
                            <div className="text-center">
                                <ShareIcon className="h-6 w-6 text-purple-500 mx-auto mb-1" />
                                <p className="text-sm text-gray-600">Shares</p>
                                <p className="font-semibold">{generatedContent.engagement_prediction.predicted_shares.toLocaleString()}</p>
                            </div>
                        </div>
                        <div className="mt-4 text-center">
                            <p className="text-sm text-gray-600">Virality Score</p>
                            <p className="text-2xl font-bold text-red-500">
                                {(generatedContent.engagement_prediction.virality_score * 100).toFixed(1)}%
                            </p>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg p-4">
                        <h4 className="font-medium text-gray-800 mb-2">Platform Tips</h4>
                        <ul className="list-disc pl-5 space-y-1">
                            {generatedContent.platform_specific_tips.map((tip, index) => (
                                <li key={index} className="text-sm text-gray-700">{tip}</li>
                            ))}
                        </ul>
                    </div>

                    <div className="mt-4 flex space-x-4">
                        <button
                            onClick={() => adaptContentCrossPlatform(generatedContent.content, generatedContent.platform)}
                            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
                        >
                            Adapt for All Platforms
                        </button>
                        <button
                            onClick={() => {
                                navigator.clipboard.writeText(generatedContent.content);
                                toast.success('Content copied to clipboard!');
                            }}
                            className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
                        >
                            Copy Content
                        </button>
                    </div>
                </div>
            )}
        </div>
    );

    const renderContentHistory = () => (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
                <DocumentTextIcon className="h-8 w-8 text-green-500 mr-3" />
                <h2 className="text-2xl font-bold text-gray-800">Content History</h2>
            </div>

            {contentHistory.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p>No viral content generated yet.</p>
                    <p className="text-sm">Start generating content to see your history here!</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {contentHistory.map((item, index) => (
                        <div key={index} className="bg-gray-50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="font-semibold text-gray-800">{item.topic}</h3>
                                <div className="flex items-center space-x-2">
                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                        {item.platform}
                                    </span>
                                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                        {item.content_type}
                                    </span>
                                </div>
                            </div>
                            <p className="text-sm text-gray-600 mb-3 line-clamp-3">{item.content}</p>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                    <span className="text-xs text-gray-500">
                                        Viral Score: {(item.viral_score * 100).toFixed(1)}%
                                    </span>
                                    <span className="text-xs text-gray-500">
                                        {new Date(item.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="flex flex-wrap gap-1">
                                    {item.hashtags.slice(0, 3).map((hashtag, idx) => (
                                        <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                            {hashtag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );

    const renderStats = () => (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
                <ChartBarIcon className="h-8 w-8 text-purple-500 mr-3" />
                <h2 className="text-2xl font-bold text-gray-800">Statistics</h2>
            </div>

            {stats ? (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4 text-center">
                            <p className="text-2xl font-bold text-blue-600">{stats.total_generated}</p>
                            <p className="text-sm text-gray-600">Total Generated</p>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4 text-center">
                            <p className="text-2xl font-bold text-green-600">{(stats.average_viral_score * 100).toFixed(1)}%</p>
                            <p className="text-sm text-gray-600">Avg Viral Score</p>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4 text-center">
                            <p className="text-2xl font-bold text-purple-600">{(stats.success_rate * 100).toFixed(1)}%</p>
                            <p className="text-sm text-gray-600">Success Rate</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h3 className="font-semibold text-gray-800 mb-3">By Platform</h3>
                            <div className="space-y-2">
                                {Object.entries(stats.by_platform).map(([platform, count]) => (
                                    <div key={platform} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600 capitalize">{platform}</span>
                                        <span className="font-semibold">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h3 className="font-semibold text-gray-800 mb-3">By Content Type</h3>
                            <div className="space-y-2">
                                {Object.entries(stats.by_content_type).map(([type, count]) => (
                                    <div key={type} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600 capitalize">{type}</span>
                                        <span className="font-semibold">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-800 mb-3">Trending Hashtags</h3>
                        <div className="flex flex-wrap gap-2">
                            {trendingHashtags.map((hashtag, index) => (
                                <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                    {hashtag}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="text-center py-8 text-gray-500">
                    <ChartBarIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p>No statistics available yet.</p>
                    <p className="text-sm">Generate some content to see your stats!</p>
                </div>
            )}
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Viral Content Generator</h1>
                    <p className="text-gray-600">Create viral content with AI-powered trend analysis and cross-platform optimization</p>
                </div>

                {/* Tab Navigation */}
                <div className="mb-8">
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-8">
                            {[
                                { id: 'generate', name: 'Generate', icon: SparklesIcon },
                                { id: 'trends', name: 'Trends', icon: ArrowTrendingUpIcon },
                                { id: 'history', name: 'History', icon: DocumentTextIcon },
                                { id: 'stats', name: 'Statistics', icon: ChartBarIcon }
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                                        activeTab === tab.id
                                            ? 'border-red-500 text-red-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                                >
                                    <tab.icon className="h-5 w-5 mr-2" />
                                    {tab.name}
                                </button>
                            ))}
                        </nav>
                    </div>
                </div>

                {/* Tab Content */}
                <div className="mt-8">
                    {activeTab === 'generate' && renderContentGenerator()}
                    {activeTab === 'trends' && renderTrendAnalysis()}
                    {activeTab === 'history' && renderContentHistory()}
                    {activeTab === 'stats' && renderStats()}
                </div>
            </div>
        </div>
    );
};

export default ViralContentGenerator;