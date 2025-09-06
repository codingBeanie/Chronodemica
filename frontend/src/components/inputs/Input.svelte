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
  
  // Configuration
  const INPUT_CONFIG = {
    BASE_CLASSES: "w-full px-3 py-2 border border-light-alt rounded-lg bg-light text-dark-text placeholder-light-text focus:ring-2 focus:ring-accent focus:border-accent transition-colors duration-200",
    DISABLED_CLASSES: "opacity-50 cursor-not-allowed",
    TOOLTIP_CLASSES: "absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-dark text-light text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10"
  };

  // Computed values
  let inputClasses = $derived(getInputClasses(disabled));
  let showLabel = $derived(!!label);
  let showHint = $derived(!!hint);
  let showCaption = $derived(!!caption);
  let labelData = $derived(renderLabel());
  let hintData = $derived(renderHintTooltip());

  function getInputClasses(isDisabled: boolean): string {
    return isDisabled 
      ? `${INPUT_CONFIG.BASE_CLASSES} ${INPUT_CONFIG.DISABLED_CLASSES}`
      : INPUT_CONFIG.BASE_CLASSES;
  }

  function renderLabel() {
    return {
      text: label,
      required: required,
      classes: "block uppercase text-sm font-medium text-dark-text"
    };
  }

  function renderHintTooltip() {
    return {
      icon: "text-xs text-lightText cursor-help rounded-full bg-light-alt w-4 h-4 flex items-center justify-center",
      tooltip: INPUT_CONFIG.TOOLTIP_CLASSES,
      text: hint
    };
  }
</script>

<div class="space-y-1">
  {#if showLabel}
    <div class="flex justify-between items-center">
      <div class="flex items-start gap-2 relative">
        <label for={id} class={labelData.classes}>
          {labelData.text}
          {#if labelData.required}<span class="text-failure">*</span>{/if}
        </label>
        
        {#if showHint}
          <div class="relative group">
            <span class={hintData.icon}>?</span>
            <div class={hintData.tooltip}>
              {hintData.text}
            </div>
          </div>
        {/if}
      </div>
      
      {#if showCaption}
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