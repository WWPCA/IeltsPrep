# IELTS Speaking Section Assessment Guide

## Assessment User Credentials
- **Username:** assessmentuser
- **Password:** assessmentpassword
- **Status:** Active assessment package (full access to all features)

## How to Use the Speaking Assessment Module

1. **Login**:
   - Go to the login page and enter the assessment user credentials

2. **Access Speaking Module**:
   - Navigate to "Assessments" > "Speaking" from the main navigation menu

3. **Select a Speaking Prompt**:
   - Choose from one of the available prompts (Part 1, 2, or 3)
   - The system will display the prompt details

4. **Record Your Response**:
   - Click the "Start Recording" button
   - Speak for at least 30 seconds to record your response
   - Click "Stop Recording" when finished

5. **Submit Speaking Response**:
   - Click "Submit" to send your recording for processing
   - The system will use transcription services to convert your speech to text
   - After transcription, GenAI assessment will evaluate your response

6. **Review Feedback**:
   - The system will display your band scores across the IELTS criteria
   - Check that feedback appears for Fluency and Coherence, Lexical Resource, 
     Grammatical Range and Accuracy, and Pronunciation

## Common API Integrations

- **Transcription Services**: Converting audio to text (check logs for any transcription errors)
- **Cloud Storage**: Storing audio files (verify file uploads work correctly)
- **Text-to-Speech** (optional): For feedback delivery

## Troubleshooting

If you encounter issues:

1. **Check Browser Console**: Look for any JavaScript errors
2. **Verify API Credentials**: Ensure API credentials are configured correctly
3. **Check Network Tab**: Monitor API calls to services
4. **Server Logs**: Review server logs for backend errors

## Expected Results

- Audio recording should work in supported browsers
- Transcription should process correctly (may take 10-30 seconds)
- Assessment should provide meaningful feedback on speaking performance
- Band scores should appear for all IELTS criteria