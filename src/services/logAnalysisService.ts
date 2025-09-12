import { errorCodeService } from './errorCodeService';

export interface LogAnalysisResult {
  errorCodes: string[];
  recommendations: string[];
  summary: string;
  urgencyLevel: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

class LogAnalysisService {
  analyzeLogContent(content: string): LogAnalysisResult {
    const errorCodes = errorCodeService.findAllErrorCodes(content);
    const recommendations: string[] = [];
    let urgencyLevel: LogAnalysisResult['urgencyLevel'] = 'low';

    // Analyze each error code found
    errorCodes.forEach(code => {
      const errorInfo = errorCodeService.getErrorInfo(code);
      if (errorInfo) {
        recommendations.push(`**${code}**: ${errorInfo.description}`);
        errorInfo.troubleshooting.forEach(step => {
          recommendations.push(`  • ${step}`);
        });

        // Determine urgency based on severity
        if (errorInfo.severity === 'Critical') {
          urgencyLevel = 'critical';
        } else if (errorInfo.severity === 'High' && urgencyLevel !== 'critical') {
          urgencyLevel = 'high';
        } else if (errorInfo.severity === 'Medium' && urgencyLevel === 'low') {
          urgencyLevel = 'medium';
        }
      }
    });

    // Analyze log patterns
    const patterns = this.analyzeLogPatterns(content);
    recommendations.push(...patterns.recommendations);
    
    // Merge urgency levels (higher priority wins)
    const urgencyPriority = { 'low': 0, 'medium': 1, 'high': 2, 'critical': 3 };
    if (urgencyPriority[patterns.urgencyLevel] > urgencyPriority[urgencyLevel]) {
      urgencyLevel = patterns.urgencyLevel;
    }

    // Generate summary
    let summary = `Log analysis completed. Found ${errorCodes.length} error code(s).`;
    if (errorCodes.length > 0) {
      summary += ` Primary issues: ${errorCodes.slice(0, 3).join(', ')}`;
    }
    if (patterns.issueCount > 0) {
      summary += ` Additional ${patterns.issueCount} pattern-based issues detected.`;
    }

    return {
      errorCodes,
      recommendations,
      summary,
      urgencyLevel,
      timestamp: new Date().toISOString()
    };
  }

  private analyzeLogPatterns(content: string): {
    recommendations: string[];
    urgencyLevel: LogAnalysisResult['urgencyLevel'];
    issueCount: number;
  } {
    const recommendations: string[] = [];
    let urgencyLevel: LogAnalysisResult['urgencyLevel'] = 'low';
    let issueCount = 0;

    const lowercaseContent = content.toLowerCase();

    // Connection issues
    if (lowercaseContent.includes('connection') && (lowercaseContent.includes('timeout') || lowercaseContent.includes('failed'))) {
      recommendations.push('**Connection Issues Detected**');
      recommendations.push('  • Check network connectivity and firewall settings');
      recommendations.push('  • Verify database server status and availability');
      recommendations.push('  • Review connection pool configuration');
      urgencyLevel = 'high';
      issueCount++;
    }

    // Performance issues
    const slowQuery = lowercaseContent.includes('slow query') || lowercaseContent.includes('execution time');
    const highCPU = lowercaseContent.includes('cpu') && lowercaseContent.includes('high');
    if (slowQuery || highCPU) {
      recommendations.push('**Performance Issues Detected**');
      recommendations.push('  • Review query performance and indexing');
      recommendations.push('  • Check system resource utilization');
      recommendations.push('  • Consider query optimization');
      if (urgencyLevel === 'low') urgencyLevel = 'medium';
      issueCount++;
    }

    // Memory issues
    if (lowercaseContent.includes('out of memory') || lowercaseContent.includes('memory allocation')) {
      recommendations.push('**Memory Issues Detected**');
      recommendations.push('  • Monitor system memory usage');
      recommendations.push('  • Review buffer pool settings');
      recommendations.push('  • Consider increasing available memory');
      urgencyLevel = 'high';
      issueCount++;
    }

    // Disk space issues
    if (lowercaseContent.includes('disk') && (lowercaseContent.includes('full') || lowercaseContent.includes('space'))) {
      recommendations.push('**Disk Space Issues Detected**');
      recommendations.push('  • Free up disk space immediately');
      recommendations.push('  • Archive or purge old log files');
      recommendations.push('  • Implement disk space monitoring');
      urgencyLevel = 'critical';
      issueCount++;
    }

    // Deadlock patterns
    if (lowercaseContent.includes('deadlock')) {
      recommendations.push('**Deadlock Issues Detected**');
      recommendations.push('  • Review transaction design and locking order');
      recommendations.push('  • Minimize transaction duration');
      recommendations.push('  • Implement deadlock retry logic');
      if (urgencyLevel === 'low') urgencyLevel = 'medium';
      issueCount++;
    }

    return { recommendations, urgencyLevel, issueCount };
  }

  async analyzeLogFile(file: File): Promise<LogAnalysisResult> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const result = this.analyzeLogContent(content);
          resolve(result);
        } catch (error) {
          reject(new Error('Failed to analyze log file'));
        }
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read log file'));
      };
      
      reader.readAsText(file);
    });
  }
}

export const logAnalysisService = new LogAnalysisService();