# src/tools/file_manager.py
"""
File management plugin for SHADOW
"""
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List

class FileManagerPlugin:
    """File management operations for SHADOW."""
    
    @staticmethod
    def create_file(filepath: str, content: str = "") -> Dict[str, Any]:
        """Create a new file with optional content."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"File created: {filepath}",
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"Failed to create file: {str(e)}"}
    
    @staticmethod
    def read_file(filepath: str, max_size: int = 10000) -> Dict[str, Any]:
        """Read file contents (with size limit for safety)."""
        try:
            if not os.path.exists(filepath):
                return {"error": f"File not found: {filepath}"}
            
            file_size = os.path.getsize(filepath)
            if file_size > max_size:
                return {"error": f"File too large ({file_size} bytes). Max size: {max_size} bytes"}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": file_size,
                "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    @staticmethod
    def copy_file(source: str, destination: str) -> Dict[str, Any]:
        """Copy a file to a new location."""
        try:
            if not os.path.exists(source):
                return {"error": f"Source file not found: {source}"}
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            shutil.copy2(source, destination)
            
            return {
                "success": True,
                "message": f"File copied from {source} to {destination}"
            }
        except Exception as e:
            return {"error": f"Failed to copy file: {str(e)}"}
    
    @staticmethod
    def move_file(source: str, destination: str) -> Dict[str, Any]:
        """Move a file to a new location."""
        try:
            if not os.path.exists(source):
                return {"error": f"Source file not found: {source}"}
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            shutil.move(source, destination)
            
            return {
                "success": True,
                "message": f"File moved from {source} to {destination}"
            }
        except Exception as e:
            return {"error": f"Failed to move file: {str(e)}"}
    
    @staticmethod
    def delete_file(filepath: str, confirm: bool = False) -> Dict[str, Any]:
        """Delete a file (requires confirmation for safety)."""
        if not confirm:
            return {"error": "File deletion requires confirmation. Set confirm=True"}
        
        try:
            if not os.path.exists(filepath):
                return {"error": f"File not found: {filepath}"}
            
            os.remove(filepath)
            
            return {
                "success": True,
                "message": f"File deleted: {filepath}"
            }
        except Exception as e:
            return {"error": f"Failed to delete file: {str(e)}"}
    
    @staticmethod
    def search_files(directory: str, pattern: str = "*", max_results: int = 50) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        import glob
        
        try:
            if not os.path.exists(directory):
                return {"error": f"Directory not found: {directory}"}
            
            search_pattern = os.path.join(directory, "**", pattern)
            files = glob.glob(search_pattern, recursive=True)
            
            # Limit results for performance
            if len(files) > max_results:
                files = files[:max_results]
                truncated = True
            else:
                truncated = False
            
            file_info = []
            for filepath in files:
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    file_info.append({
                        "path": filepath,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return {
                "success": True,
                "files": file_info,
                "total_found": len(file_info),
                "truncated": truncated
            }
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict[str, Any]:
        """Get detailed information about a file."""
        try:
            if not os.path.exists(filepath):
                return {"error": f"File not found: {filepath}"}
            
            stat = os.stat(filepath)
            
            return {
                "success": True,
                "path": filepath,
                "size": stat.st_size,
                "size_human": FileManagerPlugin._format_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": os.path.isfile(filepath),
                "is_directory": os.path.isdir(filepath),
                "extension": os.path.splitext(filepath)[1]
            }
        except Exception as e:
            return {"error": f"Failed to get file info: {str(e)}"}
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
