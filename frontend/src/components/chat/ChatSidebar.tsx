import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  BookOpen, 
  Wrench, 
  TicketPlus, 
  Database, 
  Shield, 
  Zap,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react';

const features = [
  {
    icon: <BookOpen className="w-4 h-4" />,
    title: "Documentation Search",
    description: "Instant access to INGRES docs",
    status: "active"
  },
  {
    icon: <Wrench className="w-4 h-4" />,
    title: "Smart Diagnostics", 
    description: "AI-powered troubleshooting",
    status: "active"
  },
  {
    icon: <TicketPlus className="w-4 h-4" />,
    title: "Auto Ticket Filing",
    description: "Streamlined support requests",
    status: "active"
  },
  {
    icon: <Database className="w-4 h-4" />,
    title: "Performance Analysis",
    description: "Query optimization suggestions",
    status: "beta"
  },
  {
    icon: <Shield className="w-4 h-4" />,
    title: "Security Insights",
    description: "Database security recommendations",
    status: "beta"
  },
];

const stats = [
  {
    icon: <Zap className="w-5 h-5 text-accent" />,
    label: "Avg Response Time",
    value: "< 2s"
  },
  {
    icon: <TrendingUp className="w-5 h-5 text-accent" />,
    label: "Resolution Rate", 
    value: "94%"
  },
  {
    icon: <Users className="w-5 h-5 text-accent" />,
    label: "Active Users",
    value: "2.1K"
  },
  {
    icon: <Clock className="w-5 h-5 text-accent" />,
    label: "24/7 Support",
    value: "Always On"
  }
];

export const ChatSidebar = () => {
  return (
    <Card className="w-80 h-full shadow-card bg-gradient-card border-r">
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-xl font-bold gradient-text mb-2">INGRES AI Assistant</h2>
          <p className="text-sm text-muted-foreground">
            Context-aware support with retrieval-augmented generation
          </p>
        </div>

        <Separator className="mb-6" />
        
        <div className="mb-6">
          <h3 className="text-sm font-semibold mb-4">Capabilities</h3>
          <ScrollArea className="h-64">
            <div className="space-y-3">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-background/50 hover:bg-background/80 transition-smooth">
                  <div className="text-primary mt-0.5">{feature.icon}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium truncate">{feature.title}</h4>
                      <Badge 
                        variant={feature.status === 'active' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {feature.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>

        <Separator className="mb-6" />

        <div>
          <h3 className="text-sm font-semibold mb-4">Performance Stats</h3>
          <div className="grid grid-cols-2 gap-4">
            {stats.map((stat, index) => (
              <div key={index} className="text-center p-3 rounded-lg bg-background/50">
                <div className="flex justify-center mb-2">{stat.icon}</div>
                <div className="text-lg font-bold text-primary">{stat.value}</div>
                <div className="text-xs text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};