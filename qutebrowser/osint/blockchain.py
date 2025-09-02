"""Blockchain and cryptocurrency analysis module."""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from decimal import Decimal

import requests
from PyQt6.QtCore import QObject, pyqtSignal

from qutebrowser.utils import message, log
from qutebrowser.osint.core import IntelligenceReport

logger = log.osint_blockchain = logging.getLogger('osint.blockchain')


class BlockchainAnalyzer(QObject):
    """Analyzer for blockchain and cryptocurrency intelligence."""
    
    wallet_identified = pyqtSignal(dict)
    transaction_traced = pyqtSignal(dict)
    cluster_found = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wallet_cache = {}
        self.address_patterns = self._compile_address_patterns()
        
    def _compile_address_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for different cryptocurrency addresses."""
        return {
            'bitcoin': re.compile(r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b'),
            'ethereum': re.compile(r'\b0x[a-fA-F0-9]{40}\b'),
            'litecoin': re.compile(r'\b[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}\b'),
            'dogecoin': re.compile(r'\bD{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}\b'),
            'monero': re.compile(r'\b4[0-9AB][0-9a-zA-Z]{93}\b'),
            'ripple': re.compile(r'\br[a-zA-Z0-9]{24,34}\b'),
            'bitcoin_cash': re.compile(r'\b(bitcoincash:)?(q|p)[a-z0-9]{41}\b'),
            'stellar': re.compile(r'\bG[A-Z2-7]{55}\b'),
            'cardano': re.compile(r'\b(addr1)[a-z0-9]{58}\b'),
            'tron': re.compile(r'\bT[A-Za-z1-9]{33}\b')
        }
        
    def detect_addresses(self, text: str) -> Dict[str, List[str]]:
        """Detect cryptocurrency addresses in text."""
        detected = {}
        
        for crypto, pattern in self.address_patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Remove duplicates while preserving order
                unique_matches = list(dict.fromkeys(matches))
                detected[crypto] = unique_matches
                
                # Only emit signal if we have a QObject parent
                try:
                    for address in unique_matches:
                        self.wallet_identified.emit({
                            'cryptocurrency': crypto,
                            'address': address,
                            'source': 'text_detection'
                        })
                except:
                    pass  # Signal emission failed, likely in test environment
                    
        return detected
    
    def analyze_bitcoin_address(self, address: str) -> Dict[str, Any]:
        """Analyze a Bitcoin address using blockchain APIs."""
        if address in self.wallet_cache:
            return self.wallet_cache[address]
            
        result = {
            'address': address,
            'cryptocurrency': 'bitcoin',
            'balance': 0,
            'total_received': 0,
            'total_sent': 0,
            'transaction_count': 0,
            'first_seen': None,
            'last_seen': None,
            'transactions': [],
            'cluster_info': {},
            'tags': []
        }
        
        try:
            # Query blockchain.info API
            url = f"https://blockchain.info/rawaddr/{address}?limit=50"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                result['balance'] = data.get('final_balance', 0) / 100000000  # Convert from satoshis
                result['total_received'] = data.get('total_received', 0) / 100000000
                result['total_sent'] = data.get('total_sent', 0) / 100000000
                result['transaction_count'] = data.get('n_tx', 0)
                
                # Process transactions
                for tx in data.get('txs', [])[:10]:  # Limit to 10 most recent
                    tx_info = {
                        'hash': tx.get('hash'),
                        'time': datetime.fromtimestamp(tx.get('time', 0)).isoformat(),
                        'inputs': [],
                        'outputs': [],
                        'value': 0
                    }
                    
                    # Process inputs
                    for inp in tx.get('inputs', []):
                        if 'prev_out' in inp:
                            tx_info['inputs'].append({
                                'address': inp['prev_out'].get('addr', 'Unknown'),
                                'value': inp['prev_out'].get('value', 0) / 100000000
                            })
                            
                    # Process outputs
                    for out in tx.get('out', []):
                        tx_info['outputs'].append({
                            'address': out.get('addr', 'Unknown'),
                            'value': out.get('value', 0) / 100000000
                        })
                        
                    result['transactions'].append(tx_info)
                    
                # Determine first and last seen times
                if result['transactions']:
                    result['first_seen'] = result['transactions'][-1]['time']
                    result['last_seen'] = result['transactions'][0]['time']
                    
                self.wallet_cache[address] = result
                
        except Exception as e:
            logger.error(f"Failed to analyze Bitcoin address {address}: {e}")
            
        return result
    
    def analyze_ethereum_address(self, address: str) -> Dict[str, Any]:
        """Analyze an Ethereum address."""
        if address in self.wallet_cache:
            return self.wallet_cache[address]
            
        result = {
            'address': address,
            'cryptocurrency': 'ethereum',
            'balance_eth': 0,
            'balance_usd': 0,
            'transaction_count': 0,
            'token_transfers': [],
            'nft_holdings': [],
            'smart_contracts': [],
            'ens_names': [],
            'defi_protocols': []
        }
        
        try:
            # Query Etherscan API (requires API key in production)
            # For demo, using Ethplorer free API
            url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                eth_info = data.get('ETH', {})
                result['balance_eth'] = eth_info.get('balance', 0)
                result['transaction_count'] = data.get('countTxs', 0)
                
                # Process token holdings
                for token in data.get('tokens', []):
                    token_info = token.get('tokenInfo', {})
                    result['token_transfers'].append({
                        'symbol': token_info.get('symbol'),
                        'name': token_info.get('name'),
                        'balance': token.get('balance', 0),
                        'decimals': token_info.get('decimals', 18)
                    })
                    
                self.wallet_cache[address] = result
                
        except Exception as e:
            logger.error(f"Failed to analyze Ethereum address {address}: {e}")
            
        return result
    
    def cluster_addresses(self, addresses: List[str]) -> Dict[str, List[str]]:
        """Cluster addresses that likely belong to the same entity."""
        clusters = {}
        cluster_id = 0
        
        # Simple clustering based on transaction relationships
        for i, addr1 in enumerate(addresses):
            if addr1 not in [addr for cluster in clusters.values() for addr in cluster]:
                cluster_id += 1
                clusters[f"cluster_{cluster_id}"] = [addr1]
                
                # Check for addresses that transact together
                addr1_data = self.analyze_bitcoin_address(addr1)
                
                for addr2 in addresses[i+1:]:
                    addr2_data = self.analyze_bitcoin_address(addr2)
                    
                    # Check if addresses appear in same transactions
                    addr1_tx_addrs = set()
                    for tx in addr1_data.get('transactions', []):
                        for inp in tx['inputs']:
                            addr1_tx_addrs.add(inp['address'])
                        for out in tx['outputs']:
                            addr1_tx_addrs.add(out['address'])
                            
                    if addr2 in addr1_tx_addrs:
                        clusters[f"cluster_{cluster_id}"].append(addr2)
                        
        self.cluster_found.emit({'clusters': clusters, 'count': len(clusters)})
        return clusters
    
    def search_address_in_leaks(self, address: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrency address in data breaches and leaks."""
        leak_results = []
        
        # This would typically search through breach databases
        # For demo purposes, checking against known patterns
        
        # Check if address appears in common leak patterns
        leak_indicators = [
            {'pattern': 'exchange', 'risk': 'medium'},
            {'pattern': 'mixer', 'risk': 'high'},
            {'pattern': 'darknet', 'risk': 'critical'},
            {'pattern': 'ransomware', 'risk': 'critical'}
        ]
        
        for indicator in leak_indicators:
            # In production, this would query actual breach databases
            if self._check_address_reputation(address, indicator['pattern']):
                leak_results.append({
                    'address': address,
                    'source': indicator['pattern'],
                    'risk_level': indicator['risk'],
                    'timestamp': datetime.now().isoformat()
                })
                
        return leak_results
    
    def _check_address_reputation(self, address: str, pattern: str) -> bool:
        """Check address reputation (placeholder for actual implementation)."""
        # This would query reputation databases in production
        return False
    
    def trace_transaction_flow(self, tx_hash: str, cryptocurrency: str = 'bitcoin') -> Dict[str, Any]:
        """Trace the flow of funds through a transaction."""
        flow = {
            'transaction': tx_hash,
            'cryptocurrency': cryptocurrency,
            'inputs': [],
            'outputs': [],
            'total_value': 0,
            'fee': 0,
            'timestamp': None
        }
        
        try:
            if cryptocurrency == 'bitcoin':
                url = f"https://blockchain.info/rawtx/{tx_hash}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    flow['timestamp'] = datetime.fromtimestamp(data.get('time', 0)).isoformat()
                    flow['fee'] = data.get('fee', 0) / 100000000
                    
                    # Trace inputs
                    for inp in data.get('inputs', []):
                        if 'prev_out' in inp:
                            flow['inputs'].append({
                                'address': inp['prev_out'].get('addr', 'Unknown'),
                                'value': inp['prev_out'].get('value', 0) / 100000000,
                                'spent': inp['prev_out'].get('spent', False)
                            })
                            
                    # Trace outputs
                    for out in data.get('out', []):
                        flow['outputs'].append({
                            'address': out.get('addr', 'Unknown'),
                            'value': out.get('value', 0) / 100000000,
                            'spent': out.get('spent', False)
                        })
                        
                    flow['total_value'] = sum(out['value'] for out in flow['outputs'])
                    
                    self.transaction_traced.emit(flow)
                    
        except Exception as e:
            logger.error(f"Failed to trace transaction {tx_hash}: {e}")
            
        return flow
    
    def identify_exchange_wallets(self, address: str) -> Optional[Dict[str, str]]:
        """Identify if an address belongs to a known exchange."""
        # Known exchange address patterns (simplified)
        exchange_patterns = {
            'binance': ['bnb1', '0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be'],
            'coinbase': ['0x71660c4005ba85c37ccec55d0c4493e66fe775d3'],
            'kraken': ['0x267be94b6e26c4bbaf00bd5f14de2fc47560a7b1'],
            'bitfinex': ['0x1151314c646ce4e0efd76d1af4760ae66a9fe30f']
        }
        
        for exchange, patterns in exchange_patterns.items():
            for pattern in patterns:
                if address.lower().startswith(pattern.lower()):
                    return {
                        'exchange': exchange,
                        'address': address,
                        'type': 'hot_wallet',
                        'confidence': 'medium'
                    }
                    
        return None
    
    def analyze_defi_activity(self, address: str) -> Dict[str, Any]:
        """Analyze DeFi (Decentralized Finance) activity for an address."""
        defi_activity = {
            'address': address,
            'protocols': [],
            'total_value_locked': 0,
            'yield_farming': [],
            'liquidity_pools': [],
            'loans': []
        }
        
        # This would query DeFi protocols in production
        # Example protocols to check
        protocols = ['uniswap', 'compound', 'aave', 'maker', 'curve']
        
        for protocol in protocols:
            # In production, query actual protocol contracts
            activity = self._check_defi_protocol(address, protocol)
            if activity:
                defi_activity['protocols'].append(activity)
                
        return defi_activity
    
    def _check_defi_protocol(self, address: str, protocol: str) -> Optional[Dict[str, Any]]:
        """Check activity in a specific DeFi protocol."""
        # Placeholder for actual DeFi protocol queries
        return None
    
    def create_report(self, address: str, analysis: Dict[str, Any]) -> IntelligenceReport:
        """Create an intelligence report from blockchain analysis."""
        confidence = 0.8  # High confidence for on-chain data
        
        # Adjust confidence based on data quality
        if analysis.get('transaction_count', 0) > 0:
            confidence = 0.9
            
        tags = ['blockchain', 'cryptocurrency', analysis.get('cryptocurrency', 'unknown')]
        
        # Add risk tags if applicable
        if analysis.get('cluster_info'):
            tags.append('clustered')
        if analysis.get('balance', 0) > 100000:  # High value
            tags.append('high_value')
            
        return IntelligenceReport(
            source='blockchain_analyzer',
            target=address,
            data_type='cryptocurrency_address',
            data=analysis,
            confidence=confidence,
            tags=tags
        )