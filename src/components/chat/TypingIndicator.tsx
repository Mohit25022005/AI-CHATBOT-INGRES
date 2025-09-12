import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Bot } from 'lucide-react';

export const TypingIndicator = () => {
  return (
    <div className="flex gap-3 mb-4">
      <Avatar className="w-8 h-8 border-2 border-primary/20">
        <AvatarImage src="" alt="INGRES Assistant" />
        <AvatarFallback className="bg-gradient-primary text-primary-foreground">
          <Bot className="w-4 h-4" />
        </AvatarFallback>
      </Avatar>
      <div className="max-w-[80%]">
        <div className="bg-chat-assistant border border-border rounded-lg p-4 shadow-card">
          <div className="flex items-center gap-1">
            <div className="text-sm text-muted-foreground">INGRES Assistant is thinking</div>
            <div className="flex gap-1 ml-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};