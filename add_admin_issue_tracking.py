"""
Add CSRF and Maya Conversation Issue Tracking to Admin Dashboard
This script enhances the admin dashboard with comprehensive issue tracking
"""

from main import app
from api_issues import APIIssueLog
from models import User

def create_admin_issue_dashboard():
    """Create comprehensive admin dashboard for tracking CSRF and Maya issues"""
    
    # Create admin template for enhanced issue tracking
    admin_template = """
{% extends "admin/base.html" %}

{% block title %}System Issues Dashboard{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>System Issues Dashboard</h1>
                <div class="btn-group">
                    <a href="{{ url_for('admin_dashboard') }}" class="btn btn-outline-secondary">Back to Admin</a>
                </div>
            </div>
        </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card text-white bg-danger">
                <div class="card-header">CSRF Issues</div>
                <div class="card-body">
                    <h4 class="card-title">{{ csrf_issues }}</h4>
                    <p class="card-text">Security token validation failures</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-white bg-warning">
                <div class="card-header">Maya Conversation</div>
                <div class="card-body">
                    <h4 class="card-title">{{ maya_issues }}</h4>
                    <p class="card-text">Conversation system issues</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-white bg-info">
                <div class="card-header">Total Issues</div>
                <div class="card-body">
                    <h4 class="card-title">{{ total_issues }}</h4>
                    <p class="card-text">All system issues logged</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-white bg-secondary">
                <div class="card-header">Unresolved</div>
                <div class="card-body">
                    <h4 class="card-title">{{ unresolved_issues }}</h4>
                    <p class="card-text">Requiring attention</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
        <div class="card-header">Filters</div>
        <div class="card-body">
            <form method="GET" action="{{ url_for('system_issues') }}">
                <div class="row">
                    <div class="col-md-3">
                        <select name="api_name" class="form-select">
                            <option value="">All Issue Types</option>
                            <option value="csrf_validation" {{ 'selected' if api_filter == 'csrf_validation' }}>CSRF Validation</option>
                            <option value="maya_conversation" {{ 'selected' if api_filter == 'maya_conversation' }}>Maya Conversation</option>
                            <option value="aws_bedrock" {{ 'selected' if api_filter == 'aws_bedrock' }}>AWS Bedrock</option>
                            <option value="openai" {{ 'selected' if api_filter == 'openai' }}>OpenAI</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select name="country" class="form-select">
                            <option value="">All Countries</option>
                            {% for country in countries %}
                            <option value="{{ country }}" {{ 'selected' if country_filter == country }}>{{ country }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select name="resolved" class="form-select">
                            <option value="">All Status</option>
                            <option value="false" {{ 'selected' if resolved_filter == 'false' }}>Unresolved</option>
                            <option value="true" {{ 'selected' if resolved_filter == 'true' }}>Resolved</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary">Apply Filters</button>
                        <a href="{{ url_for('system_issues') }}" class="btn btn-outline-secondary">Clear</a>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- High Frequency Issues Alert -->
    {% if frequent_issues %}
    <div class="alert alert-warning">
        <h5><i class="fas fa-exclamation-triangle"></i> High Frequency Issues</h5>
        <p>The following issues have occurred multiple times and require immediate attention:</p>
        <ul>
        {% for issue in frequent_issues %}
            <li><strong>{{ issue.api_name }}</strong> ({{ issue.endpoint }}): {{ issue.attempt_count }} attempts - {{ issue.error_message[:100] }}...</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}

    <!-- Issues Table -->
    <div class="card">
        <div class="card-header">
            <h5>System Issues ({{ issues.total }} total)</h5>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Date/Time</th>
                            <th>Issue Type</th>
                            <th>Endpoint</th>
                            <th>User</th>
                            <th>Country</th>
                            <th>Attempts</th>
                            <th>Error</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for issue in issues.items %}
                        <tr class="{{ 'table-danger' if not issue.resolved else 'table-success' }}">
                            <td>{{ issue.occurred_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td>
                                <span class="badge bg-{{ 'danger' if issue.api_name == 'csrf_validation' else 'warning' if issue.api_name == 'maya_conversation' else 'info' }}">
                                    {{ issue.api_name.replace('_', ' ').title() }}
                                </span>
                            </td>
                            <td><code>{{ issue.endpoint }}</code></td>
                            <td>
                                {% if issue.user %}
                                    <a href="{{ url_for('user_profile', user_id=issue.user.id) }}">{{ issue.user.email }}</a>
                                {% else %}
                                    <span class="text-muted">Anonymous</span>
                                {% endif %}
                            </td>
                            <td>{{ issue.country or 'Unknown' }}</td>
                            <td>
                                <span class="badge bg-{{ 'danger' if issue.attempt_count > 5 else 'warning' if issue.attempt_count > 2 else 'secondary' }}">
                                    {{ issue.attempt_count }}
                                </span>
                            </td>
                            <td>{{ issue.error_message[:50] }}{% if issue.error_message|length > 50 %}...{% endif %}</td>
                            <td>
                                {% if issue.resolved %}
                                    <span class="badge bg-success">Resolved</span>
                                {% else %}
                                    <span class="badge bg-danger">Open</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if not issue.resolved %}
                                <form method="POST" action="{{ url_for('mark_issue_resolved', issue_id=issue.id) }}" style="display: inline;">
                                    <button type="submit" class="btn btn-sm btn-success">Mark Resolved</button>
                                </form>
                                {% endif %}
                                <button class="btn btn-sm btn-info" onclick="showIssueDetails({{ issue.id }})">Details</button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    Showing {{ issues.per_page * (issues.page - 1) + 1 }} to {{ issues.per_page * issues.page if issues.per_page * issues.page < issues.total else issues.total }} of {{ issues.total }} issues
                </div>
                <nav>
                    <ul class="pagination">
                        {% if issues.has_prev %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('system_issues', page=issues.prev_num, api_name=api_filter, country=country_filter, resolved=resolved_filter) }}">Previous</a>
                        </li>
                        {% endif %}
                        
                        {% for page_num in issues.iter_pages() %}
                            {% if page_num %}
                                {% if page_num != issues.page %}
                                <li class="page-item">
                                    <a class="page-link" href="{{ url_for('system_issues', page=page_num, api_name=api_filter, country=country_filter, resolved=resolved_filter) }}">{{ page_num }}</a>
                                </li>
                                {% else %}
                                <li class="page-item active">
                                    <span class="page-link">{{ page_num }}</span>
                                </li>
                                {% endif %}
                            {% else %}
                            <li class="page-item disabled">
                                <span class="page-link">...</span>
                            </li>
                            {% endif %}
                        {% endfor %}
                        
                        {% if issues.has_next %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('system_issues', page=issues.next_num, api_name=api_filter, country=country_filter, resolved=resolved_filter) }}">Next</a>
                        </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        </div>
    </div>
</div>

<script>
function showIssueDetails(issueId) {
    // You can implement a modal or detailed view here
    alert('Issue details functionality would be implemented here for issue ID: ' + issueId);
}
</script>
{% endblock %}
"""
    
    # Write the admin template
    import os
    os.makedirs('templates/admin', exist_ok=True)
    
    with open('templates/admin/system_issues.html', 'w') as f:
        f.write(admin_template)
    
    print("✅ Created admin system issues template")

