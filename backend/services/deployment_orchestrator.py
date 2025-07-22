"""
Deployment Orchestrator for Full Stack AI Assistant
Handles containerized and serverless deployments
"""

import asyncio
import json
import yaml
import tempfile
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DeploymentPlatform(str, Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    RAILWAY = "railway"
    AWS_LAMBDA = "aws_lambda"

class DeploymentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class DeploymentResult:
    deployment_id: str
    platform: DeploymentPlatform
    status: DeploymentStatus
    url: Optional[str]
    logs: List[str]
    metrics: Dict[str, Any]
    rollback_available: bool

class DeploymentOrchestrator:
    """
    Orchestrates deployment to various platforms with production-ready configurations
    """
    
    def __init__(self):
        self.deployment_configs = {
            DeploymentPlatform.DOCKER: self._get_docker_config,
            DeploymentPlatform.KUBERNETES: self._get_kubernetes_config,
            DeploymentPlatform.VERCEL: self._get_vercel_config,
            DeploymentPlatform.NETLIFY: self._get_netlify_config,
            DeploymentPlatform.RAILWAY: self._get_railway_config,
            DeploymentPlatform.AWS_LAMBDA: self._get_lambda_config
        }
    
    async def deploy_project(
        self,
        project_id: str,
        platform: DeploymentPlatform,
        project_files: Dict[str, str],
        environment: str = "production",
        custom_config: Optional[Dict[str, Any]] = None
    ) -> DeploymentResult:
        """
        Deploy project to specified platform
        """
        try:
            deployment_id = f"deploy-{project_id}-{platform.value}-{environment}"
            
            # Get platform-specific configuration
            config_generator = self.deployment_configs[platform]
            deployment_config = config_generator(project_files, environment, custom_config)
            
            # Create temporary deployment workspace
            with tempfile.TemporaryDirectory() as temp_dir:
                workspace = Path(temp_dir)
                
                # Prepare deployment files
                await self._prepare_deployment_files(
                    workspace, project_files, deployment_config
                )
                
                # Execute deployment based on platform
                if platform == DeploymentPlatform.DOCKER:
                    result = await self._deploy_docker(workspace, deployment_config, deployment_id)
                elif platform == DeploymentPlatform.KUBERNETES:
                    result = await self._deploy_kubernetes(workspace, deployment_config, deployment_id)
                elif platform == DeploymentPlatform.VERCEL:
                    result = await self._deploy_vercel(workspace, deployment_config, deployment_id)
                elif platform == DeploymentPlatform.NETLIFY:
                    result = await self._deploy_netlify(workspace, deployment_config, deployment_id)
                else:
                    raise ValueError(f"Deployment to {platform} not yet implemented")
                
                return result
                
        except Exception as e:
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=platform,
                status=DeploymentStatus.FAILED,
                url=None,
                logs=[f"Deployment failed: {str(e)}"],
                metrics={},
                rollback_available=False
            )
    
    async def _prepare_deployment_files(
        self,
        workspace: Path,
        project_files: Dict[str, str],
        deployment_config: Dict[str, Any]
    ):
        """Prepare all deployment files in workspace"""
        
        # Write project files
        for file_path, content in project_files.items():
            full_path = workspace / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Write deployment configuration files
        config_files = deployment_config.get("files", {})
        for file_path, content in config_files.items():
            full_path = workspace / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, dict):
                if file_path.endswith('.json'):
                    full_path.write_text(json.dumps(content, indent=2))
                elif file_path.endswith(('.yml', '.yaml')):
                    full_path.write_text(yaml.dump(content, default_flow_style=False))
            else:
                full_path.write_text(content)
    
    async def _deploy_docker(
        self,
        workspace: Path,
        config: Dict[str, Any],
        deployment_id: str
    ) -> DeploymentResult:
        """Deploy using Docker"""
        
        logs = []
        
        try:
            # Build Docker image
            build_cmd = [
                "docker", "build",
                "-t", f"{deployment_id}:latest",
                str(workspace)
            ]
            
            build_result = subprocess.run(
                build_cmd, 
                capture_output=True, 
                text=True, 
                cwd=workspace
            )
            
            logs.append(f"Docker build stdout: {build_result.stdout}")
            if build_result.stderr:
                logs.append(f"Docker build stderr: {build_result.stderr}")
            
            if build_result.returncode != 0:
                raise Exception(f"Docker build failed: {build_result.stderr}")
            
            # Run container
            port_mapping = config.get("port", "3000")
            run_cmd = [
                "docker", "run", "-d",
                "-p", f"{port_mapping}:{port_mapping}",
                "--name", deployment_id,
                f"{deployment_id}:latest"
            ]
            
            run_result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True
            )
            
            logs.append(f"Docker run stdout: {run_result.stdout}")
            if run_result.stderr:
                logs.append(f"Docker run stderr: {run_result.stderr}")
            
            if run_result.returncode != 0:
                raise Exception(f"Docker run failed: {run_result.stderr}")
            
            container_id = run_result.stdout.strip()
            
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=DeploymentPlatform.DOCKER,
                status=DeploymentStatus.SUCCESS,
                url=f"http://localhost:{port_mapping}",
                logs=logs,
                metrics={"container_id": container_id},
                rollback_available=True
            )
            
        except Exception as e:
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=DeploymentPlatform.DOCKER,
                status=DeploymentStatus.FAILED,
                url=None,
                logs=logs + [f"Deployment error: {str(e)}"],
                metrics={},
                rollback_available=False
            )
    
    async def _deploy_kubernetes(
        self,
        workspace: Path,
        config: Dict[str, Any],
        deployment_id: str
    ) -> DeploymentResult:
        """Deploy using Kubernetes"""
        
        logs = []
        
        try:
            # Apply Kubernetes manifests
            kubectl_cmd = ["kubectl", "apply", "-f", str(workspace / "k8s")]
            
            kubectl_result = subprocess.run(
                kubectl_cmd,
                capture_output=True,
                text=True,
                cwd=workspace
            )
            
            logs.append(f"kubectl apply stdout: {kubectl_result.stdout}")
            if kubectl_result.stderr:
                logs.append(f"kubectl apply stderr: {kubectl_result.stderr}")
            
            if kubectl_result.returncode != 0:
                raise Exception(f"Kubernetes deployment failed: {kubectl_result.stderr}")
            
            # Wait for deployment to be ready
            wait_cmd = [
                "kubectl", "wait", "--for=condition=available", "--timeout=300s",
                f"deployment/{deployment_id}"
            ]
            
            wait_result = subprocess.run(wait_cmd, capture_output=True, text=True)
            
            logs.append(f"kubectl wait stdout: {wait_result.stdout}")
            
            # Get service URL
            service_url = await self._get_kubernetes_service_url(deployment_id)
            
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=DeploymentPlatform.KUBERNETES,
                status=DeploymentStatus.SUCCESS,
                url=service_url,
                logs=logs,
                metrics={"namespace": "default"},
                rollback_available=True
            )
            
        except Exception as e:
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=DeploymentPlatform.KUBERNETES,
                status=DeploymentStatus.FAILED,
                url=None,
                logs=logs + [f"Deployment error: {str(e)}"],
                metrics={},
                rollback_available=False
            )
    
    async def _deploy_vercel(
        self,
        workspace: Path,
        config: Dict[str, Any],
        deployment_id: str
    ) -> DeploymentResult:
        """Deploy using Vercel"""
        
        logs = []
        
        try:
            # Use Vercel CLI for deployment
            vercel_cmd = ["vercel", "--prod", "--yes"]
            
            # Set environment variables if provided
            env_vars = config.get("environment_variables", {})
            for key, value in env_vars.items():
                vercel_cmd.extend(["--env", f"{key}={value}"])
            
            vercel_result = subprocess.run(
                vercel_cmd,
                capture_output=True,
                text=True,
                cwd=workspace
            )
            
            logs.append(f"Vercel deploy stdout: {vercel_result.stdout}")
            if vercel_result.stderr:
                logs.append(f"Vercel deploy stderr: {vercel_result.stderr}")
            
            if vercel_result.returncode != 0:
                raise Exception(f"Vercel deployment failed: {vercel_result.stderr}")
            
            # Extract deployment URL from output
            deployment_url = self._extract_vercel_url(vercel_result.stdout)
            
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=DeploymentPlatform.VERCEL,
                status=DeploymentStatus.SUCCESS,
                url=deployment_url,
                logs=logs,
                metrics={"build_time": "auto"},
                rollback_available=True
            )
            
        except Exception as e:
            return DeploymentResult(
                deployment_id=deployment_id,
                platform=DeploymentPlatform.VERCEL,
                status=DeploymentStatus.FAILED,
                url=None,
                logs=logs + [f"Deployment error: {str(e)}"],
                metrics={},
                rollback_available=False
            )
    
    def _get_docker_config(
        self,
        project_files: Dict[str, str],
        environment: str,
        custom_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Docker deployment configuration"""
        
        # Detect project type
        has_frontend = any(f.startswith('frontend/') for f in project_files.keys())
        has_backend = any(f.startswith('backend/') for f in project_files.keys())
        
        dockerfiles = {}
        docker_compose = None
        
        if has_backend:
            # Generate backend Dockerfile
            dockerfiles["backend/Dockerfile"] = self._generate_backend_dockerfile()
            
        if has_frontend:
            # Generate frontend Dockerfile
            dockerfiles["frontend/Dockerfile"] = self._generate_frontend_dockerfile()
        
        if has_frontend and has_backend:
            # Generate docker-compose.yml for full-stack app
            docker_compose = self._generate_docker_compose()
        
        config = {
            "files": dockerfiles,
            "port": custom_config.get("port", "3000") if custom_config else "3000",
            "environment": environment
        }
        
        if docker_compose:
            config["files"]["docker-compose.yml"] = docker_compose
        
        return config
    
    def _get_kubernetes_config(
        self,
        project_files: Dict[str, str],
        environment: str,
        custom_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Kubernetes deployment configuration"""
        
        k8s_manifests = {}
        
        # Generate deployment manifest
        k8s_manifests["k8s/deployment.yaml"] = self._generate_k8s_deployment()
        
        # Generate service manifest
        k8s_manifests["k8s/service.yaml"] = self._generate_k8s_service()
        
        # Generate ingress manifest
        k8s_manifests["k8s/ingress.yaml"] = self._generate_k8s_ingress()
        
        # Generate horizontal pod autoscaler
        k8s_manifests["k8s/hpa.yaml"] = self._generate_k8s_hpa()
        
        return {
            "files": k8s_manifests,
            "namespace": custom_config.get("namespace", "default") if custom_config else "default",
            "environment": environment
        }
    
    def _get_vercel_config(
        self,
        project_files: Dict[str, str],
        environment: str,
        custom_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Vercel deployment configuration"""
        
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "frontend/package.json",
                    "use": "@vercel/node"
                }
            ],
            "routes": [
                {"src": "/api/(.*)", "dest": "/backend/$1"},
                {"src": "/(.*)", "dest": "/frontend/$1"}
            ]
        }
        
        return {
            "files": {
                "vercel.json": vercel_config,
                "package.json": self._generate_vercel_package_json()
            },
            "environment_variables": custom_config.get("env", {}) if custom_config else {}
        }
    
    def _generate_backend_dockerfile(self) -> str:
        """Generate optimized backend Dockerfile"""
        return """
# Multi-stage Docker build for production optimization
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8001/api/health || exit 1

# Start application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
"""
    
    def _generate_frontend_dockerfile(self) -> str:
        """Generate optimized frontend Dockerfile"""
        return """
# Multi-stage build for optimized production image
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
COPY frontend/yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY frontend/ .

# Build application
RUN yarn build

# Production stage with nginx
FROM nginx:alpine as production

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""
    
    def _generate_docker_compose(self) -> Dict[str, Any]:
        """Generate docker-compose configuration"""
        return {
            "version": "3.8",
            "services": {
                "frontend": {
                    "build": {
                        "context": ".",
                        "dockerfile": "frontend/Dockerfile"
                    },
                    "ports": ["3000:80"],
                    "depends_on": ["backend"],
                    "environment": {
                        "REACT_APP_API_URL": "http://backend:8001"
                    }
                },
                "backend": {
                    "build": {
                        "context": ".",
                        "dockerfile": "backend/Dockerfile"
                    },
                    "ports": ["8001:8001"],
                    "depends_on": ["database"],
                    "environment": {
                        "DATABASE_URL": "postgresql://user:pass@database:5432/appdb"
                    }
                },
                "database": {
                    "image": "postgres:15-alpine",
                    "environment": {
                        "POSTGRES_DB": "appdb",
                        "POSTGRES_USER": "user",
                        "POSTGRES_PASSWORD": "pass"
                    },
                    "volumes": ["postgres_data:/var/lib/postgresql/data"]
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"]
                }
            },
            "volumes": {
                "postgres_data": {}
            },
            "networks": {
                "default": {
                    "driver": "bridge"
                }
            }
        }
    
    def _generate_k8s_deployment(self) -> Dict[str, Any]:
        """Generate Kubernetes deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment", 
            "metadata": {
                "name": "fullstack-app",
                "labels": {"app": "fullstack-app"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "fullstack-app"}},
                "template": {
                    "metadata": {"labels": {"app": "fullstack-app"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "frontend",
                                "image": "fullstack-app-frontend:latest",
                                "ports": [{"containerPort": 80}],
                                "resources": {
                                    "requests": {"memory": "64Mi", "cpu": "50m"},
                                    "limits": {"memory": "128Mi", "cpu": "100m"}
                                }
                            },
                            {
                                "name": "backend",
                                "image": "fullstack-app-backend:latest",
                                "ports": [{"containerPort": 8001}],
                                "resources": {
                                    "requests": {"memory": "256Mi", "cpu": "100m"},
                                    "limits": {"memory": "512Mi", "cpu": "500m"}
                                },
                                "env": [
                                    {"name": "DATABASE_URL", "valueFrom": {"secretKeyRef": {"name": "app-secrets", "key": "database-url"}}}
                                ]
                            }
                        ]
                    }
                }
            }
        }
    
    def _generate_k8s_service(self) -> Dict[str, Any]:
        """Generate Kubernetes service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "fullstack-app-service",
                "labels": {"app": "fullstack-app"}
            },
            "spec": {
                "selector": {"app": "fullstack-app"},
                "ports": [
                    {"name": "frontend", "port": 80, "targetPort": 80},
                    {"name": "backend", "port": 8001, "targetPort": 8001}
                ],
                "type": "ClusterIP"
            }
        }
    
    async def _get_kubernetes_service_url(self, deployment_id: str) -> str:
        """Get Kubernetes service URL"""
        # This would typically involve checking ingress or load balancer
        return f"http://localhost:8080/api/v1/proxy/namespaces/default/services/{deployment_id}:80/"
    
    def _extract_vercel_url(self, output: str) -> str:
        """Extract deployment URL from Vercel output"""
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                return line.strip()
        return "https://deployment-url.vercel.app"
    
    # Additional helper methods would go here...