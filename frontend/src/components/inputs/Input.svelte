<script lang="ts">
  interface Props {
    id: string;
    value?: string | number;
    placeholder?: string;
    label?: string;
    required?: boolean;
    disabled?: boolean;
    type?: 'text' | 'email' | 'password' | 'number';
    hint?: string;
    caption?: string;
  }
  
  let {
    id,
    value = $bindable(''),
    placeholder = '',
    label,
    required = false,
    disabled = false,
    type = 'text',
    hint,
    caption = ''
  }: Props = $props();
  
  const inputClasses = "w-full px-3 py-2 border border-light-alt rounded-lg bg-light text-dark-text placeholder-light-text focus:ring-2 focus:ring-accent focus:border-accent transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
</script>

<div class="space-y-1">
  {#if label}
    <div class="flex justify-between items-center">
      <div class="flex items-start gap-2 relative">
        <label for={id} class="block uppercase text-sm font-medium text-dark-text">
          {label}
          {#if required}<span class="text-failure">*</span>{/if}
        </label>
        {#if hint}
          <div class="relative group">
            <span class="text-xs text-lightText cursor-help rounded-full bg-light-alt w-4 h-4 flex items-center justify-center">?</span>
            <!-- HINT TOOLTIP: Appears on hover -->
            <div class="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-dark text-light text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
              {hint}
            </div>
          </div>
        {/if}
      </div>
      
      <!-- INPUT CAPTION: Optional right-aligned text -->
      {#if caption}
        <span class="text-sm text-lightText">{caption}</span>
      {/if}
    </div>
  {/if}
  
  <input
    {id}
    {type}
    {placeholder}
    {required}
    {disabled}
    bind:value
    class={inputClasses}
  />
</div>