"""Core OSINT engine for coordinating intelligence gathering operations."""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from qutebrowser.utils import message, log
try:
    from qutebrowser.utils import standarddir
    from qutebrowser.config import config
except ImportError:
    # For testing without full qutebrowser environment
    import tempfile
    class MockStandardDir:
        @staticmethod
        def data():
            return Path(tempfile.gettempdir()) / 'qutebrowser_test'
    standarddir = MockStandardDir()
    config = None

logger = log.osint = logging.getLogger('osint')


@dataclass
class IntelligenceReport:
    """Container for intelligence gathering results."""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    target: str = ""
    data_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'target': self.target,
            'data_type': self.data_type,
            'data': self.data,
            'confidence': self.confidence,
            'tags': self.tags
        }


class OSINTEngine(QObject):
    """Main OSINT engine coordinating all intelligence modules."""
    
    intelligence_gathered = pyqtSignal(dict)
    analysis_complete = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reports: List[IntelligenceReport] = []
        self.active_operations: Dict[str, asyncio.Task] = {}
        self._init_storage()
        
    def _init_storage(self):
        """Initialize storage directory for OSINT data."""
        self.storage_path = Path(standarddir.data()) / 'osint'
        self.storage_path.mkdir(exist_ok=True)
        
        self.reports_path = self.storage_path / 'reports'
        self.reports_path.mkdir(exist_ok=True)
        
        self.cache_path = self.storage_path / 'cache'
        self.cache_path.mkdir(exist_ok=True)
        
    def add_report(self, report: IntelligenceReport):
        """Add a new intelligence report."""
        self.reports.append(report)
        self.intelligence_gathered.emit(report.to_dict())
        self._save_report(report)
        logger.info(f"Added intelligence report: {report.data_type} for {report.target}")
        
    def _save_report(self, report: IntelligenceReport):
        """Save report to disk."""
        filename = f"{report.timestamp.strftime('%Y%m%d_%H%M%S')}_{report.data_type}_{report.target[:20]}.json"
        filepath = self.reports_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
            
    def get_reports(self, target: Optional[str] = None, 
                   data_type: Optional[str] = None) -> List[IntelligenceReport]:
        """Get filtered intelligence reports."""
        reports = self.reports
        
        if target:
            reports = [r for r in reports if target in r.target]
        if data_type:
            reports = [r for r in reports if r.data_type == data_type]
            
        return reports
    
    def analyze_url(self, url: QUrl) -> Dict[str, Any]:
        """Perform comprehensive OSINT analysis on a URL."""
        host = url.host()
        result = {
            'url': url.toString(),
            'host': host,
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        message.info(f"Starting OSINT analysis for {host}")
        self.analysis_complete.emit(f"OSINT analysis started for {host}")
        
        return result
    
    def clear_cache(self):
        """Clear cached OSINT data."""
        for file in self.cache_path.glob('*'):
            file.unlink()
        logger.info("OSINT cache cleared")
        
    def export_reports(self, filepath: str, format: str = 'json'):
        """Export all reports to a file."""
        if format == 'json':
            data = [r.to_dict() for r in self.reports]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'csv':
            import csv
            with open(filepath, 'w', newline='') as f:
                if self.reports:
                    fieldnames = ['timestamp', 'source', 'target', 'data_type', 'confidence', 'tags']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for report in self.reports:
                        row = report.to_dict()
                        row['tags'] = ', '.join(row['tags'])
                        row.pop('data', None)
                        writer.writerow(row)