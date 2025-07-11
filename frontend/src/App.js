import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import TextGeneration from './components/TextGeneration';
import ImageGeneration from './components/ImageGeneration';
import VideoGeneration from './components/VideoGeneration';
import CodeGeneration from './components/CodeGeneration';
import SocialMediaGeneration from './components/SocialMediaGeneration';
import WorkflowAutomation from './components/WorkflowAutomation';
import AdminPanel from './components/AdminPanel';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App min-h-screen bg-gray-50">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/text-generation" element={
              <ProtectedRoute>
                <TextGeneration />
              </ProtectedRoute>
            } />
            <Route path="/image-generation" element={
              <ProtectedRoute>
                <ImageGeneration />
              </ProtectedRoute>
            } />
            <Route path="/video-generation" element={
              <ProtectedRoute>
                <VideoGeneration />
              </ProtectedRoute>
            } />
            <Route path="/code-generation" element={
              <ProtectedRoute>
                <CodeGeneration />
              </ProtectedRoute>
            } />
            <Route path="/social-media" element={
              <ProtectedRoute>
                <SocialMediaGeneration />
              </ProtectedRoute>
            } />
            <Route path="/workflows" element={
              <ProtectedRoute>
                <WorkflowAutomation />
              </ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminPanel />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;