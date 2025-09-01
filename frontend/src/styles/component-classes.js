// Centralized component styling classes
export const COMPONENT_STYLES = {
  // Button styles
  button: {
    primary: 'bg-accent text-light hover:opacity-90 px-4 py-2 rounded-md transition-opacity',
    secondary: 'bg-light text-dark border border-light-alt hover:bg-light-alt px-4 py-2 rounded-md transition-colors',
    icon: 'p-2 rounded-md hover:bg-light-alt transition-colors',
    iconLight: 'p-2 rounded-md hover:bg-light-alt text-dark-alt hover:text-dark transition-colors'
  },

  // Input styles  
  input: 'bg-light border border-light-alt px-3 py-2 rounded-md focus:border-accent focus:outline-none transition-colors',

  // Card styles
  card: 'bg-light p-6 rounded-lg shadow-sm border border-light-alt',

  // Table styles
  table: {
    wrapper: 'w-full',
    scrollWrapper: 'overflow-x-auto',
    table: 'min-w-full table-auto',
    
    header: {
      thead: 'bg-light-alt',
      tr: 'bg-light-alt',
      th: 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider whitespace-nowrap',
      thLast: 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider w-full',
      thActions: 'px-6 py-4 text-right text-xs font-medium text-dark uppercase tracking-wider w-1 whitespace-nowrap'
    },
    
    body: {
      tbody: 'bg-light divide-y divide-light-alt',
      tr: 'hover:bg-light-alt transition-colors duration-200',
      td: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt',
      tdLast: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt w-full',
      tdActions: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt text-right'
    },
    
    states: {
      loading: 'text-center py-8 text-dark',
      noData: 'text-center py-8 text-dark'
    }
  },

  // Color display styles
  colorDisplay: {
    wrapper: 'flex items-center space-x-2',
    swatch: 'w-6 h-6 border border-light-alt rounded flex-shrink-0',
    text: 'font-mono text-sm text-dark-alt'
  },

  // Layout styles
  layout: {
    container: 'w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    section: 'mb-6',
    buttonGroup: 'mb-4 flex justify-start',
    actionButtons: 'flex items-center space-x-2'
  },

  // Modal styles
  modal: {
    overlay: 'fixed inset-0 flex items-center justify-center z-50',
    backdrop: 'rgba(0,0,0 , 0.7)', // dark color with transparency
    container: 'bg-light rounded-lg shadow-xl max-w-md w-full mx-4',
    header: 'px-6 py-4 border-b border-light-alt',
    title: 'text-xl font-semibold text-dark',
    content: 'px-6 py-4 max-h-96 overflow-auto',
    footer: 'px-6 py-4 flex items-center justify-between',
    form: 'space-y-4',
    field: 'space-y-1',
    error: 'text-failure text-sm mt-1',
    loading: 'text-dark p-4 bg-light-alt rounded text-center',
    apiError: 'text-failure text-sm'
  }
};