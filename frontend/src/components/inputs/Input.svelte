<script lang="ts">
  interface Props {
    id: string;
    value?: string;
    placeholder?: string;
    label?: string;
    required?: boolean;
    disabled?: boolean;
    type?: 'text' | 'email' | 'password' | 'number';
  }
  
  let {
    id,
    value = $bindable(''),
    placeholder = '',
    label,
    required = false,
    disabled = false,
    type = 'text'
  }: Props = $props();
  
  const inputClasses = "w-full px-3 py-2 border border-light-alt rounded-lg bg-light text-dark-text placeholder-light-text focus:ring-2 focus:ring-accent focus:border-accent transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
</script>

<div class="space-y-1">
  {#if label}
    <label for={id} class="block uppercase text-sm font-medium text-dark-text">
      {label}
      {#if required}<span class="text-failure">*</span>{/if}
    </label>
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