
"""
Optional Web Dashboard for GuardianAI
Simple Flask-based monitoring interface
"""

import asyncio
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from typing import Optional

class Dashboard:
    """Optional web dashboard for monitoring"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app = None
        
        if config.enable_dashboard:
            self._setup_flask_app()
    
    def _setup_flask_app(self):
        """Setup Flask application"""
        self.app = Flask(__name__)
        CORS(self.app)
        
        @self.app.route('/')
        def index():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>GuardianAI Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
                    .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
                    .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
                    .stat-label { color: #666; margin-top: 5px; }
                    .status { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 0.9em; }
                    .status.online { background: #d4edda; color: #155724; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🛡️ GuardianAI Dashboard</h1>
                        <span class="status online">🟢 Online</span>
                    </div>
                    <div class="stats" id="stats">
                        <div class="stat-card">
                            <div class="stat-number" id="groups">-</div>
                            <div class="stat-label">Protected Groups</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="messages">-</div>
                            <div class="stat-label">Messages Processed</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="nsfw">-</div>
                            <div class="stat-label">NSFW Blocked</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="spam">-</div>
                            <div class="stat-label">Spam Blocked</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="threats">-</div>
                            <div class="stat-label">Threats Blocked</div>
                        </div>
                    </div>
                </div>
                
                <script>
                    async function updateStats() {
                        try {
                            const response = await fetch('/api/stats');
                            const data = await response.json();
                            
                            document.getElementById('groups').textContent = data.groups || 0;
                            document.getElementById('messages').textContent = data.messages_processed || 0;
                            document.getElementById('nsfw').textContent = data.nsfw_detected || 0;
                            document.getElementById('spam').textContent = data.spam_blocked || 0;
                            document.getElementById('threats').textContent = data.threats_blocked || 0;
                        } catch (error) {
                            console.error('Error fetching stats:', error);
                        }
                    }
                    
                    // Update stats every 30 seconds
                    updateStats();
                    setInterval(updateStats, 30000);
                </script>
            </body>
            </html>
            """
        
        @self.app.route('/api/stats')
        def api_stats():
            try:
                # Get basic stats
                groups = len(self.bot.enabled_groups)
                
                # This would need to be implemented with proper async handling
                # For now, return mock data
                stats = {
                    'groups': groups,
                    'messages_processed': 0,
                    'nsfw_detected': 0,
                    'spam_blocked': 0,
                    'threats_blocked': 0,
                    'status': 'online'
                }
                
                return jsonify(stats)
                
            except Exception as e:
                self.logger.error(f"Error getting dashboard stats: {e}")
                return jsonify({'error': 'Failed to get stats'}), 500
    
    def run(self):
        """Run the dashboard"""
        if self.app and self.config.enable_dashboard:
            try:
                self.logger.info(f"🌐 Starting dashboard on {self.config.dashboard_host}:{self.config.dashboard_port}")
                self.app.run(
                    host=self.config.dashboard_host,
                    port=self.config.dashboard_port,
                    debug=False,
                    threaded=True
                )
            except Exception as e:
                self.logger.error(f"❌ Failed to start dashboard: {e}")
