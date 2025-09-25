// TrueScore® Writing Assessment Component
import React, { useState, useEffect } from 'react';
import { NovaAI } from '../../services/NovaAI';

export const TrueScore = ({ assessmentData, onComplete }) => {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const analyzeWriting = async (text) => {
        setLoading(true);
        try {
            const result = await NovaAI.analyzeTrueScore(text);
            setAnalysis(result);
            onComplete(result);
        } catch (error) {
            console.error('TrueScore analysis failed:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="truescore-component">
            <h3>TrueScore® Writing Assessment</h3>
            {loading && <div className="loading">Analyzing your writing...</div>}
            {analysis && (
                <div className="analysis-results">
                    <div className="band-score">Band Score: {analysis.overallBand}</div>
                    <div className="criteria-breakdown">
                        {/* Render detailed feedback */}
                    </div>
                </div>
            )}
        </div>
    );
};
