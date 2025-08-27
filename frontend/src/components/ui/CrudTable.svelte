<script>
  export let model = '';
  
  let data = [];
  let headers = [];
  let loading = false;
  
  async function loadData() {
    if (!model) return;
    
    loading = true;
    try {
      const response = await fetch(`/api/${model.toLowerCase()}s`);
      const result = await response.json();
      
      if (result.length > 0) {
        data = result;
        headers = Object.keys(result[0]);
      } else {
        data = [];
        headers = [];
      }
    } catch (error) {
      console.error('Error loading data:', error);
      data = [];
      headers = [];
    } finally {
      loading = false;
    }
  }
  
  $: if (model) {
    loadData();
  }
</script>

<div class="w-full">
  <h2 class="text-xl font-semibold mb-4">{model} Table</h2>
  
  {#if loading}
    <div class="text-center py-4">Loading...</div>
  {:else if data.length === 0}
    <div class="text-center py-4 text-gray-500">No data available</div>
  {:else}
    <div class="overflow-x-auto">
      <table class="min-w-full bg-white border border-gray-200 rounded-lg">
        <thead class="bg-gray-50">
          <tr>
            {#each headers as header}
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">
                {header}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          {#each data as row, index}
            <tr class="hover:bg-gray-50">
              {#each headers as header}
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
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