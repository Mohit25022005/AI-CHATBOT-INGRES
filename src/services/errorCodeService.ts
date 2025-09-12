import errorCodesData from '@/data/error_codes.json';

export interface ErrorCodeInfo {
  description: string;
  category: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  troubleshooting: string[];
  common_causes: string[];
}

class ErrorCodeService {
  private errorCodes: Record<string, ErrorCodeInfo>;

  constructor() {
    this.errorCodes = errorCodesData as Record<string, ErrorCodeInfo>;
  }

  findErrorCode(text: string): string | null {
    // Common INGRES error code patterns
    const patterns = [
      /E_US\d{4}/g,           // E_US0845 format
      /INGRES-\d{4}/g,        // INGRES-0845 format  
      /ERR_\d{4}/g,           // ERR_0845 format
      /ERROR\s+(\d{4})/g      // ERROR 0845 format
    ];

    for (const pattern of patterns) {
      const matches = text.match(pattern);
      if (matches) {
        for (const match of matches) {
          const normalized = this.normalizeErrorCode(match);
          if (this.errorCodes[normalized]) {
            return normalized;
          }
        }
      }
    }
    return null;
  }

  findAllErrorCodes(text: string): string[] {
    const patterns = [
      /E_US\d{4}/g,
      /INGRES-\d{4}/g,
      /ERR_\d{4}/g,
      /ERROR\s+(\d{4})/g
    ];

    const found: string[] = [];
    for (const pattern of patterns) {
      const matches = text.match(pattern);
      if (matches) {
        for (const match of matches) {
          const normalized = this.normalizeErrorCode(match);
          if (this.errorCodes[normalized] && !found.includes(normalized)) {
            found.push(normalized);
          }
        }
      }
    }
    return found;
  }

  private normalizeErrorCode(code: string): string {
    // Convert various formats to E_US format
    if (code.startsWith('E_US')) return code;
    if (code.startsWith('INGRES-')) return code.replace('INGRES-', 'E_US');
    if (code.startsWith('ERR_')) return code.replace('ERR_', 'E_US');
    
    const match = code.match(/ERROR\s+(\d{4})/);
    if (match) return `E_US${match[1]}`;
    
    return code;
  }

  getErrorInfo(code: string): ErrorCodeInfo | null {
    const normalized = this.normalizeErrorCode(code);
    return this.errorCodes[normalized] || null;
  }

  getAllErrorCodes(): string[] {
    return Object.keys(this.errorCodes);
  }

  searchErrorCodes(query: string): string[] {
    const lowercaseQuery = query.toLowerCase();
    return Object.keys(this.errorCodes).filter(code => {
      const info = this.errorCodes[code];
      return (
        code.toLowerCase().includes(lowercaseQuery) ||
        info.description.toLowerCase().includes(lowercaseQuery) ||
        info.category.toLowerCase().includes(lowercaseQuery) ||
        info.troubleshooting.some(step => step.toLowerCase().includes(lowercaseQuery))
      );
    });
  }
}

export const errorCodeService = new ErrorCodeService();