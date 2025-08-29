<script>
  import ModalData from './ModalData.svelte';
  
  export let model = '';
  
  let data = [];
  let headers = [];
  let loading = false;
  
  // CSS Class Configurations - Easy to customize
  const tableClasses = {
    wrapper: "w-full",
    scrollWrapper: "overflow-x-auto",
    table: "min-w-full",
    header: {
      thead: "bg-light",
      tr: "bg-light-alt",
      th: "px-4 py-4 text-left text-xs font-medium uppercase tracking-wider first:rounded-tl-lg first:rounded-bl-lg last:rounded-tr-lg last:rounded-br-lg"
    },
    body: {
      tbody: "divide-y divide-light-alt",
      tr: "hover:bg-light-alt transition-colors duration-200 border-b border-light-alt",
      td: "px-4 py-4 whitespace-nowrap text-sm text-dark-alt first:rounded-tl-lg first:rounded-bl-lg last:rounded-tr-lg last:rounded-br-lg"
    },
    states: {
      loading: "text-center py-4 text-dark-alt",
      noData: "text-center py-4 text-dark-alt"
    }
  };
  
  async function loadDataStructure() {
    if (!model) return;
    
    try {
      const response = await fetch(`/api/data-structure/${model.toLowerCase()}`);
      const structure = await response.json();
      headers = (structure.columns || []).filter(column => column !== 'id');
    } catch (error) {
      console.error('Error loading data structure:', error);
      headers = [];
    }
  }

  async function loadData() {
    if (!model) return;
    
    loading = true;
    try {
      const response = await fetch(`/api/${model.toLowerCase()}`);
      const result = await response.json();
      data = result || [];
    } catch (error) {
      console.error('Error loading data:', error);
      data = [];
    } finally {
      loading = false;
    }
  }
  
  $: if (model) {
    loadDataStructure();
    loadData();
  }
</script>

<div class={tableClasses.wrapper}>
  <!-- New Entry Button -->
  <div class="mb-4 flex justify-start">
    <ModalData datamodel={model} title={`Create new ${model}`} buttonText="New Entry" />
  </div>
  
  {#if loading}
    <div class={tableClasses.states.loading}>Loading...</div>
  {:else if data.length === 0}
    <div class={tableClasses.states.noData}>No data available</div>
  {:else}
    <div class={tableClasses.scrollWrapper}>
      <table class={tableClasses.table}>
        <thead class={tableClasses.header.thead}>
          <tr class={tableClasses.header.tr}>
            {#each headers as header}
              <th class={tableClasses.header.th}>
                {header}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody class={tableClasses.body.tbody}>
          {#each data as row, index}
            <tr class={tableClasses.body.tr}>
              {#each headers as header}
                <td class={tableClasses.body.td}>
                  {row[header] ?? '-'}
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>