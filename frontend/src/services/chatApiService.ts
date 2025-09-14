// Chat API service for backend communication

const API_BASE_URL = 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  reply: string;
  sources: Array<{
    source: string;
    title: string;
    text: string;
  }>;
}

export interface TicketRequest {
  session_id: string;
  issue: string;
  chat_history?: any[];
}

export interface TicketResponse {
  ticket_id: string;
  status: string;
}

class ChatApiService {
  private async makeRequest<T>(endpoint: string, options: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }

    return response.json();
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.makeRequest<ChatResponse>('/chat/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async createTicket(request: TicketRequest): Promise<TicketResponse> {
    return this.makeRequest<TicketResponse>('/ticket/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async checkHealth(): Promise<{ status: string; service: string }> {
    return this.makeRequest<{ status: string; service: string }>('/', {
      method: 'GET',
    });
  }
}

export const chatApiService = new ChatApiService();