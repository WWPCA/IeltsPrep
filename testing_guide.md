# IELTS Speaking Section Testing Guide

## Test User Credentials
- **Username:** testuser
- **Password:** testpassword
- **Status:** Premium (full access to all features)

## How to Test the Speaking Module

1. **Login**:
   - Go to the login page and enter the test user credentials

2. **Access Speaking Module**:
   - Navigate to "Practice" > "Speaking" from the main navigation menu

3. **Select a Speaking Prompt**:
   - Choose from one of the available prompts (Part 1, 2, or 3)
   - The system will display the prompt details

4. **Test Audio Recording**:
   - Click the "Start Recording" button
   - Speak for at least 30 seconds to test the recording functionality
   - Click "Stop Recording" when finished

5. **Submit Speaking Response**:
   - Click "Submit" to send your recording to AWS for processing
   - The system will use AWS Transcribe to convert your speech to text
   - After transcription, AWS analysis will evaluate your response

6. **Review Feedback**:
   - The system should display your band scores across the IELTS criteria
   - Check that feedback appears for Fluency and Coherence, Lexical Resource, 
     Grammatical Range and Accuracy, and Pronunciation

## Common AWS API Checks

- **AWS Transcribe**: Converting audio to text (check logs for any transcription errors)
- **AWS S3**: Storing audio files (verify file uploads work correctly)
- **AWS Polly** (optional): Text-to-speech for feedback

## Troubleshooting

If you encounter issues:

1. **Check Browser Console**: Look for any JavaScript errors
2. **Verify AWS Credentials**: Ensure AWS credentials are configured correctly
3. **Check Network Tab**: Monitor API calls to AWS services
4. **Server Logs**: Review server logs for backend errors

## Expected Results

- Audio recording should work in supported browsers
- Transcription should process correctly (may take 10-30 seconds)
- Analysis should provide meaningful feedback on speaking performance
- Band scores should appear for all IELTS criteria