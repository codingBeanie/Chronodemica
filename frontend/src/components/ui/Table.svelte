<script lang="ts">
  import ModalData from './ModalData.svelte';
  import Button from './Button.svelte';
  import { API } from '../../api/api';
  
  // Svelte 5 runes
  const { model, mode = 'crud' } = $props<{ 
    model: string;
    mode?: 'crud' | 'simple';
  }>();
  
  let data = $state<any[]>([]);
  let headers = $state<string[]>([]);
  let loading = $state(false);
  
  // Modal state management
  let isModalActive = $state(false);
  let modalType = $state<'create' | 'edit'>('create');
  let editData = $state<any>(null);
  
  // Sorting state management
  let sortColumn = $state<string | null>(null);
  let sortDirection = $state<'ascending' | 'descending'>('ascending');
  
  // Local table styles
  const styles = {
    wrapper: 'w-full',
    scrollWrapper: 'overflow-x-auto',
    table: 'min-w-full table-auto',
    
    header: {
      thead: 'bg-light-alt',
      tr: 'bg-light-alt',
      th: 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider whitespace-nowrap',
      thLast: 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider w-full',
      thActions: 'px-6 py-4 text-right text-xs font-medium text-dark uppercase tracking-wider w-1 whitespace-nowrap'
    },
    
    body: {
      tbody: 'bg-light divide-y divide-light-alt',
      tr: 'hover:bg-light-alt transition-colors duration-200',
      td: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt',
      tdLast: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt w-full',
      tdActions: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt text-right'
    },
    
    states: {
      loading: 'text-center py-8 text-dark',
      noData: 'text-center py-8 text-dark'
    }
  };

  const colorStyles = {
    wrapper: 'flex items-center space-x-2',
    swatch: 'w-6 h-6 border border-light-alt rounded flex-shrink-0',
    text: 'font-mono text-sm text-dark-alt'
  };

  const layoutStyles = {
    buttonGroup: 'mb-4 flex justify-start',
    actionButtons: 'flex items-center space-x-2'
  };
  
  // Load data structure for table headers
  async function loadDataStructure() {
    if (!model) return;
    
    const result = await API.getDataStructure(model.toLowerCase());
    if (result.success && result.data?.columns) {
      headers = result.data.columns.filter((column: string) => column !== 'id');
    } else {
      console.error('Error loading data structure:', result.error);
      headers = [];
    }
  }

  // Load table data
  async function loadData() {
    if (!model) return;
    
    loading = true;
    const result = await API.getAll(model as any, 0, 100, sortColumn || undefined, sortDirection);
    
    if (result.success && result.data) {
      data = result.data;
    } else {
      console.error('Error loading data:', result.error);
      data = [];
    }
    
    loading = false;
  }

  // Handle successful data creation/update
  function handleDataChanged() {
    isModalActive = false; // Close modal
    editData = null; // Clear edit data
    loadData();
  }

  // Open modal with type and optional data
  function openModal(type: 'create' | 'edit', data: any = null) {
    modalType = type;
    editData = data;
    isModalActive = true;
  }

  // Handle delete action
  async function handleDelete(row: any) {
    if (!row.id || !confirm('Are you sure you want to delete this item?')) return;
    
    const result = await API.delete(model as any, row.id);
    if (result.success) {
      loadData();
    } else {
      console.error('Error deleting item:', result.error);
    }
  }

  // Handle sorting toggle
  function toggleSort(column: string) {
    if (sortColumn === column) {
      // Same column clicked - toggle direction
      sortDirection = sortDirection === 'ascending' ? 'descending' : 'ascending';
    } else {
      // Different column clicked - set new column and default to ascending
      sortColumn = column;
      sortDirection = 'ascending';
    }
    
    console.log('Sorting column:', column, 'Direction:', sortDirection);
    // Reload data with new sorting
    loadData();
  }
  
  // Get sort icon for a column
  function getSortIcon(column: string): string {
    if (sortColumn !== column) {
      return 'bi bi-arrow-down-up'; // Default unsorted icon
    }
    return sortDirection === 'ascending' ? 'bi bi-arrow-up' : 'bi bi-arrow-down';
  }

  // Reactive effect to load data when model changes
  $effect(() => {
    if (model) {
      loadDataStructure();
      loadData();
    }
  });
</script>

<div class={styles.wrapper}>
  <!-- Action Bar - only show in CRUD mode -->
  {#if mode === 'crud'}
    <div class={layoutStyles.buttonGroup}>
      <Button 
        text="New Entry" 
        type="text" 
        theme="accent" 
        onclick={() => openModal('create')} 
      />
    </div>
  {/if}
  
  {#if loading}
    <div class={styles.states.loading}>
      Loading...
    </div>
  {:else if data.length === 0}
    <div class={styles.states.noData}>
      No data available
    </div>
  {:else}
    <div class={styles.scrollWrapper}>
      <table class={styles.table}>
        <!-- Table Header -->
        <thead class={styles.header.thead}>
          <tr class={styles.header.tr}>
            {#each headers as header, index}
              <th class={index === headers.length - 1 ? styles.header.thLast : styles.header.th}>
                <div class="flex items-center justify-between">
                  <span>{header.replace(/_/g, ' ')}</span>
                  <button
                    onclick={() => toggleSort(header)}
                    class="ml-2 p-1 hover:bg-gray-200 rounded transition-colors"
                  >
                    <i class="{getSortIcon(header)} {sortColumn === header ? 'text-blue-600' : 'text-gray-500'} text-sm"></i>
                  </button>
                </div>
              </th>
            {/each}
            {#if mode === 'crud'}
              <th class={styles.header.thActions}>
                Actions
              </th>
            {/if}
          </tr>
        </thead>
        
        <!-- Table Body -->
        <tbody class={styles.body.tbody}>
          {#each data as row (row.id)}
            <tr class={styles.body.tr}>
              {#each headers as header, index}
                <td class={index === headers.length - 1 ? styles.body.tdLast : styles.body.td}>
                  {#if header === 'color' && row[header]}
                    <div class={colorStyles.wrapper}>
                      <div 
                        class={colorStyles.swatch}
                        style="background-color: {row[header]}"
                      ></div>
                      <span class={colorStyles.text}>{row[header]}</span>
                    </div>
                  {:else}
                    {row[header] ?? '-'}
                  {/if}
                </td>
              {/each}
              {#if mode === 'crud'}
                <td class={styles.body.tdActions}>
                  <div class={layoutStyles.actionButtons}>
                    <Button 
                      icon="bi bi-pencil-square"
                      type="icon"
                      theme="light" 
                      onclick={() => openModal('edit', row)} 
                    />
                    <Button 
                      icon="bi bi-trash3"
                      type="icon"
                      theme="light" 
                      onclick={() => handleDelete(row)} 
                    />
                  </div>
                </td>
              {/if}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

  <!-- Single Modal for both Create and Edit - only in CRUD mode -->
  {#if mode === 'crud'}
    <ModalData 
      active={isModalActive}
      datamodel={model}
      type={modalType}
      editData={editData}
      onSuccess={handleDataChanged}
    />
  {/if}
</div>