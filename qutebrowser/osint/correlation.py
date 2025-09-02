"""Data correlation engine for linking OSINT intelligence across sources."""

import sqlite3
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import networkx as nx

from PyQt6.QtCore import QObject, pyqtSignal

from qutebrowser.utils import log
from qutebrowser.osint.core import IntelligenceReport
try:
    from qutebrowser.utils import standarddir
except ImportError:
    # For testing without full qutebrowser environment
    import tempfile
    from pathlib import Path
    class MockStandardDir:
        @staticmethod
        def data():
            return Path(tempfile.gettempdir()) / 'qutebrowser_test'
    standarddir = MockStandardDir()

logger = log.osint_correlation = logging.getLogger('osint.correlation')


class CorrelationDatabase(QObject):
    """SQLite-based correlation engine for OSINT data."""
    
    correlation_found = pyqtSignal(dict)
    entity_linked = pyqtSignal(dict)
    pattern_detected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = Path(standarddir.data()) / 'osint' / 'correlation.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.graph = nx.Graph()
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence REAL DEFAULT 0.5,
                metadata TEXT,
                UNIQUE(entity_type, entity_value)
            )
        ''')
        
        # Create relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                source_entity_id TEXT NOT NULL,
                target_entity_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                evidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_entity_id) REFERENCES entities(entity_id),
                FOREIGN KEY (target_entity_id) REFERENCES entities(entity_id)
            )
        ''')
        
        # Create observations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                observation_id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                source TEXT NOT NULL,
                observation_type TEXT NOT NULL,
                data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
            )
        ''')
        
        # Create indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators (
                indicator_id TEXT PRIMARY KEY,
                indicator_type TEXT NOT NULL,
                indicator_value TEXT NOT NULL,
                entity_id TEXT,
                tags TEXT,
                severity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
            )
        ''')
        
        # Create correlation_rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlation_rules (
                rule_id TEXT PRIMARY KEY,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                conditions TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create indices for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity_value ON entities(entity_value)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationship_source ON relationships(source_entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationship_target ON relationships(target_entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_observation_entity ON observations(entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicator_value ON indicators(indicator_value)')
        
        self.conn.commit()
        
        # Load default correlation rules
        self._load_default_rules()
        
    def _load_default_rules(self):
        """Load default correlation rules."""
        default_rules = [
            {
                'rule_id': 'email_domain_link',
                'rule_name': 'Email to Domain Correlation',
                'rule_type': 'pattern',
                'conditions': json.dumps({
                    'pattern': r'(.+)@(.+)',
                    'link_type': 'email_domain'
                }),
                'priority': 8
            },
            {
                'rule_id': 'ip_asn_link',
                'rule_name': 'IP to ASN Correlation',
                'rule_type': 'network',
                'conditions': json.dumps({
                    'entity_types': ['ip_address', 'asn']
                }),
                'priority': 7
            },
            {
                'rule_id': 'cert_domain_link',
                'rule_name': 'Certificate to Domain Correlation',
                'rule_type': 'certificate',
                'conditions': json.dumps({
                    'entity_types': ['ssl_cert', 'domain']
                }),
                'priority': 9
            },
            {
                'rule_id': 'blockchain_cluster',
                'rule_name': 'Blockchain Address Clustering',
                'rule_type': 'blockchain',
                'conditions': json.dumps({
                    'entity_type': 'crypto_address',
                    'cluster_threshold': 0.7
                }),
                'priority': 6
            }
        ]
        
        cursor = self.conn.cursor()
        for rule in default_rules:
            cursor.execute('''
                INSERT OR IGNORE INTO correlation_rules 
                (rule_id, rule_name, rule_type, conditions, priority)
                VALUES (?, ?, ?, ?, ?)
            ''', (rule['rule_id'], rule['rule_name'], rule['rule_type'],
                 rule['conditions'], rule['priority']))
        
        self.conn.commit()
        
    def add_entity(self, entity_type: str, entity_value: str, 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add or update an entity in the database."""
        entity_id = hashlib.sha256(f"{entity_type}:{entity_value}".encode()).hexdigest()[:16]
        
        cursor = self.conn.cursor()
        
        # Check if entity exists
        cursor.execute('''
            SELECT entity_id FROM entities 
            WHERE entity_type = ? AND entity_value = ?
        ''', (entity_type, entity_value))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update last_seen
            cursor.execute('''
                UPDATE entities 
                SET last_seen = CURRENT_TIMESTAMP,
                    metadata = ?
                WHERE entity_id = ?
            ''', (json.dumps(metadata) if metadata else None, existing['entity_id']))
            entity_id = existing['entity_id']
        else:
            # Insert new entity
            cursor.execute('''
                INSERT INTO entities (entity_id, entity_type, entity_value, metadata)
                VALUES (?, ?, ?, ?)
            ''', (entity_id, entity_type, entity_value, 
                 json.dumps(metadata) if metadata else None))
            
            # Add to graph
            self.graph.add_node(entity_id, type=entity_type, value=entity_value)
            
        self.conn.commit()
        
        # Run correlation rules
        self._run_correlation_rules(entity_id)
        
        return entity_id
        
    def add_relationship(self, source_entity_id: str, target_entity_id: str,
                        relationship_type: str, confidence: float = 0.5,
                        evidence: Optional[Dict[str, Any]] = None) -> str:
        """Add a relationship between two entities."""
        relationship_id = hashlib.sha256(
            f"{source_entity_id}:{target_entity_id}:{relationship_type}".encode()
        ).hexdigest()[:16]
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO relationships 
            (relationship_id, source_entity_id, target_entity_id, 
             relationship_type, confidence, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (relationship_id, source_entity_id, target_entity_id,
             relationship_type, confidence, json.dumps(evidence) if evidence else None))
        
        self.conn.commit()
        
        # Add edge to graph
        self.graph.add_edge(source_entity_id, target_entity_id,
                          type=relationship_type, confidence=confidence)
        
        self.entity_linked.emit({
            'source': source_entity_id,
            'target': target_entity_id,
            'type': relationship_type
        })
        
        return relationship_id
        
    def add_observation(self, entity_id: str, source: str,
                       observation_type: str, data: Dict[str, Any]) -> str:
        """Add an observation about an entity."""
        observation_id = hashlib.sha256(
            f"{entity_id}:{source}:{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO observations 
            (observation_id, entity_id, source, observation_type, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (observation_id, entity_id, source, observation_type, json.dumps(data)))
        
        self.conn.commit()
        
        return observation_id
        
    def correlate_data(self, data_type: str, data_value: str) -> List[Dict[str, Any]]:
        """Find correlations for a given data point."""
        correlations = []
        
        # First, find or create the entity
        entity_id = self.add_entity(data_type, data_value)
        
        cursor = self.conn.cursor()
        
        # Find direct relationships
        cursor.execute('''
            SELECT r.*, 
                   e1.entity_type as source_type, e1.entity_value as source_value,
                   e2.entity_type as target_type, e2.entity_value as target_value
            FROM relationships r
            JOIN entities e1 ON r.source_entity_id = e1.entity_id
            JOIN entities e2 ON r.target_entity_id = e2.entity_id
            WHERE r.source_entity_id = ? OR r.target_entity_id = ?
            ORDER BY r.confidence DESC
        ''', (entity_id, entity_id))
        
        for row in cursor.fetchall():
            correlations.append({
                'relationship_type': row['relationship_type'],
                'confidence': row['confidence'],
                'source': {
                    'type': row['source_type'],
                    'value': row['source_value']
                },
                'target': {
                    'type': row['target_type'],
                    'value': row['target_value']
                }
            })
            
        # Find indirect relationships using graph
        if entity_id in self.graph:
            # Find nodes within 2 hops
            for neighbor in nx.single_source_shortest_path_length(
                self.graph, entity_id, cutoff=2
            ):
                if neighbor != entity_id:
                    path = nx.shortest_path(self.graph, entity_id, neighbor)
                    
                    cursor.execute('''
                        SELECT entity_type, entity_value 
                        FROM entities WHERE entity_id = ?
                    ''', (neighbor,))
                    
                    neighbor_entity = cursor.fetchone()
                    if neighbor_entity:
                        correlations.append({
                            'relationship_type': 'indirect',
                            'confidence': 0.3,
                            'hops': len(path) - 1,
                            'path': path,
                            'entity': {
                                'type': neighbor_entity['entity_type'],
                                'value': neighbor_entity['entity_value']
                            }
                        })
                        
        self.correlation_found.emit({
            'entity': {'type': data_type, 'value': data_value},
            'correlations': correlations
        })
        
        return correlations
        
    def _run_correlation_rules(self, entity_id: str):
        """Run correlation rules for a new entity."""
        cursor = self.conn.cursor()
        
        # Get entity details
        cursor.execute('''
            SELECT entity_type, entity_value, metadata 
            FROM entities WHERE entity_id = ?
        ''', (entity_id,))
        
        entity = cursor.fetchone()
        if not entity:
            return
            
        # Get enabled rules
        cursor.execute('''
            SELECT * FROM correlation_rules 
            WHERE enabled = 1 
            ORDER BY priority DESC
        ''')
        
        for rule in cursor.fetchall():
            conditions = json.loads(rule['conditions'])
            
            if rule['rule_type'] == 'pattern':
                self._apply_pattern_rule(entity_id, entity, conditions)
            elif rule['rule_type'] == 'network':
                self._apply_network_rule(entity_id, entity, conditions)
            elif rule['rule_type'] == 'certificate':
                self._apply_certificate_rule(entity_id, entity, conditions)
            elif rule['rule_type'] == 'blockchain':
                self._apply_blockchain_rule(entity_id, entity, conditions)
                
    def _apply_pattern_rule(self, entity_id: str, entity: sqlite3.Row,
                           conditions: Dict[str, Any]):
        """Apply pattern-based correlation rule."""
        import re
        
        pattern = conditions.get('pattern')
        if not pattern:
            return
            
        match = re.match(pattern, entity['entity_value'])
        if match:
            # Extract parts and create relationships
            if entity['entity_type'] == 'email':
                username, domain = entity['entity_value'].split('@')
                
                # Add domain entity
                domain_id = self.add_entity('domain', domain)
                
                # Create relationship
                self.add_relationship(
                    entity_id, domain_id,
                    'email_domain',
                    confidence=0.9,
                    evidence={'source': 'pattern_match'}
                )
                
                # Add username entity
                username_id = self.add_entity('username', username)
                self.add_relationship(
                    entity_id, username_id,
                    'email_username',
                    confidence=0.9,
                    evidence={'source': 'pattern_match'}
                )
                
    def _apply_network_rule(self, entity_id: str, entity: sqlite3.Row,
                           conditions: Dict[str, Any]):
        """Apply network-based correlation rule."""
        if entity['entity_type'] == 'ip_address':
            # Look for ASN information
            from qutebrowser.osint.bgp import BGPAnalyzer
            bgp = BGPAnalyzer()
            
            bgp_data = bgp.analyze_ip(entity['entity_value'])
            
            if bgp_data.get('asn'):
                # Add ASN entity
                asn_id = self.add_entity(
                    'asn',
                    str(bgp_data['asn']),
                    metadata={'name': bgp_data.get('asn_name')}
                )
                
                # Create relationship
                self.add_relationship(
                    entity_id, asn_id,
                    'ip_in_asn',
                    confidence=0.95,
                    evidence={'source': 'bgp_lookup', 'data': bgp_data}
                )
                
    def _apply_certificate_rule(self, entity_id: str, entity: sqlite3.Row,
                               conditions: Dict[str, Any]):
        """Apply certificate-based correlation rule."""
        if entity['entity_type'] == 'domain':
            # Look for SSL certificates
            from qutebrowser.osint.certificates import CertificateIntelligence
            cert_intel = CertificateIntelligence()
            
            cert_data = cert_intel.get_certificate(entity['entity_value'])
            
            if cert_data:
                # Add certificate entity
                cert_id = self.add_entity(
                    'ssl_cert',
                    cert_data['fingerprint_sha256'],
                    metadata=cert_data
                )
                
                # Create relationship
                self.add_relationship(
                    entity_id, cert_id,
                    'has_certificate',
                    confidence=1.0,
                    evidence={'source': 'direct_observation'}
                )
                
                # Add SANs as related domains
                for san in cert_data.get('san', []):
                    san_id = self.add_entity('domain', san)
                    self.add_relationship(
                        cert_id, san_id,
                        'certificate_san',
                        confidence=1.0,
                        evidence={'source': 'certificate_san'}
                    )
                    
    def _apply_blockchain_rule(self, entity_id: str, entity: sqlite3.Row,
                              conditions: Dict[str, Any]):
        """Apply blockchain-based correlation rule."""
        if entity['entity_type'] == 'crypto_address':
            # Look for transaction relationships
            from qutebrowser.osint.blockchain import BlockchainAnalyzer
            blockchain = BlockchainAnalyzer()
            
            analysis = blockchain.analyze_bitcoin_address(entity['entity_value'])
            
            # Find addresses that transact together
            related_addresses = set()
            for tx in analysis.get('transactions', []):
                for inp in tx.get('inputs', []):
                    if inp['address'] != entity['entity_value']:
                        related_addresses.add(inp['address'])
                for out in tx.get('outputs', []):
                    if out['address'] != entity['entity_value']:
                        related_addresses.add(out['address'])
                        
            # Create relationships with frequently appearing addresses
            for addr in related_addresses:
                addr_id = self.add_entity('crypto_address', addr)
                self.add_relationship(
                    entity_id, addr_id,
                    'transacts_with',
                    confidence=0.7,
                    evidence={'source': 'blockchain_analysis'}
                )
                
    def find_patterns(self, entity_type: Optional[str] = None,
                     time_window: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find patterns in the correlated data."""
        patterns = []
        
        cursor = self.conn.cursor()
        
        # Find entities with many relationships (hubs)
        query = '''
            SELECT e.entity_id, e.entity_type, e.entity_value, 
                   COUNT(DISTINCT r.relationship_id) as relationship_count
            FROM entities e
            LEFT JOIN relationships r ON (
                e.entity_id = r.source_entity_id OR 
                e.entity_id = r.target_entity_id
            )
        '''
        
        params = []
        conditions = []
        
        if entity_type:
            conditions.append('e.entity_type = ?')
            params.append(entity_type)
            
        if time_window:
            cutoff = datetime.now() - timedelta(days=time_window)
            conditions.append('e.last_seen >= ?')
            params.append(cutoff)
            
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        query += ' GROUP BY e.entity_id HAVING relationship_count > 5'
        query += ' ORDER BY relationship_count DESC'
        
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'hub_entity',
                'entity': {
                    'type': row['entity_type'],
                    'value': row['entity_value']
                },
                'relationship_count': row['relationship_count']
            })
            
        # Find strongly connected components in the graph
        if len(self.graph) > 0:
            components = list(nx.strongly_connected_components(
                self.graph.to_directed()
            ))
            
            for component in components:
                if len(component) > 2:
                    patterns.append({
                        'type': 'connected_cluster',
                        'size': len(component),
                        'entities': list(component)
                    })
                    
        self.pattern_detected.emit({'patterns': patterns})
        
        return patterns
        
    def export_graph(self, format: str = 'json') -> str:
        """Export the correlation graph."""
        if format == 'json':
            # Convert graph to JSON format
            data = nx.node_link_data(self.graph)
            
            # Add entity details
            cursor = self.conn.cursor()
            for node in data['nodes']:
                cursor.execute('''
                    SELECT entity_type, entity_value 
                    FROM entities WHERE entity_id = ?
                ''', (node['id'],))
                
                entity = cursor.fetchone()
                if entity:
                    node['entity_type'] = entity['entity_type']
                    node['entity_value'] = entity['entity_value']
                    
            return json.dumps(data, indent=2)
            
        elif format == 'gexf':
            # Export to GEXF format for Gephi
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.gexf', delete=False) as f:
                nx.write_gexf(self.graph, f.name)
                return f.name
                
        elif format == 'graphml':
            # Export to GraphML format
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
                nx.write_graphml(self.graph, f.name)
                return f.name
                
    def query_entities(self, entity_type: Optional[str] = None,
                      search_term: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Query entities from the database."""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT e.*, COUNT(DISTINCT o.observation_id) as observation_count
            FROM entities e
            LEFT JOIN observations o ON e.entity_id = o.entity_id
        '''
        
        params = []
        conditions = []
        
        if entity_type:
            conditions.append('e.entity_type = ?')
            params.append(entity_type)
            
        if search_term:
            conditions.append('e.entity_value LIKE ?')
            params.append(f'%{search_term}%')
            
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        query += ' GROUP BY e.entity_id'
        query += ' ORDER BY e.last_seen DESC'
        query += f' LIMIT {limit}'
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'entity_id': row['entity_id'],
                'entity_type': row['entity_type'],
                'entity_value': row['entity_value'],
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'confidence': row['confidence'],
                'observation_count': row['observation_count'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None
            })
            
        return results
        
    def get_entity_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get timeline of observations for an entity."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM observations 
            WHERE entity_id = ? 
            ORDER BY timestamp DESC
        ''', (entity_id,))
        
        timeline = []
        for row in cursor.fetchall():
            timeline.append({
                'observation_id': row['observation_id'],
                'source': row['source'],
                'type': row['observation_type'],
                'timestamp': row['timestamp'],
                'data': json.loads(row['data']) if row['data'] else None
            })
            
        return timeline