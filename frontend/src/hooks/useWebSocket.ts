/**
 * Custom hook for managing WebSocket connections in the AI matching theater
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { websocketService } from '../services/websocketService';
import { WebSocketEventType, WebSocketEvent } from '../types/matching';

interface UseWebSocketOptions {
    sessionId?: string;
    userId?: string;
    token?: string;
    autoConnect?: boolean;
    reconnectAttempts?: number;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    connectionState: string;
    error: string | null;
    connect: (sessionId: string, token: string) => Promise<boolean>;
    connectToNotifications: (userId: string, token: string) => Promise<boolean>;
    disconnect: () => void;
    send: (message: any) => void;
    on: (eventType: WebSocketEventType, handler: (data: any) => void) => void;
    off: (eventType: WebSocketEventType, handler: (data: any) => void) => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
    const [isConnected, setIsConnected] = useState(false);
    const [connectionState, setConnectionState] = useState('disconnected');
    const [error, setError] = useState<string | null>(null);

    const eventHandlersRef = useRef<Map<WebSocketEventType, Set<(data: any) => void>>>(new Map());
    const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);

    // Monitor connection state
    useEffect(() => {
        const checkConnectionState = () => {
            const state = websocketService.getConnectionState();
            setConnectionState(state);
            setIsConnected(state === 'connected');
        };

        const interval = setInterval(checkConnectionState, 1000);
        return () => clearInterval(interval);
    }, []);

    // Auto-connect if options provided
    useEffect(() => {
        if (options.autoConnect && options.sessionId && options.token) {
            connect(options.sessionId, options.token);
        }
    }, [options.autoConnect, options.sessionId, options.token]);

    // Setup event handlers
    useEffect(() => {
        // Connection events
        const handleConnectionEstablished = (data: WebSocketEvent) => {
            setIsConnected(true);
            setError(null);
            startHeartbeat();

            // Notify handlers
            const handlers = eventHandlersRef.current.get('connection_established');
            if (handlers) {
                handlers.forEach(handler => handler(data));
            }
        };

        const handleError = (data: WebSocketEvent) => {
            setError(data.message || 'WebSocket error occurred');

            // Notify handlers
            const handlers = eventHandlersRef.current.get('error');
            if (handlers) {
                handlers.forEach(handler => handler(data));
            }
        };

        // Register internal handlers
        websocketService.on('connection_established', handleConnectionEstablished);
        websocketService.on('error', handleError);

        return () => {
            websocketService.off('connection_established', handleConnectionEstablished);
            websocketService.off('error', handleError);
            stopHeartbeat();
        };
    }, []);

    const connect = useCallback(async (sessionId: string, token: string): Promise<boolean> => {
        try {
            setError(null);
            const success = await websocketService.connectToSession(sessionId, token);

            if (success) {
                setIsConnected(true);
                startHeartbeat();
            } else {
                setError('Failed to connect to session');
            }

            return success;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Connection failed';
            setError(errorMessage);
            return false;
        }
    }, []);

    const connectToNotifications = useCallback(async (userId: string, token: string): Promise<boolean> => {
        try {
            setError(null);
            const success = await websocketService.connectToNotifications(userId, token);

            if (success) {
                setIsConnected(true);
                startHeartbeat();
            } else {
                setError('Failed to connect to notifications');
            }

            return success;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Connection failed';
            setError(errorMessage);
            return false;
        }
    }, []);

    const disconnect = useCallback(() => {
        websocketService.disconnect();
        setIsConnected(false);
        setError(null);
        stopHeartbeat();
    }, []);

    const send = useCallback((message: any) => {
        if (isConnected) {
            websocketService.send(message);
        } else {
            console.warn('Cannot send message: WebSocket not connected');
        }
    }, [isConnected]);

    const on = useCallback((eventType: WebSocketEventType, handler: (data: any) => void) => {
        // Store handler reference
        if (!eventHandlersRef.current.has(eventType)) {
            eventHandlersRef.current.set(eventType, new Set());
        }
        eventHandlersRef.current.get(eventType)!.add(handler);

        // Register with WebSocket service
        websocketService.on(eventType, handler);
    }, []);

    const off = useCallback((eventType: WebSocketEventType, handler: (data: any) => void) => {
        // Remove handler reference
        const handlers = eventHandlersRef.current.get(eventType);
        if (handlers) {
            handlers.delete(handler);
        }

        // Unregister from WebSocket service
        websocketService.off(eventType, handler);
    }, []);

    const startHeartbeat = useCallback(() => {
        if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
        }

        heartbeatIntervalRef.current = setInterval(() => {
            if (websocketService.isConnected()) {
                websocketService.ping();
            }
        }, 30000); // Ping every 30 seconds
    }, []);

    const stopHeartbeat = useCallback(() => {
        if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
            heartbeatIntervalRef.current = null;
        }
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            disconnect();
            stopHeartbeat();
        };
    }, [disconnect, stopHeartbeat]);

    return {
        isConnected,
        connectionState,
        error,
        connect,
        connectToNotifications,
        disconnect,
        send,
        on,
        off
    };
};

export default useWebSocket;