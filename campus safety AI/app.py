from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
from datetime import datetime
import json

app = Flask(__name__)

# Configure Google AI
GOOGLE_API_KEY = "AIzaSyIYMHFlDOJv1yL5oFZqI2MojaQ5-C4"
genai.configure(api_key=GOOGLE_API_KEY)

# In-memory storage for incidents
incidents = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campus Safety & Incident Reporting</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --dark-gradient: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            --card-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            --card-shadow-hover: 0 30px 80px rgba(0, 0, 0, 0.25);
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            padding: 0;
            color: #333;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            pointer-events: none;
            z-index: 1;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 2;
        }

        header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
            animation: fadeInDown 1s ease-out;
        }

        .header-content {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 40px 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        }

        .shield-icon {
            font-size: 4rem;
            margin-bottom: 15px;
            display: inline-block;
            animation: pulse 2s ease-in-out infinite;
            filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        header p {
            font-size: 1.1rem;
            font-weight: 300;
            opacity: 0.9;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 50px;
            animation: fadeInUp 1s ease-out 0.5s both;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px 30px;
            text-align: center;
            box-shadow: var(--card-shadow);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
            min-width: 150px;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--card-shadow-hover);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 800;
            color: #667eea;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #666;
            font-weight: 500;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 50px;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 30px;
            box-shadow: var(--card-shadow);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
            animation: fadeIn 1s ease-out 1s both;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: var(--card-shadow-hover);
        }

        .card h2 {
            color: #333;
            margin-bottom: 25px;
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .badge-new {
            background: #ff4757;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            animation: bounce 1s ease-in-out infinite;
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-3px); }
            60% { transform: translateY(-2px); }
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }

        .btn {
            background: var(--primary-gradient);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: #667eea;
            font-weight: 500;
        }

        .incident-list {
            max-height: 600px;
            overflow-y: auto;
        }

        .incident-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }

        .incident-card:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .incident-card.severity-high {
            border-left-color: #ff4757;
        }

        .incident-card.severity-medium {
            border-left-color: #ffa726;
        }

        .incident-card.severity-low {
            border-left-color: #4caf50;
        }

        .incident-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .incident-type {
            font-weight: 600;
            color: #333;
            font-size: 1.1rem;
        }

        .incident-time {
            color: #666;
            font-size: 0.9rem;
        }

        .incident-location {
            color: #667eea;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .incident-description {
            color: #555;
            margin-bottom: 12px;
            line-height: 1.5;
        }

        .incident-reporter {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 15px;
            font-style: italic;
        }

        .ai-response {
            background: #f8f9ff;
            border-radius: 10px;
            padding: 15px;
            border-left: 3px solid #667eea;
        }

        .ai-label {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }

        .ai-text {
            color: #555;
            line-height: 1.5;
            font-size: 0.95rem;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            opacity: 0.5;
        }

        .alert {
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            font-weight: 500;
            animation: slideDown 0.3s ease-out;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 30px;
            }

            .stats-bar {
                flex-direction: column;
                gap: 15px;
            }

            .stat-card {
                padding: 20px;
            }

            h1 {
                font-size: 2rem;
            }

            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-content">
                <div class="shield-icon">🛡️</div>
                <h1>Campus Safety & Incident Reporting</h1>
                <p>AI-Powered Security System • Real-Time Response • 24/7 Protection</p>
            </div>
        </header>

        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-number" id="totalIncidents">0</div>
                <div class="stat-label">Total Reports</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="todayIncidents">0</div>
                <div class="stat-label">Today's Reports</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">AI</div>
                <div class="stat-label">Powered Analysis</div>
            </div>
        </div>

        <div id="alertContainer"></div>

        <div class="main-content">
            <div class="card">
                <h2>Report an Incident</h2>
                <form id="incidentForm">
                    <div class="form-group">
                        <label for="incidentType">Incident Type *</label>
                        <select id="incidentType" required>
                            <option value="">Select incident type</option>
                            <option value="theft">🔒 Theft</option>
                            <option value="assault">⚠️ Assault</option>
                            <option value="harassment">🚫 Harassment</option>
                            <option value="suspicious_activity">👁️ Suspicious Activity</option>
                            <option value="fire">🔥 Fire Hazard</option>
                            <option value="medical">🏥 Medical Emergency</option>
                            <option value="vandalism">🎨 Vandalism</option>
                            <option value="other">📋 Other</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="location">Location *</label>
                        <input type="text" id="location" placeholder="e.g., Building A, Room 205" required>
                    </div>

                    <div class="form-group">
                        <label for="description">Detailed Description *</label>
                        <textarea id="description" placeholder="Please provide comprehensive information about the incident, including time, people involved, and any other relevant details..." required></textarea>
                    </div>

                    <div class="form-group">
                        <label for="reporterName">Your Name (Optional)</label>
                        <input type="text" id="reporterName" placeholder="Anonymous Reporter">
                    </div>

                    <button type="submit" class="btn" id="submitBtn">
                        Submit Report
                    </button>
                </form>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p class="loading-text">AI is analyzing your report...</p>
                </div>
            </div>

            <div class="card">
                <h2>Recent Incidents<span class="badge-new" id="newBadge" style="display: none;">NEW</span></h2>
                <div class="incident-list" id="incidentList">
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <p>No incidents reported yet</p>
                        <p style="font-size: 0.9rem; margin-top: 10px; opacity: 0.7;">Your safety reports will appear here</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('incidentForm');
        const loading = document.getElementById('loading');
        const submitBtn = document.getElementById('submitBtn');
        const incidentList = document.getElementById('incidentList');
        const alertContainer = document.getElementById('alertContainer');
        const totalIncidentsEl = document.getElementById('totalIncidents');
        const todayIncidentsEl = document.getElementById('todayIncidents');
        const newBadge = document.getElementById('newBadge');

        let lastIncidentCount = 0;

        function showAlert(message, type = 'success') {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alertContainer.appendChild(alert);
            setTimeout(() => {
                alert.style.animation = 'fadeIn 0.3s ease-out reverse';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }

        function getSeverityClass(type) {
            const highSeverity = ['assault', 'fire', 'medical'];
            const mediumSeverity = ['theft', 'harassment', 'suspicious_activity'];
            if (highSeverity.includes(type)) return 'severity-high';
            if (mediumSeverity.includes(type)) return 'severity-medium';
            return 'severity-low';
        }

        function formatIncidentType(type) {
            const icons = {
                'theft': '🔒',
                'assault': '⚠️',
                'harassment': '🚫',
                'suspicious_activity': '👁️',
                'fire': '🔥',
                'medical': '🏥',
                'vandalism': '🎨',
                'other': '📋'
            };
            const formatted = type.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
            return `${icons[type] || '📋'} ${formatted}`;
        }

        function formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (minutes < 1) return 'Just now';
            if (minutes < 60) return `${minutes}m ago`;
            if (hours < 24) return `${hours}h ago`;
            return `${days}d ago`;
        }

        async function submitIncident() {
            const formData = {
                type: document.getElementById('incidentType').value,
                location: document.getElementById('location').value,
                description: document.getElementById('description').value,
                reporter_name: document.getElementById('reporterName').value || 'Anonymous'
            };

            if (!formData.type || !formData.location || !formData.description) {
                showAlert('Please fill in all required fields', 'error');
                return;
            }

            loading.style.display = 'block';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            try {
                const response = await fetch('/api/report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (response.ok) {
                    showAlert('Incident reported successfully! AI analysis complete.', 'success');
                    form.reset();
                    loadIncidents();
                    updateStats();
                } else {
                    showAlert(result.error || 'Failed to submit report', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('Network error. Please try again.', 'error');
            } finally {
                loading.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Report';
            }
        }

        async function loadIncidents() {
            try {
                const response = await fetch('/api/incidents');
                const result = await response.json();

                if (response.ok) {
                    renderIncidents(result.incidents);
                    updateStats();
                }
            } catch (error) {
                console.error('Error loading incidents:', error);
            }
        }

        function renderIncidents(incidents) {
            if (incidents.length === 0) {
                incidentList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <p>No incidents reported yet</p>
                        <p style="font-size: 0.9rem; margin-top: 10px; opacity: 0.7;">Your safety reports will appear here</p>
                    </div>
                `;
                return;
            }

            incidentList.innerHTML = incidents.map(incident => `
                <div class="incident-card ${getSeverityClass(incident.type)}">
                    <div class="incident-header">
                        <span class="incident-type">${formatIncidentType(incident.type)}</span>
                        <span class="incident-time">${formatTime(incident.timestamp)}</span>
                    </div>
                    <div class="incident-location">${incident.location}</div>
                    <div class="incident-description">${incident.description}</div>
                    <div class="incident-reporter">Reported by: ${incident.reporter_name}</div>
                    <div class="ai-response">
                        <div class="ai-label">🤖 AI Safety Recommendation:</div>
                        <div class="ai-text">${incident.ai_response}</div>
                    </div>
                </div>
            `).join('');

            // Show new badge if there are new incidents
            if (incidents.length > lastIncidentCount) {
                newBadge.style.display = 'inline-block';
                setTimeout(() => newBadge.style.display = 'none', 5000);
            }
            lastIncidentCount = incidents.length;
        }

        function updateStats() {
            totalIncidentsEl.textContent = lastIncidentCount;
            const today = new Date().toDateString();
            const todayCount = incidents.filter(i => new Date(i.timestamp).toDateString() === today).length;
            todayIncidentsEl.textContent = todayCount;
        }

        // Event listeners
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            submitIncident();
        });

        // Load incidents on page load
        loadIncidents();

        // Auto-refresh every 30 seconds
        setInterval(loadIncidents, 30000);

        // Animation on load
        window.addEventListener('load', () => {
            document.querySelectorAll('.form-group').forEach((group, index) => {
                group.style.animation = `fadeIn 0.6s ease-out ${index * 0.1}s both`;
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/report', methods=['POST'])
def report_incident():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['type', 'location', 'description']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate AI response using Google Gemini
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""You are an expert campus safety AI assistant. Analyze this incident report and provide professional recommendations:

Incident Type: {data['type']}
Location: {data['location']}
Description: {data['description']}

Provide a concise, professional safety recommendation (3-4 sentences) that includes:
1. Immediate safety actions to take
2. Specific authorities or departments to contact (campus security, medical services, counseling, etc.)
3. Important preventive measures or follow-up steps
4. Any relevant campus resources available

Keep the tone professional, supportive, and actionable. Focus on practical safety guidance."""

            response = model.generate_content(prompt)
            ai_response = response.text
            
        except Exception as e:
            print(f"AI Error: {e}")
            ai_response = "Please contact campus security immediately at ext. 911 for urgent assistance. For non-emergency situations, visit the Campus Safety Office during business hours. Your safety is our top priority, and trained professionals are available 24/7 to assist you."
        
        # Create incident record
        incident = {
            'id': len(incidents) + 1,
            'type': data['type'],
            'location': data['location'],
            'description': data['description'],
            'reporter_name': data.get('reporter_name', 'Anonymous'),
            'timestamp': datetime.now().isoformat(),
            'ai_response': ai_response
        }
        
        incidents.insert(0, incident)
        
        return jsonify({
            'success': True,
            'incident': incident
        }), 201
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    return jsonify({
        'success': True,
        'incidents': incidents
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🛡️  CAMPUS SAFETY & INCIDENT REPORTING SYSTEM".center(70))
    print("="*70)
    print("\n✨ Features:")
    print("   • AI-Powered Safety Recommendations")
    print("   • Real-Time Incident Tracking")
    print("   • Beautiful Responsive UI")
    print("   • Advanced Animations & Transitions")
    print("\n🚀 Server Information:")
    print(f"   • URL: http://127.0.0.1:5000")
    print(f"   • Status: Running")
    print(f"   • Mode: Development")
    print("\n📱 Access the application:")
    print("   • Desktop: Open browser → http://127.0.0.1:5000")
    print("   • Mobile: Connect to same network → http://[YOUR_IP]:5000")
    print("\n⚙️  Configuration:")
    print("   • API: Google Gemini AI")
    print("   • Backend: Flask")
    print("   • Storage: In-Memory")
    print("\n" + "="*70)
    print("Press CTRL+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
