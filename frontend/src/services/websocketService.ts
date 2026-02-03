/**
 * WebSocket service for real-time AI matching theater
 */
import { WebSocketEvent, WebSocketEventType } from '../types/matching';

export class WebSocketService {
    private socket: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 1000;
    private eventHandlers: Map<WebSocketEventType, Set<(data: any) => void>> = new Map();
    private isConnecting = false;

    constructor(private baseUrl: string = 'ws://localhost:8000') { }

    /**
     * Connect to a specific AI matching session
     */
    async connectToSession(sessionId: string, token: string): Promise<boolean> {
        if (this.isConnecting) {
            return false;
        }

        this.isConnecting = true;

        try {
            // Disconnect existing connection
            if (this.socket) {
                this.disconnect();
            }

            // Create new WebSocket connection using native WebSocket (not Socket.IO)
            const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws/session/${sessionId}?token=${encodeURIComponent(token)}`;

            return new Promise((resolve, reject) => {
                const ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    console.log(`Connected to session ${sessionId}`);
                    this.isConnecting = false;
                    this.reconnectAttempts = 0;
                    resolve(true);
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                };

                ws.onclose = (event) => {
                    console.log('WebSocket connection closed:', event.code, event.reason);
                    
                    // If the socket in the class is not this socket, it means we've already disconnected
                    // or reconnected, so we shouldn't attempt to reconnect for this closed socket.
                    if (this.socket !== ws) {
                        return;
                    }
                    
                    this.isConnecting = false;

                    // Attempt reconnection if not intentional
                    if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.attemptReconnection(sessionId, token);
                    }
                };

                ws.onerror = (error) => {
                    // Ignore errors for stale sockets (e.g. cancelled by strict mode unmount)
                    if (this.socket !== ws) {
                        return;
                    }
                    console.error('WebSocket error:', error);
                    this.isConnecting = false;
                    reject(error);
                };

                // Store the WebSocket connection
                this.socket = ws as any; // Type assertion for compatibility
            });

        } catch (error) {
            this.isConnecting = false;
            console.error('Failed to connect to WebSocket:', error);
            return false;
        }
    }

    /**
     * Connect to user notifications
     */
    async connectToNotifications(userId: string, token: string): Promise<boolean> {
        try {
            const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws/notifications/${userId}?token=${encodeURIComponent(token)}`;

            return new Promise((resolve, reject) => {
                const ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    console.log(`Connected to notifications for user ${userId}`);
                    resolve(true);
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Error parsing notification message:', error);
                    }
                };

                ws.onclose = () => {
                    console.log('Notifications WebSocket closed');
                };

                ws.onerror = (error) => {
                    console.error('Notifications WebSocket error:', error);
                    reject(error);
                };

                this.socket = ws as any;
            });

        } catch (error) {
            console.error('Failed to connect to notifications:', error);
            return false;
        }
    }

    /**
     * Disconnect from WebSocket
     */
    disconnect(): void {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        // Do not clear event handlers automatically to allow for reconnection
        // Components should manage their own listeners using off()
        this.reconnectAttempts = 0;
        this.isConnecting = false;
    }

    /**
     * Send a message through WebSocket
     */
    send(message: any): void {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected, cannot send message:', message);
        }
    }

    /**
     * Send user feedback
     */
    sendFeedback(feedback: any): void {
        this.send({
            type: 'user_feedback',
            feedback,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Send user reaction
     */
    sendReaction(messageId: string, reactionType: string): void {
        this.send({
            type: 'reaction',
            reaction: {
                message_id: messageId,
                type: reactionType
            },
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Send guidance to AI avatar
     */
    sendGuidance(avatarId: string, instruction: string): void {
        this.send({
            type: 'user_guidance',
            guidance: {
                avatar_id: avatarId,
                instruction
            },
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Request compatibility update
     */
    requestCompatibilityUpdate(): void {
        this.send({
            type: 'request_compatibility_update',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Start AI conversation
     */
    startConversation(): void {
        this.send({
            type: 'start_conversation',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Send ping to keep connection alive
     */
    ping(): void {
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Add event listener
     */
    on(eventType: WebSocketEventType, handler: (data: any) => void): void {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, new Set());
        }
        this.eventHandlers.get(eventType)!.add(handler);
    }

    /**
     * Remove event listener
     */
    off(eventType: WebSocketEventType, handler: (data: any) => void): void {
        const handlers = this.eventHandlers.get(eventType);
        if (handlers) {
            handlers.delete(handler);
        }
    }

    /**
     * Check if connected
     */
    isConnected(): boolean {
        return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
    }

    /**
     * Get connection state
     */
    getConnectionState(): string {
        if (!this.socket) return 'disconnected';

        switch (this.socket.readyState) {
            case WebSocket.CONNECTING: return 'connecting';
            case WebSocket.OPEN: return 'connected';
            case WebSocket.CLOSING: return 'closing';
            case WebSocket.CLOSED: return 'closed';
            default: return 'unknown';
        }
    }

    /**
     * Handle incoming WebSocket messages
     */
    private handleMessage(data: WebSocketEvent): void {
        const handlers = this.eventHandlers.get(data.type as WebSocketEventType);
        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in WebSocket event handler for ${data.type}:`, error);
                }
            });
        }
    }

    /**
     * Attempt to reconnect
     */
    private async attemptReconnection(sessionId: string, token: string): Promise<void> {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);

        setTimeout(async () => {
            try {
                await this.connectToSession(sessionId, token);
            } catch (error) {
                console.error('Reconnection failed:', error);
            }
        }, delay);
    }

    /**
     * Start periodic ping to keep connection alive
     */
    startHeartbeat(interval: number = 30000): void {
        setInterval(() => {
            if (this.isConnected()) {
                this.ping();
            }
        }, interval);
    }
}

// Global WebSocket service instance
export const websocketService = new WebSocketService();

// Utility functions
export const connectToMatchingSession = async (sessionId: string, token: string): Promise<boolean> => {
    return await websocketService.connectToSession(sessionId, token);
};

export const connectToNotifications = async (userId: string, token: string): Promise<boolean> => {
    return await websocketService.connectToNotifications(userId, token);
};

export const disconnectWebSocket = (): void => {
    websocketService.disconnect();
};

export default websocketService;