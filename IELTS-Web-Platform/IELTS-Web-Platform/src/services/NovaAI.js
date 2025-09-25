// Nova AI Service Integration
export class NovaAI {
    static async analyzeTrueScore(writingText) {
        const response = await fetch('/api/nova-micro/writing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                writing_text: writingText,
                assessment_type: 'academic_writing'
            })
        });
        
        if (!response.ok) {
            throw new Error('TrueScore analysis failed');
        }
        
        return await response.json();
    }
    
    static async analyzeClearScore(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);
        
        const response = await fetch('/api/nova-sonic-stream', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('ClearScore analysis failed');
        }
        
        return await response.json();
    }
    
    static async getMayaResponse(userText) {
        const response = await fetch('/api/maya/conversation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_text: userText })
        });
        
        return await response.json();
    }
}
