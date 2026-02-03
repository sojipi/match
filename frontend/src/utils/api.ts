/**
 * API client utility with automatic token refresh
 */

interface RequestConfig extends RequestInit {
    skipAuth?: boolean;
}

class ApiClient {
    private baseURL: string;
    private refreshing: Promise<string> | null = null;

    constructor(baseURL: string = '') {
        this.baseURL = baseURL;
    }

    /**
     * Make an authenticated API request
     */
    async request<T = any>(
        endpoint: string,
        config: RequestConfig = {}
    ): Promise<T> {
        const { skipAuth, ...fetchConfig } = config;

        // Prepare headers
        const headers = new Headers(fetchConfig.headers);
        if (!headers.has('Content-Type')) {
            headers.set('Content-Type', 'application/json');
        }

        // Add authentication token if not skipped
        if (!skipAuth) {
            const token = localStorage.getItem('token');
            if (token) {
                headers.set('Authorization', `Bearer ${token}`);
            }
        }

        // Make the request
        let response = await fetch(`${this.baseURL}${endpoint}`, {
            ...fetchConfig,
            headers,
        });

        // Handle 401 Unauthorized - try to refresh token
        if (response.status === 401 && !skipAuth) {
            const newToken = await this.refreshToken();
            if (newToken) {
                // Retry the request with new token
                headers.set('Authorization', `Bearer ${newToken}`);
                response = await fetch(`${this.baseURL}${endpoint}`, {
                    ...fetchConfig,
                    headers,
                });
            } else {
                // Refresh failed, redirect to login
                this.handleAuthFailure();
                throw new Error('Authentication failed');
            }
        }

        // Handle non-OK responses
        if (!response.ok) {
            const error = await this.handleError(response);
            throw error;
        }

        // Parse and return response
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }

        return response.text() as any;
    }

    /**
     * Refresh the access token using refresh token
     */
    private async refreshToken(): Promise<string | null> {
        // Prevent multiple simultaneous refresh requests
        if (this.refreshing) {
            return this.refreshing;
        }

        this.refreshing = (async () => {
            try {
                const refreshToken = localStorage.getItem('refreshToken');
                if (!refreshToken) {
                    return null;
                }

                const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh_token: refreshToken }),
                });

                if (!response.ok) {
                    return null;
                }

                const data = await response.json();
                const newToken = data.access_token;

                // Update stored token
                localStorage.setItem('token', newToken);

                // Dispatch Redux action to update store
                if (window.dispatchTokenUpdate) {
                    window.dispatchTokenUpdate(newToken);
                }

                return newToken;
            } catch (error) {
                console.error('Token refresh failed:', error);
                return null;
            } finally {
                this.refreshing = null;
            }
        })();

        return this.refreshing;
    }

    /**
     * Handle authentication failure
     */
    private handleAuthFailure(): void {
        // Clear stored tokens
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');

        // Redirect to login page
        window.location.href = '/auth/login';
    }

    /**
     * Handle API errors
     */
    private async handleError(response: Response): Promise<Error> {
        let message = `Request failed with status ${response.status}`;

        try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                message = errorData.detail || errorData.message || message;
            } else {
                const text = await response.text();
                if (text) {
                    message = text;
                }
            }
        } catch (e) {
            // Failed to parse error, use default message
        }

        return new Error(message);
    }

    /**
     * Convenience methods for common HTTP verbs
     */
    get<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
        return this.request<T>(endpoint, { ...config, method: 'GET' });
    }

    post<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        return this.request<T>(endpoint, {
            ...config,
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    put<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        return this.request<T>(endpoint, {
            ...config,
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    patch<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        return this.request<T>(endpoint, {
            ...config,
            method: 'PATCH',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    delete<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
        return this.request<T>(endpoint, { ...config, method: 'DELETE' });
    }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export as 'api' for backward compatibility
export const api = apiClient;

// Extend Window interface for TypeScript
declare global {
    interface Window {
        dispatchTokenUpdate?: (token: string) => void;
    }
}

export default apiClient;
