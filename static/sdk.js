/**
 * arifOS WebMCP Client SDK
 * Handles real-time vitals and cross-protocol 888_HOLD state.
 */
export class WebMCPSDK {
    constructor(config = {}) {
        this.baseUrl = config.baseUrl || window.location.origin;
        this.wsUrl = config.wsUrl || this.baseUrl.replace(/^http/, 'ws') + '/webmcp/ws';
        this.actorId = config.actorId || 'ariffazil';
        
        this.socket = null;
        this.listeners = {
            'vitals': [],
            '888_HOLD': [],
            'connected': [],
            'disconnected': []
        };
        
        this.reconnectAttempts = 0;
        this.maxReconnects = 10;
    }

    /**
     * Connect to the WebMCP WebSocket gateway
     */
    connect() {
        console.log(`[WebMCP] Connecting to ${this.wsUrl}...`);
        this.socket = new WebSocket(this.wsUrl);

        this.socket.onopen = () => {
            console.log('[WebMCP] Connected to Sovereign Gateway');
            this.reconnectAttempts = 0;
            this.emit('connected', { timestamp: Date.now() });
        };

        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.emit(message.type, message);
            } catch (err) {
                console.error('[WebMCP] Failed to parse message:', err);
            }
        };

        this.socket.onclose = () => {
            console.warn('[WebMCP] Disconnected from Gateway');
            this.emit('disconnected', { timestamp: Date.now() });
            this.handleReconnect();
        };

        this.socket.onerror = (err) => {
            console.error('[WebMCP] WebSocket error:', err);
        };
    }

    /**
     * Handle backoff reconnection
     */
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnects) {
            const timeout = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            this.reconnectAttempts++;
            console.log(`[WebMCP] Reconnecting in ${timeout}ms... (Attempt ${this.reconnectAttempts})`);
            setTimeout(() => this.connect(), timeout);
        } else {
            console.error('[WebMCP] Maximum reconnection attempts reached.');
        }
    }

    /**
     * Register a listener for an event type.
     */
    on(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
        }
        this.listeners[eventType].push(callback);
    }

    /**
     * Trigger registered listeners for an event.
     */
    emit(eventType, data) {
        if (this.listeners[eventType]) {
            this.listeners[eventType].forEach(cb => cb(data));
        } else {
            console.warn(`[WebMCP] Unhandled event type: ${eventType}`, data);
        }
    }

    /**
     * F13 Sovereign Action: Resolve an 888_HOLD state
     */
    async resolveHold(holdId, decision, justification = "") {
        console.log(`[WebMCP] Resolving HOLD ${holdId} with verdict ${decision}`);
        
        try {
            const response = await fetch(`${this.baseUrl}/hold/${holdId}/resolve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    actor_id: this.actorId,
                    decision: decision, // 'APPROVED' or 'DENIED'
                    justification: justification
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error(`[WebMCP] Failed to resolve HOLD ${holdId}:`, error);
            throw error;
        }
    }
}
