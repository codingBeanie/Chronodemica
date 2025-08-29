<script lang="ts">
  interface Props {
    text: string;
    mode?: 'dark' | 'light' | 'accent' | 'success' | 'failure';
    onclick?: () => void;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
  }
  
  let {
    text,
    mode = 'accent',
    onclick,
    type = 'button',
    disabled = false
  }: Props = $props();
  
  function getButtonClasses(mode: string): string {
    const baseClasses = "px-3 py-2 cursor-pointer rounded-lg transition-colors duration-200 font-medium focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
    
    switch (mode) {
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
  {type}
  {disabled}
  class={getButtonClasses(mode)}
  onclick={onclick}
>
  {text}
</button>