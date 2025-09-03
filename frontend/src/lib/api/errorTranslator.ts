// Error pattern definitions
const ERROR_PATTERNS = {
  unique: ['unique constraint failed', 'already exists', 'duplicate', 'integrityerror', 'unique', 'violates unique constraint'],
  validation: ['validation', 'format', 'validationerror'],
  permission: ['permission', 'unauthorized', 'forbidden'],
  notFound: ['not found', 'does not exist'],
  foreignKey: ['foreign key constraint failed', 'foreign key'],
  database: ['database', 'connection']
} as const;

// Error messages
const ERROR_MESSAGES = {
  unique: 'This entry already exists. Please use different values.',
  validation: 'Invalid data format. Please check your inputs.',
  unauthorized: 'You need to be logged in to perform this action.',
  forbidden: 'You don\'t have permission to perform this action.',
  notFound: 'The requested item was not found.',
  foreignKey: 'This item is referenced by other data and cannot be modified.',
  database: 'Database connection error. Please try again later.',
  server: 'Server error. Please try again or contact the administrator.',
  generic: 'Something went wrong. Please try again or contact the administrator.',
  unexpected: 'An unexpected error occurred. Please try again or contact the administrator.'
} as const;

// Check if error message matches any pattern
function matchesPattern(lowerMessage: string, patterns: readonly string[]): boolean {
  return patterns.some(pattern => lowerMessage.includes(pattern));
}

// Get error category from message content
function getErrorCategory(lowerMessage: string): keyof typeof ERROR_MESSAGES | null {
  if (matchesPattern(lowerMessage, ERROR_PATTERNS.unique)) return 'unique';
  if (matchesPattern(lowerMessage, ERROR_PATTERNS.validation) && !lowerMessage.includes('unique')) return 'validation';
  if (matchesPattern(lowerMessage, ERROR_PATTERNS.permission)) return 'forbidden';
  if (matchesPattern(lowerMessage, ERROR_PATTERNS.notFound)) return 'notFound';
  if (matchesPattern(lowerMessage, ERROR_PATTERNS.foreignKey)) return 'foreignKey';
  if (matchesPattern(lowerMessage, ERROR_PATTERNS.database)) return 'database';
  return null;
}

/**
 * Translates technical API error messages into user-friendly messages
 */
export function translateApiError(errorData: any, status: number): string {
  const errorMessage = errorData?.detail || errorData?.message || errorData || '';
  
  // Handle by HTTP status first
  switch (status) {
    case 401: return ERROR_MESSAGES.unauthorized;
    case 403: return ERROR_MESSAGES.forbidden;
    case 404: return ERROR_MESSAGES.notFound;
    case 409: return ERROR_MESSAGES.unique;
    case 500: return ERROR_MESSAGES.server;
  }
  
  // Handle by message content
  if (typeof errorMessage === 'string' && errorMessage.length > 0) {
    const lowerMessage = errorMessage.toLowerCase();
    const category = getErrorCategory(lowerMessage);
    
    if (category) {
      return ERROR_MESSAGES[category];
    }
    
    return ERROR_MESSAGES.generic;
  }
  
  return ERROR_MESSAGES.unexpected;
}

/**
 * Translates network errors into user-friendly messages
 */
export function translateNetworkError(error: any): string {
  if (error?.name === 'AbortError') {
    return 'Request was cancelled. Please try again.';
  }
  
  if (error?.name === 'TypeError' && error?.message?.includes('fetch') ||
      error?.code === 'NETWORK_ERROR' || 
      error?.message?.includes('network')) {
    return 'Network error. Please check your internet connection and try again.';
  }
  
  return 'Unable to connect to the server. Please check your internet connection and try again.';
}