/**
 * WebSocket Test Page - Simple page to test WebSocket connection
 */
import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Paper,
    Typography,
    Button,
    TextField,
    Alert,
    List,
    ListItem,
    ListItemText,
    Chip
} from '@mui/material';
import { websocketService } from '../services/websocketService';

const WebSocketTestPage: React.FC = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [connectionState, setConnectionState] = useState('disconnected');
    const [messages, setMessages] = useState<any[]>([]);
    const [sessionId, setSessionId] = useState('test-session-123');
    const [token, setToken] = useState(localStorage.getItem('token') || '');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Set up event listeners
        websocketService.on('connection_established', (data) => {
            console.log('Connection established:', data);
            setMessages(prev => [...prev, { type: 'connection_established', data, timestamp: new Date() }]);
            setIsConnected(true);
            setError(null);
        });

        websocketService.on('error', (data) => {
            console.log('WebSocket error:', data);
            setMessages(prev => [...prev, { type: 'error', data, timestamp: new Date() }]);
            setError(data.message || 'WebSocket error');
        });

        websocketService.on('ai_message', (data) => {
            console.log('AI message:', data);
            setMessages(prev => [...prev, { type: 'ai_message', data, timestamp: new Date() }]);
        });

        websocketService.on('compatibility_update', (data) => {
            console.log('Compatibility update:', data);
            setMessages(prev => [...prev, { type: 'compatibility_update', data, timestamp: new Date() }]);
        });

        // Monitor connection state
        const interval = setInterval(() => {
            const state = websocketService.getConnectionState();
            setConnectionState(state);
            setIsConnected(state === 'connected');
        }, 1000);

        return () => {
            clearInterval(interval);
            websocketService.disconnect();
        };
    }, []);

    const handleConnect = async () => {
        setError(null);
        setMessages([]);

        try {
            const success = await websocketService.connectToSession(sessionId, token);
            if (!success) {
                setError('Failed to connect to WebSocket');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Connection failed');
        }
    };

    const handleDisconnect = () => {
        websocketService.disconnect();
        setIsConnected(false);
        setMessages([]);
    };

    const handleStartConversation = () => {
        websocketService.startConversation();
    };

    const handleRequestUpdate = () => {
        websocketService.requestCompatibilityUpdate();
    };

    const handleSendMessage = () => {
        websocketService.send({
            type: 'test_message',
            content: 'Hello from test page',
            timestamp: new Date().toISOString()
        });
    };

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                WebSocket Connection Test
            </Typography>

            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Connection Settings
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <TextField
                        label="Session ID"
                        value={sessionId}
                        onChange={(e) => setSessionId(e.target.value)}
                        size="small"
                        sx={{ flex: 1 }}
                    />
                    <TextField
                        label="Auth Token"
                        value={token}
                        onChange={(e) => setToken(e.target.value)}
                        size="small"
                        sx={{ flex: 1 }}
                    />
                </Box>

                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                    <Button
                        variant="contained"
                        onClick={handleConnect}
                        disabled={isConnected}
                    >
                        Connect
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={handleDisconnect}
                        disabled={!isConnected}
                    >
                        Disconnect
                    </Button>
                    <Chip
                        label={`Status: ${connectionState}`}
                        color={isConnected ? 'success' : 'default'}
                    />
                </Box>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}
            </Paper>

            {isConnected && (
                <Paper sx={{ p: 3, mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Test Actions
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                            variant="contained"
                            onClick={handleStartConversation}
                            color="primary"
                        >
                            Start Conversation
                        </Button>
                        <Button
                            variant="contained"
                            onClick={handleRequestUpdate}
                            color="secondary"
                        >
                            Request Update
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={handleSendMessage}
                        >
                            Send Test Message
                        </Button>
                    </Box>
                </Paper>
            )}

            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Messages ({messages.length})
                </Typography>

                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                    {messages.map((message, index) => (
                        <ListItem key={index} divider>
                            <ListItemText
                                primary={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <Chip
                                            label={message.type}
                                            size="small"
                                            color={message.type === 'error' ? 'error' : 'primary'}
                                        />
                                        <Typography variant="caption">
                                            {message.timestamp.toLocaleTimeString()}
                                        </Typography>
                                    </Box>
                                }
                                secondary={
                                    <pre style={{ fontSize: '0.8rem', margin: 0, whiteSpace: 'pre-wrap' }}>
                                        {JSON.stringify(message.data, null, 2)}
                                    </pre>
                                }
                            />
                        </ListItem>
                    ))}
                    {messages.length === 0 && (
                        <ListItem>
                            <ListItemText
                                primary="No messages yet"
                                secondary="Connect to the WebSocket to see messages"
                            />
                        </ListItem>
                    )}
                </List>
            </Paper>
        </Container>
    );
};

export default WebSocketTestPage;