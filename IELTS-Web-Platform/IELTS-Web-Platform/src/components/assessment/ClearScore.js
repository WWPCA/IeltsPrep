// ClearScore® Speaking Assessment Component
import React, { useState, useRef } from 'react';
import { NovaAI } from '../../services/NovaAI';

export const ClearScore = ({ assessmentData, onComplete }) => {
    const [recording, setRecording] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const mediaRecorderRef = useRef(null);
    
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            setRecording(true);
            
            mediaRecorderRef.current.ondataavailable = async (event) => {
                const audioBlob = event.data;
                await analyzeSpeaking(audioBlob);
            };
            
            mediaRecorderRef.current.start();
        } catch (error) {
            console.error('Recording failed:', error);
        }
    };
    
    const analyzeSpeaking = async (audioBlob) => {
        try {
            const result = await NovaAI.analyzeClearScore(audioBlob);
            setAnalysis(result);
            onComplete(result);
        } catch (error) {
            console.error('ClearScore analysis failed:', error);
        }
    };
    
    return (
        <div className="clearscore-component">
            <h3>ClearScore® Speaking Assessment</h3>
            <button onClick={startRecording} disabled={recording}>
                {recording ? 'Recording...' : 'Start Speaking Assessment'}
            </button>
            {analysis && (
                <div className="speaking-results">
                    <div className="band-score">Band Score: {analysis.overallBand}</div>
                    <div className="pronunciation-feedback">
                        {/* Render pronunciation analysis */}
                    </div>
                </div>
            )}
        </div>
    );
};