def add_admin_routes():
    """Add admin routes for system issue tracking"""
    
    admin_routes_addition = '''

@app.route('/admin/system_issues')
@admin_required
def system_issues():
    """Comprehensive system issues dashboard including CSRF and Maya conversation issues."""
    try:
        from sqlalchemy import func
        
        # Get pagination and filters
        page = request.args.get('page', 1, type=int)
        per_page = 20
        api_filter = request.args.get('api_name', '')
        country_filter = request.args.get('country', '')
        resolved_filter = request.args.get('resolved', '')
        
        # Build query with filters
        query = APIIssueLog.query
        
        if api_filter:
            query = query.filter(APIIssueLog.api_name == api_filter)
        if country_filter:
            query = query.filter(APIIssueLog.country == country_filter)
        if resolved_filter:
            query = query.filter(APIIssueLog.resolved == (resolved_filter == 'true'))
        
        issues = query.order_by(APIIssueLog.occurred_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get comprehensive statistics
        total_issues = APIIssueLog.query.count()
        unresolved_issues = APIIssueLog.query.filter_by(resolved=False).count()
        csrf_issues = APIIssueLog.query.filter_by(api_name='csrf_validation', resolved=False).count()
        maya_issues = APIIssueLog.query.filter_by(api_name='maya_conversation', resolved=False).count()
        
        # Get unique countries for filter dropdown
        countries = db.session.query(APIIssueLog.country).filter(
            APIIssueLog.country.isnot(None)
        ).distinct().order_by(APIIssueLog.country).all()
        countries = [c[0] for c in countries if c[0]]
        
        # Get high-frequency issues (more than 3 attempts, unresolved)
        frequent_issues = APIIssueLog.query.filter(
            APIIssueLog.attempt_count > 3,
            APIIssueLog.resolved == False
        ).order_by(APIIssueLog.attempt_count.desc()).limit(5).all()
        
        return render_template('admin/system_issues.html',
                             issues=issues,
                             total_issues=total_issues,
                             unresolved_issues=unresolved_issues,
                             csrf_issues=csrf_issues,
                             maya_issues=maya_issues,
                             countries=countries,
                             frequent_issues=frequent_issues,
                             api_filter=api_filter,
                             country_filter=country_filter,
                             resolved_filter=resolved_filter)
                             
    except Exception as e:
        flash(f'Error loading system issues: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/mark_issue_resolved/<int:issue_id>', methods=['POST'])
@admin_required
def mark_issue_resolved(issue_id):
    """Mark a system issue as resolved."""
    try:
        issue = APIIssueLog.query.get_or_404(issue_id)
        issue.resolved = True
        issue.resolved_at = datetime.utcnow()
        issue.resolution_notes = f"Marked resolved by admin user at {datetime.utcnow()}"
        
        db.session.commit()
        flash(f'Issue #{issue_id} marked as resolved', 'success')
        
    except Exception as e:
        flash(f'Error resolving issue: {str(e)}', 'error')
    
    return redirect(url_for('system_issues'))
'''
    
    # Add to admin_routes.py
    with open('admin_routes.py', 'a') as f:
        f.write(admin_routes_addition)
    
    print("✅ Added system issues routes to admin dashboard")

def update_database_schema():
    """Update database to include the new attempt_count column"""
    
    try:
        with app.app_context():
            # Check if attempt_count column exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('api_issue_log')]
            
            if 'attempt_count' not in columns:
                # Add the column
                db.session.execute('ALTER TABLE api_issue_log ADD COLUMN attempt_count INTEGER DEFAULT 1')
                db.session.commit()
                print("✅ Added attempt_count column to api_issue_log table")
            else:
                print("✅ attempt_count column already exists")
                
    except Exception as e:
        print(f"Error updating database schema: {e}")

if __name__ == "__main__":
    print("Setting up admin issue tracking dashboard...")
    create_admin_issue_dashboard()
    add_admin_routes()
    update_database_schema()
    print("\\n✅ Admin issue tracking dashboard setup complete!")
    print("\\nFeatures added:")
    print("- CSRF validation error tracking")
    print("- Maya conversation issue monitoring") 
    print("- User, country, and attempt count tracking")
    print("- High-frequency issue alerts")
    print("- Comprehensive filtering and pagination")
    print("- Admin resolution workflow")