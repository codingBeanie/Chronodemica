<script lang="ts">
  interface Props {
    content: string;
    visible?: boolean;
    x?: number;
    y?: number;
  }

  const { content, visible = false, x = 0, y = 0 } = $props<Props>();
</script>

{#if visible}
  <div 
    class="fixed z-50 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg shadow-sm pointer-events-none whitespace-nowrap"
    style="left: {x}px; top: {y}px; transform: translate(-50%, -100%); margin-top: -8px;"
  >
    {content}
    <!-- Tooltip arrow -->
    <div class="absolute top-full left-1/2 transform -translate-x-1/2">
      <div class="border-4 border-transparent border-t-gray-900"></div>
    </div>
  </div>
{/if}