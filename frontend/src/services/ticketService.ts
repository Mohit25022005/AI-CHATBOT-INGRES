export interface Ticket {
  id: string;
  user_query: string;
  timestamp: string;
  status: 'open' | 'in-progress' | 'resolved' | 'closed';
  category?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  assignee?: string;
  resolution?: string;
  error_codes?: string[];
}

const TICKETS_STORAGE_KEY = 'ingres-tickets';

class TicketService {
  private getTickets(): Ticket[] {
    try {
      const stored = localStorage.getItem(TICKETS_STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error loading tickets:', error);
      return [];
    }
  }

  private saveTickets(tickets: Ticket[]): void {
    try {
      localStorage.setItem(TICKETS_STORAGE_KEY, JSON.stringify(tickets));
    } catch (error) {
      console.error('Error saving tickets:', error);
    }
  }

  createTicket(query: string, errorCodes?: string[]): Ticket {
    const tickets = this.getTickets();
    
    // Determine priority based on error codes and content
    let priority: Ticket['priority'] = 'medium';
    if (errorCodes?.length || query.toLowerCase().includes('critical') || query.toLowerCase().includes('urgent')) {
      priority = 'high';
    } else if (query.toLowerCase().includes('slow') || query.toLowerCase().includes('performance')) {
      priority = 'medium';
    }

    // Categorize based on content
    let category = 'General';
    if (query.toLowerCase().includes('connection') || query.toLowerCase().includes('timeout')) {
      category = 'Connection';
    } else if (query.toLowerCase().includes('authentication') || query.toLowerCase().includes('login')) {
      category = 'Authentication';
    } else if (query.toLowerCase().includes('performance') || query.toLowerCase().includes('slow')) {
      category = 'Performance';
    } else if (query.toLowerCase().includes('error') || errorCodes?.length) {
      category = 'Error Investigation';
    }

    const ticket: Ticket = {
      id: `ING-${Date.now()}-${Math.random().toString(36).substr(2, 4).toUpperCase()}`,
      user_query: query,
      timestamp: new Date().toISOString(),
      status: 'open',
      category,
      priority,
      error_codes: errorCodes
    };

    tickets.unshift(ticket); // Add to beginning
    this.saveTickets(tickets);
    return ticket;
  }

  getAllTickets(): Ticket[] {
    return this.getTickets();
  }

  getTicketById(id: string): Ticket | undefined {
    return this.getTickets().find(ticket => ticket.id === id);
  }

  updateTicketStatus(id: string, status: Ticket['status']): boolean {
    const tickets = this.getTickets();
    const ticketIndex = tickets.findIndex(ticket => ticket.id === id);
    
    if (ticketIndex !== -1) {
      tickets[ticketIndex].status = status;
      if (status === 'resolved' || status === 'closed') {
        tickets[ticketIndex].resolution = status === 'resolved' ? 'Issue resolved by support team' : 'Ticket closed';
      }
      this.saveTickets(tickets);
      return true;
    }
    return false;
  }

  deleteTicket(id: string): boolean {
    const tickets = this.getTickets();
    const filteredTickets = tickets.filter(ticket => ticket.id !== id);
    
    if (filteredTickets.length !== tickets.length) {
      this.saveTickets(filteredTickets);
      return true;
    }
    return false;
  }

  getTicketStats() {
    const tickets = this.getTickets();
    return {
      total: tickets.length,
      open: tickets.filter(t => t.status === 'open').length,
      inProgress: tickets.filter(t => t.status === 'in-progress').length,
      resolved: tickets.filter(t => t.status === 'resolved').length,
      closed: tickets.filter(t => t.status === 'closed').length
    };
  }
}

export const ticketService = new TicketService();