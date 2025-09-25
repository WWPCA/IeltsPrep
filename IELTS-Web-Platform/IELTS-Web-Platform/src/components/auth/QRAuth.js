// QR Code Authentication Component
import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { AuthService } from '../../services/AuthService';

export const QRAuth = ({ onAuthSuccess }) => {
    const [qrData, setQrData] = useState(null);
    const [authStatus, setAuthStatus] = useState('pending');
    
    useEffect(() => {
        generateQRCode();
        const interval = setInterval(checkAuthStatus, 2000);
        return () => clearInterval(interval);
    }, []);
    
    const generateQRCode = async () => {
        try {
            const qrCode = await AuthService.generateQRCode();
            setQrData(qrCode);
        } catch (error) {
            console.error('QR generation failed:', error);
        }
    };
    
    const checkAuthStatus = async () => {
        if (!qrData) return;
        
        try {
            const status = await AuthService.checkQRStatus(qrData.sessionId);
            if (status.authenticated) {
                setAuthStatus('success');
                onAuthSuccess(status.user);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
        }
    };
    
    return (
        <div className="qr-auth-component">
            <h3>Mobile App Authentication</h3>
            {qrData && (
                <div className="qr-code-container">
                    <QRCodeSVG value={qrData.qrString} size={200} />
                    <p>Scan with your IELTS GenAI Prep mobile app</p>
                </div>
            )}
            <div className={`auth-status ${authStatus}`}>
                {authStatus === 'pending' && 'Waiting for mobile app scan...'}
                {authStatus === 'success' && 'Authentication successful!'}
            </div>
        </div>
    );
};
