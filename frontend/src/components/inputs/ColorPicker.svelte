<script lang="ts">
  interface Props {
    id: string;
    value?: string;
    label?: string;
    required?: boolean;
    disabled?: boolean;
  }
  
  let {
    id,
    value = $bindable('#000000'),
    label,
    required = false,
    disabled = false
  }: Props = $props();
  
  const inputClasses = "w-16 h-10 border border-light-alt rounded-lg bg-light cursor-pointer focus:ring-2 focus:ring-accent focus:border-accent transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
  const textInputClasses = "flex-1 px-3 py-2 border border-light-alt rounded-lg bg-light text-dark-text placeholder-light-text focus:ring-2 focus:ring-accent focus:border-accent transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
</script>

<div class="space-y-1">
  {#if label}
    <label for={id} class="block uppercase text-sm font-medium text-dark-text">
      {label}
      {#if required}<span class="text-failure">*</span>{/if}
    </label>
  {/if}
  
  <div class="flex items-center space-x-3">
    <input
      {id}
      type="color"
      {required}
      {disabled}
      bind:value
      class={inputClasses}
    />
    <input
      type="text"
      {required}
      {disabled}
      bind:value
      placeholder="#000000"
      maxlength="7"
      pattern="^#[0-9A-Fa-f]{6}$"
      class={textInputClasses}
    />
  </div>
</div>