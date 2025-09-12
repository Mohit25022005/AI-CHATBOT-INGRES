import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Send, Paperclip, Mic, Square } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string, file?: File) => void;
  isProcessing?: boolean;
}

export const ChatInput = ({ onSendMessage, isProcessing = false }: ChatInputProps) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((message.trim() || selectedFile) && !isProcessing) {
      onSendMessage(message.trim() || selectedFile?.name || '', selectedFile || undefined);
      setMessage('');
      setSelectedFile(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Accept .txt, .log files for log analysis
      const validTypes = ['text/plain', '.log', '.txt'];
      const isValid = validTypes.some(type => 
        file.type === type || file.name.toLowerCase().endsWith(type.replace('text/', '.'))
      );
      
      if (isValid) {
        setSelectedFile(file);
      } else {
        alert('Please upload a .txt or .log file for analysis.');
      }
    }
    e.target.value = ''; // Reset input
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Voice recording logic would go here
  };
  return (
    <Card className="p-4 shadow-card bg-gradient-card border-t">
      <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1 relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              selectedFile 
                ? `Analyzing ${selectedFile.name}...` 
                : "Ask about INGRES documentation, troubleshooting, or file a support ticket..."
            }
            disabled={isProcessing}
            className="pr-12 bg-background border-border focus:ring-primary"
          />
          <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {selectedFile && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-destructive"
                onClick={() => setSelectedFile(null)}
              >
                ✕
              </Button>
            )}
            <input
              type="file"
              accept=".txt,.log,text/plain"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <Paperclip className="w-4 h-4" />
            </Button>
          </div>
        </div>
        
        <Button
          type="button"
          variant={isRecording ? "destructive" : "assistant"}
          size="icon"
          onClick={toggleRecording}
          className="h-10 w-10"
        >
          {isRecording ? <Square className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </Button>
        
        <Button
          type="submit"
          variant="chat"
          size="icon"
          disabled={(!message.trim() && !selectedFile) || isProcessing}
          className="h-10 w-10"
        >
          <Send className="w-4 h-4" />
        </Button>
      </form>
      
      {/* File upload status */}
      {selectedFile && (
        <div className="flex items-center gap-2 mt-2 p-2 bg-muted rounded-md">
          <span className="text-sm text-muted-foreground">
            📄 {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </span>
        </div>
      )}
      
      {/* Quick action buttons */}
      <div className="flex flex-wrap gap-2 mt-3">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSendMessage("Help me troubleshoot a database connection issue")}
          disabled={isProcessing}
        >
          Troubleshoot
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSendMessage("Show me the latest INGRES documentation")}
          disabled={isProcessing}
        >
          Documentation
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSendMessage("File a support ticket")}
          disabled={isProcessing}
        >
          File Ticket
        </Button>
      </div>
    </Card>
  );
};