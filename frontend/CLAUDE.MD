# Frontend Architecture

## Svelte 5 Requirements
**MANDATORY:** Use only Svelte 5 syntax and patterns:
- Use `$state()` for reactive variables instead of `let` declarations
- Use `$derived()` for computed values instead of reactive statements
- Use `$effect()` for side effects instead of reactive statements  
- Use `$props()` for component props instead of `export let`
- Use event attributes `onclick={}` instead of `on:click={}`
- Use `$bindable()` for two-way binding props
- Apply runes-first approach in ALL components

## Component Architecture
- Create UI components in `/src/components/ui/` for any non-standard HTML elements
- Components: Button, Input, Card, Modal, Slider, etc.
- **Zero inline CSS** in .svelte files - everything via reusable components
- **Maximum component reuse** - create minimal variants, extend via props
- **Nested components allowed** - Card can use Button, no duplicate components needed
- **Props for variations** - different colors/styles via component properties

## Pages & Layouts
- Place all page/layout .svelte files in dedicated directories
- **Minimal UI detail** on pages - compose primarily from components
- Pages should focus on data flow and component composition

## Centralized Styling System

### Design Tokens (Central Configuration)
Create `/src/styles/design-tokens.js` with:
```javascript
export const DESIGN_TOKENS = {
  // Colors
  colors: {
    dark: '#1a1a1a',
    light: '#f8f9fa', 
    lightBg: '#ffffff',
    darkText: '#2d3748',
    lightText: '#718096',
    accent: '#3182ce',
    success: '#38a169',
    failure: '#e53e3e'
  },
  
  // Spacing
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem'
  },
  
  // Typography
  fontSize: {
    sm: '0.875rem',
    base: '1rem', 
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem'
  },
  
  // Borders & Radius
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem'
  }
};
```

### Tailwind Theme Integration
- Use design tokens in `tailwind.config.js`
- **Only custom color classes** - no -100, -200 suffixes
- All components MUST use centralized theme classes
- Easy global theme changes via single config file

### Component Style Guidelines
- **Component-local styling** - Each component defines its own styles internally
- **No centralized style classes** - Styles are encapsulated within components
- **Consistent design tokens** - Use shared color/spacing variables from Tailwind config
- **Reusable components** - Create variations through props, not external style classes

## Styling Guidelines
- **Minimalist modern design** with consistent spacing and typography
- **Unified look & feel** across all components
- **Responsive design** with mobile-first approach
- **Accessibility considerations** in all UI components