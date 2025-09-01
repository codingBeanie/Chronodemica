<script lang="ts">
  interface Props {
    text?: string;
    icon?: string;
    theme?: 'dark' | 'light' | 'accent' | 'success' | 'failure';
    type?: 'text' | 'icon' | 'text-icon';
    onclick?: () => void;
    disabled?: boolean;
  }
  
  let {
    text,
    icon,
    theme = 'accent',
    type = 'text',
    onclick,
    disabled = false
  }: Props = $props();
  
  function getButtonClasses(theme: string, buttonType: string): string {
    // Determine padding based on button type
    let baseClasses = "cursor-pointer rounded-lg transition-colors duration-200 focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
    
    switch (buttonType) {
      case 'icon':
        baseClasses = `p-2 ${baseClasses}`;
        break;
      case 'text':
        baseClasses = `px-3 py-2 font-medium ${baseClasses}`;
        break;
      case 'text-icon':
        baseClasses = `px-3 py-2 font-medium flex items-center ${baseClasses}`;
        break;
      default:
        baseClasses = `px-3 py-2 font-medium ${baseClasses}`;
    }
    
    // Apply theme colors
    switch (theme) {
      case 'dark':
        return `${baseClasses} bg-dark text-light hover:bg-dark-alt focus:ring-dark`;
      case 'light':
        return `${baseClasses} bg-light text-dark border border-light-alt hover:bg-light-alt focus:ring-light-alt`;
      case 'accent':
        return `${baseClasses} bg-accent text-light hover:bg-dark focus:ring-accent`;
      case 'success':
        return `${baseClasses} bg-success text-light hover:bg-success focus:ring-success`;
      case 'failure':
        return `${baseClasses} bg-failure text-light hover:bg-failure focus:ring-failure`;
      default:
        return `${baseClasses} bg-accent text-light hover:bg-dark focus:ring-accent`;
    }
  }
</script>

<button
  type="button"
  {disabled}
  class={getButtonClasses(theme, type)}
  onclick={onclick}
>
  {#if type === 'icon'}
    {#if icon}
      <i class={icon}></i>
    {/if}
  {:else if type === 'text'}
    {text || ''}
  {:else if type === 'text-icon'}
    {#if icon}
      <i class={icon}></i>
    {/if}
    {#if text}
      <span class="ml-2">{text}</span>
    {/if}
  {:else}
    <!-- Fallback for backward compatibility -->
    {#if icon}
      <i class={icon}></i>
    {/if}
    {#if text}
      {#if icon}<span class="ml-2">{text}</span>{:else}{text}{/if}
    {/if}
  {/if}
</button>