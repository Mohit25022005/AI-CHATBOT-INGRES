import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Bot, User, CheckCircle, Clock, FileText } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant' | 'system';
  timestamp: Date;
  type?: 'text' | 'diagnostic' | 'ticket' | 'log-analysis' | 'error-code';
  status?: 'processing' | 'completed' | 'error';
  errorCodes?: string[];
  ticketId?: string;
  canCreateTicket?: boolean;
}

interface ChatMessageProps {
  message: Message;
  onCreateTicket?: () => void;
}

export const ChatMessage = ({ message, onCreateTicket }: ChatMessageProps) => {
  const isUser = message.sender === 'user';
  const isSystem = message.sender === 'system';
  
  const getMessageIcon = () => {
    if (message.type === 'diagnostic') return <CheckCircle className="w-4 h-4 text-accent" />;
    if (message.type === 'ticket') return <FileText className="w-4 h-4 text-accent" />;
    return null;
  };

  return (
    <div className={`flex gap-3 mb-4 message-enter ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar className="w-8 h-8 border-2 border-primary/20">
          <AvatarImage src="" alt="INGRES Assistant" />
          <AvatarFallback className="bg-gradient-primary text-primary-foreground">
            <Bot className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
        <Card 
          className={`p-4 shadow-card ${
            isUser 
              ? 'bg-chat-user text-chat-user-foreground ml-auto' 
              : isSystem 
                ? 'bg-chat-system text-chat-system-foreground border border-accent/20'
                : 'bg-chat-assistant text-chat-assistant-foreground'
          }`}
        >
          <div className="flex items-start gap-2">
            {getMessageIcon()}
            <div className="flex-1">
              <p className="text-sm leading-relaxed whitespace-pre-line">{message.content}</p>
              
              {message.canCreateTicket && onCreateTicket && !message.ticketId && (
                <Button
                  variant="outline" 
                  size="sm"
                  onClick={onCreateTicket}
                  className="mt-3"
                >
                  Create Support Ticket
                </Button>
              )}
              
              {message.status && (
                <div className="mt-2 flex items-center gap-1 text-xs opacity-70">
                  {message.status === 'processing' && <Clock className="w-3 h-3 animate-spin" />}
                  {message.status === 'completed' && <CheckCircle className="w-3 h-3" />}
                  <span className="capitalize">{message.status}</span>
                </div>
              )}
            </div>
          </div>
        </Card>
        
        <div className="text-xs text-muted-foreground mt-1 px-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
      
      {isUser && (
        <Avatar className="w-8 h-8 border-2 border-primary/20">
          <AvatarImage src="" alt="User" />
          <AvatarFallback className="bg-secondary text-secondary-foreground">
            <User className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
};