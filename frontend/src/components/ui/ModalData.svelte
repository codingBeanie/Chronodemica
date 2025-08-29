<script lang="ts">
  import Button from './Button.svelte';
  
  interface Props {
    datamodel: string;
    title?: string;
    buttonText?: string;
    isOpen?: boolean;
  }
  
  let {
    datamodel,
    title = `New ${datamodel}`,
    buttonText = `New ${datamodel}`,
    isOpen = $bindable(false)
  }: Props = $props();
  
  function openModal() {
    isOpen = true;
  }
  
  function handleSave() {
    isOpen = false;
  }
  
  function handleCancel() {
    isOpen = false;
  }
  
  function handleClickOutside() {
    isOpen = false;
  }
</script>

<Button text={buttonText} mode="accent" onclick={openModal} />

{#if isOpen}
  <div 
    class="fixed inset-0 flex items-center justify-center z-50"
    style="background-color: rgba(0, 0, 0, 0.7);"
    onclick={handleClickOutside}
    onkeydown={(e) => e.key === 'Escape' && handleClickOutside()}
    role="button"
    tabindex="0"
  >
    <div 
      class="bg-light rounded-lg shadow-xl max-w-md w-full mx-4"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      tabindex="-1"
    >
      <!-- Modal header -->
      <div class="px-6 py-4 border-b border-light-alt">
        <h2 class="text-xl font-semibold text-dark">
          {title}
        </h2>
      </div>
      
      <!-- Modal footer -->
      <div class="px-6 py-4 flex justify-end space-x-3">
        <Button text="Cancel" mode="light" onclick={handleCancel} />
        <Button text="Save" mode="accent" onclick={handleSave} />
      </div>
    </div>
  </div>
{/if}