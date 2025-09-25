// Email Service Integration
export class EmailService {
    static async sendWelcomeEmail(email, name = '') {
        try {
            const response = await fetch('/api/send-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'welcome',
                    email: email,
                    name: name
                })
            });
            
            return response.ok;
        } catch (error) {
            console.error('Email service error:', error);
            return false;
        }
    }
    
    static async sendAssessmentComplete(email, assessmentType, results) {
        try {
            const response = await fetch('/api/send-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'assessment_complete',
                    email: email,
                    assessment_type: assessmentType,
                    results: results
                })
            });
            
            return response.ok;
        } catch (error) {
            console.error('Assessment email error:', error);
            return false;
        }
    }
}
