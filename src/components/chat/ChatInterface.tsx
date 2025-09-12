import React, { useState, useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatSidebar } from './ChatSidebar';
import { TypingIndicator } from './TypingIndicator';
import { useToast } from '@/hooks/use-toast';
import { RefreshCw, Settings, Maximize2, Ticket } from 'lucide-react';
import { Link } from 'react-router-dom';
import { errorCodeService } from '@/services/errorCodeService';
import { ticketService } from '@/services/ticketService';
import { logAnalysisService } from '@/services/logAnalysisService';
import heroImage from '@/assets/ingres-hero.jpg';

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

export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: '1',
      content: "Welcome to INGRES AI Assistant! I'm here to help with documentation, troubleshooting, and support tickets. What can I assist you with today?",
      sender: 'assistant',
      timestamp: new Date(),
      type: 'text'
    };
    setMessages([welcomeMessage]);
  }, []);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (content: string, file?: File) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      // Check if it's a file upload for log analysis
      if (file) {
        const analysisResult = await logAnalysisService.analyzeLogFile(file);
        
        let responseContent = `**Log Analysis Complete**\n\n${analysisResult.summary}\n\n`;
        responseContent += `**Urgency Level:** ${analysisResult.urgencyLevel.toUpperCase()}\n\n`;
        
        if (analysisResult.recommendations.length > 0) {
          responseContent += `**Recommendations:**\n${analysisResult.recommendations.join('\n')}\n\n`;
        }

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: responseContent,
          sender: 'assistant',
          timestamp: new Date(),
          type: 'log-analysis',
          status: 'completed',
          errorCodes: analysisResult.errorCodes,
          canCreateTicket: analysisResult.urgencyLevel !== 'low'
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsProcessing(false);
        return;
      }

      // Check for error codes in the message
      const errorCodes = errorCodeService.findAllErrorCodes(content);
      
      if (errorCodes.length > 0) {
        // Handle error code diagnosis
        let responseContent = `**Error Code Analysis**\n\nI found ${errorCodes.length} error code(s) in your message:\n\n`;
        
        errorCodes.forEach(code => {
          const errorInfo = errorCodeService.getErrorInfo(code);
          if (errorInfo) {
            responseContent += `**${code}**: ${errorInfo.description}\n`;
            responseContent += `**Category**: ${errorInfo.category} | **Severity**: ${errorInfo.severity}\n\n`;
            responseContent += `**Troubleshooting Steps:**\n`;
            errorInfo.troubleshooting.forEach((step, index) => {
              responseContent += `${index + 1}. ${step}\n`;
            });
            responseContent += '\n';
          }
        });

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: responseContent,
          sender: 'assistant',
          timestamp: new Date(),
          type: 'error-code',
          status: 'completed',
          errorCodes,
          canCreateTicket: true
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsProcessing(false);
        return;
      }

      // Simulate AI response with different types based on message content
      setTimeout(() => {
        let responseContent = '';
        let messageType: Message['type'] = 'text';
        let status: Message['status'] | undefined;
        let canCreateTicket = false;

        if (content.toLowerCase().includes('troubleshoot') || content.toLowerCase().includes('error')) {
          responseContent = "I'll help you diagnose this issue. Let me run some diagnostics on your INGRES database configuration...\n\nBased on your description, here are some initial troubleshooting steps:\n\n• Check database server connectivity\n• Verify user permissions and authentication\n• Review recent system logs for error patterns\n• Examine database configuration settings\n\nIf the issue persists, I can help you create a support ticket.";
          messageType = 'diagnostic';
          status = 'completed';
          canCreateTicket = true;
        } else if (content.toLowerCase().includes('ticket') || content.toLowerCase().includes('support')) {
          responseContent = "I'll create a support ticket for you based on your description.";
          messageType = 'ticket';
          status = 'processing';
        } else if (content.toLowerCase().includes('documentation') || content.toLowerCase().includes('docs')) {
          responseContent = "Here are the most relevant INGRES documentation sections for your query:\n\n• Database Configuration Guide (v12.2)\n• Performance Optimization Best Practices\n• Troubleshooting Connection Issues\n• User Management and Security\n• Backup and Recovery Procedures\n\nWould you like me to dive deeper into any specific topic?";
        } else {
          responseContent = "I understand you're asking about INGRES. I can help you with:\n\n• **Documentation lookup** - Find specific guides and references\n• **Error diagnosis** - Analyze error codes and logs\n• **Troubleshooting** - Step-by-step issue resolution\n• **Support tickets** - File and track support requests\n• **Performance optimization** - Database tuning advice\n\nPlease be more specific about your needs, or upload a log file for analysis.";
          canCreateTicket = false;
        }

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: responseContent,
          sender: 'assistant',
          timestamp: new Date(),
          type: messageType,
          status,
          canCreateTicket
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsProcessing(false);

        // Handle ticket creation
        if (messageType === 'ticket') {
          setTimeout(() => {
            const ticket = ticketService.createTicket(content, errorCodes);
            
            const ticketMessage: Message = {
              id: (Date.now() + 2).toString(),
              content: `Support ticket created successfully!\n\n**Ticket ID:** ${ticket.id}\n**Priority:** ${ticket.priority}\n**Category:** ${ticket.category}\n**Status:** ${ticket.status}\n\nYour issue has been logged and assigned to our support team. You can track the progress in the [Tickets](/tickets) section.`,
              sender: 'assistant',
              timestamp: new Date(),
              type: 'ticket',
              status: 'completed',
              ticketId: ticket.id
            };

            setMessages(prev => [...prev, ticketMessage]);
            
            toast({
              title: 'Support Ticket Created',
              description: `Ticket ${ticket.id} has been filed successfully.`,
            });
          }, 1500);
        }
      }, 2000);

    } catch (error) {
      setIsProcessing(false);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        type: 'text',
        status: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const createTicketFromMessage = (message: Message) => {
    if (!message.canCreateTicket) return;
    
    const ticket = ticketService.createTicket(
      `User reported: ${message.content}`,
      message.errorCodes
    );
    
    toast({
      title: 'Support Ticket Created',
      description: `Ticket ${ticket.id} has been filed successfully.`,
    });

    const ticketMessage: Message = {
      id: Date.now().toString(),
      content: `Support ticket ${ticket.id} has been created for this issue. You can track its progress in the [Tickets](/tickets) section.`,
      sender: 'system',
      timestamp: new Date(),
      type: 'ticket',
      status: 'completed',
      ticketId: ticket.id
    };

    setMessages(prev => [...prev, ticketMessage]);
  };

  // ✅ Proper clearChat function
  const clearChat = () => {
    setMessages([{
      id: '1',
      content: "Chat cleared. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date(),
      type: 'text'
    }]);

    toast({
      title: "Chat Cleared",
      description: "Conversation history has been reset.",
    });
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      {showSidebar && <ChatSidebar />}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Card className="flex items-center justify-between p-4 shadow-card bg-gradient-card border-b">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">AI</span>
            </div>
            <div>
              <h1 className="font-bold text-lg">INGRES Virtual Assistant</h1>
              <p className="text-sm text-muted-foreground">Smart support for database operations</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={clearChat}>
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="w-4 h-4" />
            </Button>
            <Link to="/tickets">
              <Button variant="ghost" size="icon">
                <Ticket className="w-4 h-4" />
              </Button>
            </Link>
            <Button variant="ghost" size="icon" onClick={() => setShowSidebar(!showSidebar)}>
              <Maximize2 className="w-4 h-4" />
            </Button>
          </div>
        </Card>

        {/* Hero Section (shown when no user messages yet) */}
        {messages.length <= 1 && (
          <div 
            className="relative py-16 px-8 text-center bg-cover bg-center bg-no-repeat"
            style={{ backgroundImage: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), url(${heroImage})` }}
          >
            <div className="relative z-10 max-w-3xl mx-auto">
              <h1 className="text-4xl font-bold text-white mb-4">
                Welcome to INGRES <span className="gradient-text">AI Assistant</span>
              </h1>
              <p className="text-xl text-white/90 mb-8 leading-relaxed">
                Context-aware diagnostic chatbot with retrieval-augmented generation for seamless INGRES database support
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Button 
                  variant="hero" 
                  className="shadow-glow"
                  onClick={() => handleSendMessage("Help me troubleshoot a database connection issue")}
                >
                  Start Troubleshooting
                </Button>
                <Button 
                  variant="assistant"
                  onClick={() => handleSendMessage("Show me the latest INGRES documentation")}
                >
                  Browse Documentation
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage 
                key={message.id} 
                message={message} 
                onCreateTicket={() => createTicketFromMessage(message)}
              />
            ))}
            {isProcessing && <TypingIndicator />}
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="p-6 pt-0">
          <div className="max-w-4xl mx-auto">
            <ChatInput onSendMessage={handleSendMessage} isProcessing={isProcessing} />
          </div>
        </div>
      </div>
    </div>
  );
};