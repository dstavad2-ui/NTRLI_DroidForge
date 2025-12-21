"""
DroidForge GitHub Integration
=============================
Integration with GitHub API for repository management and CI/CD control.
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin

from utils.logger import get_logger


@dataclass
class WorkflowRun:
    """Represents a GitHub Actions workflow run."""
    id: int
    name: str
    status: str
    conclusion: Optional[str]
    created_at: str
    updated_at: str
    html_url: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowRun':
        return cls(
            id=data['id'],
            name=data.get('name', ''),
            status=data.get('status', ''),
            conclusion=data.get('conclusion'),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            html_url=data.get('html_url', '')
        )


@dataclass
class Repository:
    """Represents a GitHub repository."""
    owner: str
    name: str
    full_name: str
    default_branch: str
    private: bool
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Repository':
        return cls(
            owner=data['owner']['login'],
            name=data['name'],
            full_name=data['full_name'],
            default_branch=data.get('default_branch', 'main'),
            private=data.get('private', False)
        )


class GitHubIntegration:
    """
    GitHub API integration for DroidForge.
    
    Provides:
    - Repository information
    - Workflow dispatch (trigger builds)
    - Workflow run status
    - Artifact retrieval
    - File operations
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, config_manager, event_bus):
        self.config = config_manager
        self.event_bus = event_bus
        self.logger = get_logger("GitHub")
        
        # Get credentials
        self._token = self.config.get("github.token", os.environ.get("GITHUB_TOKEN", ""))
        self._owner = self.config.get("github.owner", "")
        self._repo = self.config.get("github.repo", "")
    
    @property
    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured."""
        return bool(self._token and self._owner and self._repo)
    
    def _request(self, method: str, endpoint: str, data: Dict = None,
                 headers: Dict = None) -> Dict:
        """
        Make an authenticated request to GitHub API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
            
        Returns:
            Response JSON
        """
        url = urljoin(self.BASE_URL + "/", endpoint.lstrip("/"))
        
        req_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if headers:
            req_headers.update(headers)
        
        body = None
        if data:
            body = json.dumps(data).encode('utf-8')
            req_headers["Content-Type"] = "application/json"
        
        request = Request(url, data=body, headers=req_headers, method=method)
        
        try:
            with urlopen(request, timeout=30) as response:
                if response.status == 204:  # No content
                    return {"status": "success"}
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            self.logger.error(f"GitHub API error: {e.code} - {error_body}")
            raise GitHubError(f"GitHub API error: {e.code}", e.code, error_body)
        except URLError as e:
            self.logger.error(f"Network error: {e}")
            raise GitHubError(f"Network error: {e}")
    
    def get_repository(self) -> Repository:
        """Get repository information."""
        endpoint = f"/repos/{self._owner}/{self._repo}"
        data = self._request("GET", endpoint)
        return Repository.from_dict(data)
    
    def trigger_workflow(self, workflow_file: str, ref: str = "main",
                        inputs: Dict[str, str] = None) -> Dict:
        """
        Trigger a workflow dispatch event.
        
        Args:
            workflow_file: Workflow file name (e.g., "build.yml")
            ref: Git ref to run workflow on
            inputs: Workflow inputs
            
        Returns:
            Dispatch result
        """
        if not self.is_configured:
            raise GitHubError("GitHub integration not configured")
        
        endpoint = f"/repos/{self._owner}/{self._repo}/actions/workflows/{workflow_file}/dispatches"
        
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        
        self.logger.info(f"Triggering workflow: {workflow_file} on {ref}")
        
        result = self._request("POST", endpoint, data)
        
        self.event_bus.emit("github_workflow_triggered", workflow_file, ref)
        
        return {
            "status": "dispatched",
            "workflow": workflow_file,
            "ref": ref,
            "inputs": inputs
        }
    
    def get_workflow_runs(self, workflow_file: str = None, 
                         limit: int = 10) -> List[WorkflowRun]:
        """
        Get recent workflow runs.
        
        Args:
            workflow_file: Filter by workflow file
            limit: Maximum runs to return
            
        Returns:
            List of WorkflowRun objects
        """
        if workflow_file:
            endpoint = f"/repos/{self._owner}/{self._repo}/actions/workflows/{workflow_file}/runs"
        else:
            endpoint = f"/repos/{self._owner}/{self._repo}/actions/runs"
        
        endpoint += f"?per_page={limit}"
        
        data = self._request("GET", endpoint)
        
        runs = []
        for run_data in data.get('workflow_runs', []):
            runs.append(WorkflowRun.from_dict(run_data))
        
        return runs
    
    def get_workflow_run(self, run_id: int) -> WorkflowRun:
        """Get a specific workflow run."""
        endpoint = f"/repos/{self._owner}/{self._repo}/actions/runs/{run_id}"
        data = self._request("GET", endpoint)
        return WorkflowRun.from_dict(data)
    
    def get_run_artifacts(self, run_id: int) -> List[Dict]:
        """
        Get artifacts from a workflow run.
        
        Args:
            run_id: Workflow run ID
            
        Returns:
            List of artifact metadata
        """
        endpoint = f"/repos/{self._owner}/{self._repo}/actions/runs/{run_id}/artifacts"
        data = self._request("GET", endpoint)
        return data.get('artifacts', [])
    
    def download_artifact(self, artifact_id: int, output_path: str) -> str:
        """
        Download an artifact.
        
        Args:
            artifact_id: Artifact ID
            output_path: Local path to save artifact
            
        Returns:
            Path to downloaded file
        """
        endpoint = f"/repos/{self._owner}/{self._repo}/actions/artifacts/{artifact_id}/zip"
        
        url = urljoin(self.BASE_URL + "/", endpoint.lstrip("/"))
        
        request = Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
        })
        
        with urlopen(request, timeout=120) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        
        self.logger.info(f"Downloaded artifact to: {output_path}")
        return output_path
    
    def get_file_content(self, path: str, ref: str = None) -> str:
        """
        Get file content from repository.
        
        Args:
            path: File path in repository
            ref: Git ref (branch, tag, commit)
            
        Returns:
            File content
        """
        endpoint = f"/repos/{self._owner}/{self._repo}/contents/{path}"
        if ref:
            endpoint += f"?ref={ref}"
        
        data = self._request("GET", endpoint)
        
        if data.get('encoding') == 'base64':
            return base64.b64decode(data['content']).decode('utf-8')
        return data.get('content', '')
    
    def create_or_update_file(self, path: str, content: str, 
                              message: str, branch: str = None) -> Dict:
        """
        Create or update a file in the repository.
        
        Args:
            path: File path
            content: File content
            message: Commit message
            branch: Target branch
            
        Returns:
            Commit information
        """
        endpoint = f"/repos/{self._owner}/{self._repo}/contents/{path}"
        
        # Check if file exists to get SHA
        sha = None
        try:
            existing = self._request("GET", endpoint)
            sha = existing.get('sha')
        except GitHubError as e:
            if e.status_code != 404:
                raise
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
        }
        if sha:
            data["sha"] = sha
        if branch:
            data["branch"] = branch
        
        result = self._request("PUT", endpoint, data)
        
        return {
            "path": path,
            "sha": result.get('content', {}).get('sha'),
            "commit": result.get('commit', {}).get('sha')
        }
    
    def get_branches(self) -> List[str]:
        """Get list of branches."""
        endpoint = f"/repos/{self._owner}/{self._repo}/branches"
        data = self._request("GET", endpoint)
        return [b['name'] for b in data]
    
    def get_latest_release(self) -> Optional[Dict]:
        """Get the latest release."""
        try:
            endpoint = f"/repos/{self._owner}/{self._repo}/releases/latest"
            return self._request("GET", endpoint)
        except GitHubError as e:
            if e.status_code == 404:
                return None
            raise
    
    def create_release(self, tag: str, name: str, body: str,
                      draft: bool = False, prerelease: bool = False) -> Dict:
        """
        Create a new release.
        
        Args:
            tag: Tag name for release
            name: Release title
            body: Release description
            draft: Create as draft
            prerelease: Mark as prerelease
            
        Returns:
            Release information
        """
        endpoint = f"/repos/{self._owner}/{self._repo}/releases"
        
        data = {
            "tag_name": tag,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        
        result = self._request("POST", endpoint, data)
        
        self.logger.info(f"Created release: {tag}")
        self.event_bus.emit("github_release_created", tag, result.get('id'))
        
        return result


class GitHubError(Exception):
    """GitHub API error."""
    
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
