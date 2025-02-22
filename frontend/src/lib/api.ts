interface ApiResponse<T = unknown> {
    status: boolean;
    message: string;
    data?: T;
    error?: unknown;
}

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

interface RequestOptions {
    method: HttpMethod;
    body?: unknown;
    headers?: Record<string, string>;
}

export class ApiHelper {
    private baseUrl: string;
    private defaultHeaders: Record<string, string>;

    constructor(
        baseUrl: string = `http://${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` ||
            "http://localhost:8000/api/v1"
    ) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
        this.defaultHeaders = {
            "Content-Type": "application/json",
        };
    }

    private async request<T>(endpoint: string, options: RequestOptions): Promise<ApiResponse<T>> {
        const url = `${this.baseUrl}${endpoint}`;

        try {
            const response = await fetch(url, {
                method: options.method,
                headers: {
                    ...this.defaultHeaders,
                    ...options.headers,
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
            });

            const data = await response.json();

            if (!response.ok) {
                throw {
                    status: false,
                    message: data.message || "An error occurred",
                    error: data.error,
                    statusCode: response.status,
                };
            }

            return data as ApiResponse<T>;
            // eslint-disable-next-line
        } catch (error: any) {
            if (error.status === false) {
                throw error;
            }

            throw {
                status: false,
                message: "Network error occurred",
                error: error.message,
            };
        }
    }

    async get<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, { method: "GET", headers });
    }

    async post<T>(
        endpoint: string,
        // eslint-disable-next-line
        body: any,
        headers?: Record<string, string>
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, { method: "POST", body, headers });
    }

    async put<T>(
        endpoint: string,
        // eslint-disable-next-line
        body: any,
        headers?: Record<string, string>
    ): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, { method: "PUT", body, headers });
    }

    async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
        return this.request<T>(endpoint, { method: "DELETE", headers });
    }

    setAuthToken(token: string) {
        this.defaultHeaders["Authorization"] = `Bearer ${token}`;
    }

    clearAuthToken() {
        delete this.defaultHeaders["Authorization"];
    }
}
