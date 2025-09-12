import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ticketService, type Ticket } from '@/services/ticketService';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Clock, CheckCircle, XCircle, AlertCircle, Search, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

const Tickets = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [filteredTickets, setFilteredTickets] = useState<Ticket[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const { toast } = useToast();

  useEffect(() => {
    loadTickets();
  }, []);

  useEffect(() => {
    filterTickets();
  }, [tickets, searchQuery, statusFilter, priorityFilter]);

  const loadTickets = () => {
    const allTickets = ticketService.getAllTickets();
    setTickets(allTickets);
  };

  const filterTickets = () => {
    let filtered = [...tickets];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(ticket =>
        ticket.user_query.toLowerCase().includes(query) ||
        ticket.id.toLowerCase().includes(query) ||
        ticket.category?.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(ticket => ticket.status === statusFilter);
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(ticket => ticket.priority === priorityFilter);
    }

    setFilteredTickets(filtered);
  };

  const updateTicketStatus = (ticketId: string, newStatus: Ticket['status']) => {
    if (ticketService.updateTicketStatus(ticketId, newStatus)) {
      loadTickets();
      toast({
        title: 'Ticket Updated',
        description: `Ticket ${ticketId} status changed to ${newStatus}`,
      });
    }
  };

  const deleteTicket = (ticketId: string) => {
    if (ticketService.deleteTicket(ticketId)) {
      loadTickets();
      toast({
        title: 'Ticket Deleted',
        description: `Ticket ${ticketId} has been removed`,
      });
    }
  };

  const getStatusIcon = (status: Ticket['status']) => {
    switch (status) {
      case 'open':
        return <AlertCircle className="w-4 h-4 text-accent" />;
      case 'in-progress':
        return <Clock className="w-4 h-4 text-primary" />;
      case 'resolved':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'closed':
        return <XCircle className="w-4 h-4 text-muted-foreground" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: Ticket['status']) => {
    switch (status) {
      case 'open':
        return 'bg-accent text-accent-foreground';
      case 'in-progress':
        return 'bg-primary text-primary-foreground';
      case 'resolved':
        return 'bg-green-500 text-white';
      case 'closed':
        return 'bg-muted text-muted-foreground';
      default:
        return 'bg-secondary text-secondary-foreground';
    }
  };

  const getPriorityColor = (priority?: Ticket['priority']) => {
    switch (priority) {
      case 'urgent':
        return 'bg-destructive text-destructive-foreground';
      case 'high':
        return 'bg-orange-500 text-white';
      case 'medium':
        return 'bg-primary text-primary-foreground';
      case 'low':
        return 'bg-muted text-muted-foreground';
      default:
        return 'bg-secondary text-secondary-foreground';
    }
  };

  const stats = ticketService.getTicketStats();

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Support Tickets</h1>
            <p className="text-muted-foreground">Manage and track INGRES support requests</p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-primary">{stats.total}</div>
              <p className="text-sm text-muted-foreground">Total Tickets</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-accent">{stats.open}</div>
              <p className="text-sm text-muted-foreground">Open</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-primary">{stats.inProgress}</div>
              <p className="text-sm text-muted-foreground">In Progress</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-green-500">{stats.resolved}</div>
              <p className="text-sm text-muted-foreground">Resolved</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search tickets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="in-progress">In Progress</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <SelectValue placeholder="Filter by priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priority</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Tickets List */}
        <div className="space-y-4">
          {filteredTickets.length > 0 ? (
            filteredTickets.map((ticket) => (
              <Card key={ticket.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(ticket.status)}
                        <CardTitle className="text-lg">{ticket.id}</CardTitle>
                        <Badge className={getStatusColor(ticket.status)}>
                          {ticket.status.replace('-', ' ')}
                        </Badge>
                        {ticket.priority && (
                          <Badge variant="outline" className={getPriorityColor(ticket.priority)}>
                            {ticket.priority}
                          </Badge>
                        )}
                        {ticket.category && (
                          <Badge variant="secondary">{ticket.category}</Badge>
                        )}
                      </div>
                      <CardDescription className="text-sm">
                        {new Date(ticket.timestamp).toLocaleDateString()} at{' '}
                        {new Date(ticket.timestamp).toLocaleTimeString()}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      {ticket.status !== 'resolved' && ticket.status !== 'closed' && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateTicketStatus(ticket.id, 'in-progress')}
                            disabled={ticket.status === 'in-progress'}
                          >
                            Start
                          </Button>
                          <Button
                            size="sm"
                            variant="default"
                            onClick={() => updateTicketStatus(ticket.id, 'resolved')}
                          >
                            Resolve
                          </Button>
                        </>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteTicket(ticket.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm mb-3">{ticket.user_query}</p>
                  
                  {ticket.error_codes && ticket.error_codes.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium mb-1">Error Codes:</p>
                      <div className="flex flex-wrap gap-1">
                        {ticket.error_codes.map((code) => (
                          <Badge key={code} variant="destructive" className="text-xs">
                            {code}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {ticket.resolution && (
                    <div className="border-t pt-3 mt-3">
                      <p className="text-sm font-medium mb-1">Resolution:</p>
                      <p className="text-sm text-muted-foreground">{ticket.resolution}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No tickets found</h3>
                <p className="text-muted-foreground">
                  {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all'
                    ? 'No tickets match your current filters.'
                    : 'No support tickets have been created yet.'}
                </p>
                {(searchQuery || statusFilter !== 'all' || priorityFilter !== 'all') && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSearchQuery('');
                      setStatusFilter('all');
                      setPriorityFilter('all');
                    }}
                    className="mt-4"
                  >
                    Clear Filters
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Tickets;