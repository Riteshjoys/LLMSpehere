import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';
import { 
  Mic, 
  Video, 
  Settings, 
  Play, 
  Pause, 
  Download, 
  Upload, 
  Save, 
  Trash2, 
  Clock, 
  Volume2, 
  User,
  Monitor,
  Music,
  Wand2,
  FileText,
  Eye,
  Loader,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Zap,
  Sparkles,
  Camera,
  Headphones,
  Film,
  Palette,
  Layout,
  PlayCircle,
  StopCircle,
  SkipForward,
  SkipBack,
  VolumeX,
  Volume1,
  Maximize,
  Minimize,
  RotateCcw,
  Share2,
  ExternalLink
} from 'lucide-react';

const FacelessContentCreator = () => {
  const { api } = useAuth();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('create');
  const [generationStep, setGenerationStep] = useState(1);
  
  // Content creation state
  const [contentData, setContentData] = useState({
    title: '',
    description: '',
    tts_text: '',
    voice_id: '',
    video_duration: 60,
    video_format: 'mp4',
    video_quality: 'high',
    video_resolution: '1920x1080'
  });
  
  // Available options
  const [voices, setVoices] = useState([]);
  const [characters, setCharacters] = useState([]);
  const [backgroundMusic, setBackgroundMusic] = useState([]);
  const [templates, setTemplates] = useState([]);
  
  // Selected options
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [selectedMusic, setSelectedMusic] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  
  // Screen recording settings
  const [screenRecording, setScreenRecording] = useState({
    enabled: false,
    duration: 60,
    fps: 30,
    quality: 'high',
    capture_audio: true
  });
  
  // Character settings
  const [characterSettings, setCharacterSettings] = useState({
    enabled: false,
    position: { x: 0.8, y: 0.7 },
    scale: 1.0,
    animation: 'talking'
  });
  
  // Music settings
  const [musicSettings, setMusicSettings] = useState({
    enabled: false,
    volume: 0.3,
    fade_in: 0.0,
    fade_out: 0.0,
    loop: true
  });
  
  // Generated content
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentHistory, setContentHistory] = useState([]);
  const [stats, setStats] = useState(null);
  
  // Audio preview
  const [audioPreview, setAudioPreview] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  useEffect(() => {
    loadInitialData();
  }, []);
  
  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load all available options
      const [voicesRes, charactersRes, musicRes, templatesRes, historyRes, statsRes] = await Promise.all([
        api.get('/api/faceless-content/voices'),
        api.get('/api/faceless-content/characters'),
        api.get('/api/faceless-content/background-music'),
        api.get('/api/faceless-content/templates'),
        api.get('/api/faceless-content/history?limit=20'),
        api.get('/api/faceless-content/stats/overview')
      ]);
      
      setVoices(voicesRes.data || []);
      setCharacters(charactersRes.data || []);
      setBackgroundMusic(musicRes.data || []);
      setTemplates(templatesRes.data || []);
      setContentHistory(historyRes.data || []);
      setStats(statsRes.data || null);
      
      // Set default voice if available
      if (voicesRes.data && voicesRes.data.length > 0) {
        setSelectedVoice(voicesRes.data[0]);
        setContentData(prev => ({ ...prev, voice_id: voicesRes.data[0].voice_id }));
      }
      
    } catch (error) {
      console.error('Error loading initial data:', error);
      toast.error('Failed to load initial data');
    } finally {
      setLoading(false);
    }
  };
  
  const generateTTSPreview = async () => {
    if (!contentData.tts_text || !selectedVoice) {
      toast.error('Please enter text and select a voice');
      return;
    }
    
    try {
      setLoading(true);
      const response = await api.post('/api/faceless-content/tts/generate', {
        text: contentData.tts_text,
        voice_id: selectedVoice.voice_id,
        stability: 0.5,
        similarity_boost: 0.5
      });
      
      setAudioPreview(response.data.audio_url);
      toast.success('Audio preview generated!');
    } catch (error) {
      console.error('Error generating TTS preview:', error);
      toast.error('Failed to generate audio preview');
    } finally {
      setLoading(false);
    }
  };
  
  const generateFacelessContent = async () => {
    if (!contentData.title || !contentData.tts_text || !selectedVoice) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    try {
      setLoading(true);
      setGenerationStep(1);
      
      // Prepare request data
      const requestData = {
        title: contentData.title,
        description: contentData.description,
        tts_text: contentData.tts_text,
        voice_id: selectedVoice.voice_id,
        video_duration: contentData.video_duration,
        video_format: contentData.video_format,
        video_quality: contentData.video_quality,
        video_resolution: contentData.video_resolution
      };
      
      // Add screen recording if enabled
      if (screenRecording.enabled) {
        requestData.screen_recording = {
          duration: screenRecording.duration,
          fps: screenRecording.fps,
          quality: screenRecording.quality,
          capture_audio: screenRecording.capture_audio
        };
      }
      
      // Add character if enabled
      if (characterSettings.enabled && selectedCharacter) {
        requestData.animated_character = {
          character_id: selectedCharacter.character_id,
          animation: characterSettings.animation,
          duration: contentData.video_duration,
          position: characterSettings.position,
          scale: characterSettings.scale,
          text: contentData.tts_text
        };
      }
      
      // Add background music if enabled
      if (musicSettings.enabled && selectedMusic) {
        requestData.background_music = {
          track_id: selectedMusic.track_id,
          volume: musicSettings.volume,
          fade_in: musicSettings.fade_in,
          fade_out: musicSettings.fade_out,
          loop: musicSettings.loop
        };
      }
      
      setGenerationStep(2);
      const response = await api.post('/api/faceless-content/generate', requestData);
      
      setGenerationStep(3);
      setGeneratedContent(response.data);
      setActiveTab('preview');
      
      toast.success('Faceless content generated successfully!');
      
      // Refresh history
      loadContentHistory();
      
    } catch (error) {
      console.error('Error generating content:', error);
      toast.error('Failed to generate content');
    } finally {
      setLoading(false);
      setGenerationStep(1);
    }
  };
  
  const generateFromTemplate = async (template) => {
    if (!contentData.tts_text) {
      toast.error('Please enter text for the template');
      return;
    }
    
    try {
      setLoading(true);
      const response = await api.post(`/api/faceless-content/templates/${template.template_id}/generate`, {
        custom_text: contentData.tts_text
      });
      
      setGeneratedContent(response.data);
      setActiveTab('preview');
      toast.success('Content generated from template!');
      
    } catch (error) {
      console.error('Error generating from template:', error);
      toast.error('Failed to generate from template');
    } finally {
      setLoading(false);
    }
  };
  
  const loadContentHistory = async () => {
    try {
      const response = await api.get('/api/faceless-content/history?limit=20');
      setContentHistory(response.data || []);
    } catch (error) {
      console.error('Error loading content history:', error);
    }
  };
  
  const deleteContent = async (contentId) => {
    try {
      await api.delete(`/api/faceless-content/${contentId}`);
      toast.success('Content deleted successfully');
      loadContentHistory();
    } catch (error) {
      console.error('Error deleting content:', error);
      toast.error('Failed to delete content');
    }
  };
  
  const playAudio = (audioUrl) => {
    const audio = new Audio(audioUrl);
    audio.play();
    setIsPlaying(true);
    audio.onended = () => setIsPlaying(false);
  };
  
  const tabs = [
    { id: 'create', label: 'Create Content', icon: Wand2 },
    { id: 'templates', label: 'Templates', icon: Layout },
    { id: 'preview', label: 'Preview', icon: Eye },
    { id: 'history', label: 'History', icon: Clock },
    { id: 'stats', label: 'Statistics', icon: Zap }
  ];
  
  if (loading && voices.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading Faceless Content Creator...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-3 rounded-xl">
                <Video className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Faceless Content Creator</h1>
                <p className="text-gray-600">Create engaging videos without showing your face</p>
              </div>
            </div>
            
            {stats && (
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{stats.total_content}</div>
                  <div className="text-sm text-gray-600">Total Content</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{Math.round(stats.total_duration / 60)}m</div>
                  <div className="text-sm text-gray-600">Total Duration</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{Math.round(stats.success_rate)}%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Create Content Tab */}
        {activeTab === 'create' && (
          <div className="space-y-8">
            {/* Generation Progress */}
            {loading && (
              <div className="card">
                <div className="flex items-center space-x-4">
                  <Loader className="h-6 w-6 animate-spin text-primary-600" />
                  <div>
                    <h3 className="text-lg font-semibold">Generating Content</h3>
                    <p className="text-gray-600">
                      {generationStep === 1 && 'Preparing content...'}
                      {generationStep === 2 && 'Generating audio and video...'}
                      {generationStep === 3 && 'Finalizing content...'}
                    </p>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(generationStep / 3) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Basic Content Settings */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold flex items-center">
                  <FileText className="h-6 w-6 mr-2" />
                  Basic Content Settings
                </h2>
              </div>
              
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Content Title *
                    </label>
                    <input
                      type="text"
                      value={contentData.title}
                      onChange={(e) => setContentData(prev => ({ ...prev, title: e.target.value }))}
                      className="input-field"
                      placeholder="Enter content title"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Video Duration (seconds)
                    </label>
                    <input
                      type="number"
                      value={contentData.video_duration}
                      onChange={(e) => setContentData(prev => ({ ...prev, video_duration: parseInt(e.target.value) }))}
                      className="input-field"
                      min="10"
                      max="300"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={contentData.description}
                    onChange={(e) => setContentData(prev => ({ ...prev, description: e.target.value }))}
                    rows="3"
                    className="input-field"
                    placeholder="Brief description of your content"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Script / Narration Text *
                  </label>
                  <textarea
                    value={contentData.tts_text}
                    onChange={(e) => setContentData(prev => ({ ...prev, tts_text: e.target.value }))}
                    rows="6"
                    className="input-field"
                    placeholder="Enter the text you want to be narrated..."
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    This text will be converted to speech using AI voice synthesis
                  </p>
                </div>
              </div>
            </div>
            
            {/* Voice Selection */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold flex items-center">
                  <Mic className="h-6 w-6 mr-2" />
                  Voice Selection
                </h2>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {voices.map((voice) => (
                    <div
                      key={voice.voice_id}
                      onClick={() => {
                        setSelectedVoice(voice);
                        setContentData(prev => ({ ...prev, voice_id: voice.voice_id }));
                      }}
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${
                        selectedVoice?.voice_id === voice.voice_id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium text-gray-900">{voice.name}</h3>
                          <p className="text-sm text-gray-600">{voice.category}</p>
                        </div>
                        {voice.preview_url && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              playAudio(voice.preview_url);
                            }}
                            className="p-2 text-gray-400 hover:text-primary-600"
                          >
                            <Play className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="flex space-x-4">
                  <button
                    onClick={generateTTSPreview}
                    disabled={loading || !contentData.tts_text || !selectedVoice}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Headphones className="h-4 w-4" />
                    <span>Generate Audio Preview</span>
                  </button>
                  
                  {audioPreview && (
                    <button
                      onClick={() => playAudio(audioPreview)}
                      className="btn-secondary flex items-center space-x-2"
                    >
                      <Play className="h-4 w-4" />
                      <span>Play Preview</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            {/* Screen Recording Settings */}
            <div className="card">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold flex items-center">
                    <Monitor className="h-6 w-6 mr-2" />
                    Screen Recording
                  </h2>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={screenRecording.enabled}
                      onChange={(e) => setScreenRecording(prev => ({ ...prev, enabled: e.target.checked }))}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm font-medium">Enable Screen Recording</span>
                  </label>
                </div>
              </div>
              
              {screenRecording.enabled && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration (seconds)
                    </label>
                    <input
                      type="number"
                      value={screenRecording.duration}
                      onChange={(e) => setScreenRecording(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                      className="input-field"
                      min="10"
                      max="300"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Frame Rate
                    </label>
                    <select
                      value={screenRecording.fps}
                      onChange={(e) => setScreenRecording(prev => ({ ...prev, fps: parseInt(e.target.value) }))}
                      className="input-field"
                    >
                      <option value={15}>15 FPS</option>
                      <option value={30}>30 FPS</option>
                      <option value={60}>60 FPS</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quality
                    </label>
                    <select
                      value={screenRecording.quality}
                      onChange={(e) => setScreenRecording(prev => ({ ...prev, quality: e.target.value }))}
                      className="input-field"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={screenRecording.capture_audio}
                      onChange={(e) => setScreenRecording(prev => ({ ...prev, capture_audio: e.target.checked }))}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm font-medium">Capture System Audio</span>
                  </div>
                </div>
              )}
            </div>
            
            {/* Animated Character Settings */}
            <div className="card">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold flex items-center">
                    <User className="h-6 w-6 mr-2" />
                    Animated Character
                  </h2>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={characterSettings.enabled}
                      onChange={(e) => setCharacterSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm font-medium">Enable Character</span>
                  </label>
                </div>
              </div>
              
              {characterSettings.enabled && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {characters.map((character) => (
                      <div
                        key={character.character_id}
                        onClick={() => setSelectedCharacter(character)}
                        className={`p-4 border rounded-lg cursor-pointer transition-all ${
                          selectedCharacter?.character_id === character.character_id
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <h3 className="font-medium text-gray-900">{character.name}</h3>
                        <p className="text-sm text-gray-600">{character.animation_type}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {character.animations.map((animation) => (
                            <span
                              key={animation}
                              className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                            >
                              {animation}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {selectedCharacter && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Animation
                        </label>
                        <select
                          value={characterSettings.animation}
                          onChange={(e) => setCharacterSettings(prev => ({ ...prev, animation: e.target.value }))}
                          className="input-field"
                        >
                          {selectedCharacter.animations.map((animation) => (
                            <option key={animation} value={animation}>{animation}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Scale
                        </label>
                        <input
                          type="range"
                          min="0.5"
                          max="2"
                          step="0.1"
                          value={characterSettings.scale}
                          onChange={(e) => setCharacterSettings(prev => ({ ...prev, scale: parseFloat(e.target.value) }))}
                          className="w-full"
                        />
                        <span className="text-sm text-gray-600">{characterSettings.scale}x</span>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Position
                        </label>
                        <div className="flex space-x-2">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={characterSettings.position.x}
                            onChange={(e) => setCharacterSettings(prev => ({ 
                              ...prev, 
                              position: { ...prev.position, x: parseFloat(e.target.value) }
                            }))}
                            className="flex-1"
                          />
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={characterSettings.position.y}
                            onChange={(e) => setCharacterSettings(prev => ({ 
                              ...prev, 
                              position: { ...prev.position, y: parseFloat(e.target.value) }
                            }))}
                            className="flex-1"
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Background Music Settings */}
            <div className="card">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold flex items-center">
                    <Music className="h-6 w-6 mr-2" />
                    Background Music
                  </h2>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={musicSettings.enabled}
                      onChange={(e) => setMusicSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm font-medium">Enable Background Music</span>
                  </label>
                </div>
              </div>
              
              {musicSettings.enabled && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {backgroundMusic.map((music) => (
                      <div
                        key={music.track_id}
                        onClick={() => setSelectedMusic(music)}
                        className={`p-4 border rounded-lg cursor-pointer transition-all ${
                          selectedMusic?.track_id === music.track_id
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <h3 className="font-medium text-gray-900">{music.name}</h3>
                        <p className="text-sm text-gray-600">{music.genre} • {music.mood}</p>
                        <p className="text-sm text-gray-500">{Math.round(music.duration)}s • {music.tempo}</p>
                      </div>
                    ))}
                  </div>
                  
                  {selectedMusic && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Volume
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={musicSettings.volume}
                          onChange={(e) => setMusicSettings(prev => ({ ...prev, volume: parseFloat(e.target.value) }))}
                          className="w-full"
                        />
                        <span className="text-sm text-gray-600">{Math.round(musicSettings.volume * 100)}%</span>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Fade In (seconds)
                        </label>
                        <input
                          type="number"
                          value={musicSettings.fade_in}
                          onChange={(e) => setMusicSettings(prev => ({ ...prev, fade_in: parseFloat(e.target.value) }))}
                          className="input-field"
                          min="0"
                          max="10"
                          step="0.5"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Fade Out (seconds)
                        </label>
                        <input
                          type="number"
                          value={musicSettings.fade_out}
                          onChange={(e) => setMusicSettings(prev => ({ ...prev, fade_out: parseFloat(e.target.value) }))}
                          className="input-field"
                          min="0"
                          max="10"
                          step="0.5"
                        />
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={musicSettings.loop}
                          onChange={(e) => setMusicSettings(prev => ({ ...prev, loop: e.target.checked }))}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm font-medium">Loop Music</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Generate Button */}
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">Ready to Generate?</h3>
                  <p className="text-gray-600">Click the button below to create your faceless content</p>
                </div>
                <button
                  onClick={generateFacelessContent}
                  disabled={loading || !contentData.title || !contentData.tts_text || !selectedVoice}
                  className="btn-primary flex items-center space-x-2 px-6 py-3"
                >
                  {loading ? (
                    <Loader className="h-5 w-5 animate-spin" />
                  ) : (
                    <Sparkles className="h-5 w-5" />
                  )}
                  <span>Generate Faceless Content</span>
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templates.map((template) => (
                <div key={template.template_id} className="card">
                  <div className="card-header">
                    <h3 className="text-lg font-semibold">{template.name}</h3>
                    <span className="text-sm text-primary-600 bg-primary-100 px-2 py-1 rounded">
                      {template.category}
                    </span>
                  </div>
                  
                  <div className="space-y-4">
                    <p className="text-gray-600">{template.description}</p>
                    
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="h-4 w-4 mr-2" />
                        <span>{template.video_duration}s duration</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Film className="h-4 w-4 mr-2" />
                        <span>{template.video_resolution} • {template.video_quality}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="font-medium">Content Structure:</h4>
                      {template.content_structure.map((section, index) => (
                        <div key={index} className="flex items-center text-sm text-gray-600">
                          <span className="w-2 h-2 bg-primary-500 rounded-full mr-2"></span>
                          <span>{section.type}: {section.duration}s</span>
                        </div>
                      ))}
                    </div>
                    
                    <button
                      onClick={() => generateFromTemplate(template)}
                      disabled={!contentData.tts_text || loading}
                      className="btn-primary w-full"
                    >
                      Use This Template
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Preview Tab */}
        {activeTab === 'preview' && (
          <div className="space-y-6">
            {generatedContent ? (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold">Generated Content</h2>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    generatedContent.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {generatedContent.status}
                  </span>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">{generatedContent.title}</h3>
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{Math.round(generatedContent.duration)}s</span>
                      </div>
                      <div className="flex items-center">
                        <Film className="h-4 w-4 mr-1" />
                        <span>{(generatedContent.file_size / 1024 / 1024).toFixed(1)}MB</span>
                      </div>
                    </div>
                  </div>
                  
                  {generatedContent.video_url && (
                    <div>
                      <h4 className="font-medium mb-2">Generated Video:</h4>
                      <video 
                        src={generatedContent.video_url} 
                        controls 
                        className="w-full max-w-2xl rounded-lg"
                      />
                    </div>
                  )}
                  
                  {generatedContent.audio_url && (
                    <div>
                      <h4 className="font-medium mb-2">Generated Audio:</h4>
                      <audio 
                        src={generatedContent.audio_url} 
                        controls 
                        className="w-full max-w-md"
                      />
                    </div>
                  )}
                  
                  <div className="flex space-x-4">
                    <button
                      onClick={() => {
                        const a = document.createElement('a');
                        a.href = generatedContent.video_url;
                        a.download = `${generatedContent.title}.mp4`;
                        a.click();
                      }}
                      className="btn-primary flex items-center space-x-2"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download Video</span>
                    </button>
                    
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(generatedContent.video_url);
                        toast.success('Video URL copied to clipboard');
                      }}
                      className="btn-secondary flex items-center space-x-2"
                    >
                      <Share2 className="h-4 w-4" />
                      <span>Share</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card text-center py-12">
                <Video className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Content Generated Yet</h3>
                <p className="text-gray-600 mb-4">Generate your first faceless content to see the preview here</p>
                <button
                  onClick={() => setActiveTab('create')}
                  className="btn-primary"
                >
                  Create Content
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            {contentHistory.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {contentHistory.map((content) => (
                  <div key={content.content_id} className="card">
                    <div className="card-header">
                      <h3 className="text-lg font-semibold">{content.title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        content.status === 'completed' ? 'bg-green-100 text-green-800' : 
                        content.status === 'failed' ? 'bg-red-100 text-red-800' : 
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {content.status}
                      </span>
                    </div>
                    
                    <div className="space-y-4">
                      {content.description && (
                        <p className="text-gray-600 text-sm">{content.description}</p>
                      )}
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          <span>{content.duration ? `${Math.round(content.duration)}s` : 'N/A'}</span>
                        </div>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          <span>{new Date(content.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setGeneratedContent(content);
                            setActiveTab('preview');
                          }}
                          className="btn-secondary flex-1 text-sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </button>
                        <button
                          onClick={() => deleteContent(content.content_id)}
                          className="btn-ghost text-red-600 hover:bg-red-50 p-2"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card text-center py-12">
                <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Content History</h3>
                <p className="text-gray-600 mb-4">Your generated content will appear here</p>
                <button
                  onClick={() => setActiveTab('create')}
                  className="btn-primary"
                >
                  Create Your First Content
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* Stats Tab */}
        {activeTab === 'stats' && stats && (
          <div className="space-y-6">
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Content</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_content}</p>
                  </div>
                  <div className="bg-blue-100 p-3 rounded-full">
                    <Film className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Duration</p>
                    <p className="text-2xl font-bold text-gray-900">{Math.round(stats.total_duration / 60)}m</p>
                  </div>
                  <div className="bg-green-100 p-3 rounded-full">
                    <Clock className="h-6 w-6 text-green-600" />
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{Math.round(stats.success_rate)}%</p>
                  </div>
                  <div className="bg-purple-100 p-3 rounded-full">
                    <CheckCircle className="h-6 w-6 text-purple-600" />
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Avg Processing</p>
                    <p className="text-2xl font-bold text-gray-900">{Math.round(stats.avg_processing_time)}s</p>
                  </div>
                  <div className="bg-yellow-100 p-3 rounded-full">
                    <Zap className="h-6 w-6 text-yellow-600" />
                  </div>
                </div>
              </div>
            </div>
            
            {/* Popular Voices */}
            {stats.popular_voices.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold">Popular Voices</h3>
                </div>
                <div className="space-y-3">
                  {stats.popular_voices.map((voice, index) => (
                    <div key={voice.voice_id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-sm text-gray-500">#{index + 1}</span>
                        <span className="font-medium">{voice.voice_id}</span>
                      </div>
                      <span className="text-sm text-gray-600">{voice.count} uses</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Recent Content */}
            {stats.recent_content.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold">Recent Content</h3>
                </div>
                <div className="space-y-3">
                  {stats.recent_content.map((content) => (
                    <div key={content.content_id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{content.title}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(content.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        content.status === 'completed' ? 'bg-green-100 text-green-800' : 
                        content.status === 'failed' ? 'bg-red-100 text-red-800' : 
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {content.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FacelessContentCreator;