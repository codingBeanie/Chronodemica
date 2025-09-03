<script lang="ts">
  import ModalData from './ModalData.svelte';
  import Button from './Button.svelte';
  import { API } from '../../lib/api/api';
  
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
  
  // Consolidated styles configuration
  const styles = {
    wrapper: 'w-full',
    scrollWrapper: 'overflow-x-auto',
    table: 'min-w-full table-auto',
    
    // Header styles
    thead: 'bg-light-alt',
    thBase: 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider whitespace-nowrap',
    thLast: 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider w-full',
    thActions: 'px-6 py-4 text-right text-xs font-medium text-dark uppercase tracking-wider w-1 whitespace-nowrap',
    
    // Body styles
    tbody: 'bg-light divide-y divide-light-alt',
    trBody: 'hover:bg-light-alt border-b border-light-alt transition-colors duration-200',
    tdBase: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt',
    tdLast: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt w-full',
    tdActions: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt text-right',
    
    // State styles
    loading: 'text-center py-8 text-dark',
    noData: 'text-center py-8 text-dark',
    
    // Color display styles
    colorWrapper: 'flex items-center space-x-2',
    colorSwatch: 'w-6 h-6 border border-light-alt rounded flex-shrink-0',
    colorText: 'font-mono text-sm text-dark-alt',
    
    // Layout styles
    buttonGroup: 'mb-4 flex justify-start',
    actionButtons: 'flex items-center space-x-2',
    headerButton: 'flex items-center justify-start w-full text-left cursor-pointer',
    sortIcon: 'mr-2 text-sm'
  };
  
  // Unified data loading function
  async function loadTableData(loadStructure = false) {
    if (!model) return;
    
    // Load data structure if needed
    if (loadStructure) {
      const structureResult = await API.getDataStructure(model.toLowerCase());
      if (structureResult.success && structureResult.data?.columns) {
        headers = structureResult.data.columns.filter((column: string) => column !== 'id');
      } else {
        console.error('Error loading data structure:', structureResult.error);
        headers = [];
      }
    }
    
    // Load table data
    loading = true;
    const dataResult = await API.getAll(model as any, 0, 100, sortColumn || undefined, sortDirection);
    
    if (dataResult.success && dataResult.data) {
      data = dataResult.data;
    } else {
      console.error('Error loading data:', dataResult.error);
      data = [];
    }
    
    loading = false;
  }

  // Consolidated modal management
  function handleModal(action: 'open' | 'close', type?: 'create' | 'edit', data?: any) {
    if (action === 'open') {
      modalType = type!;
      editData = data || null;
      isModalActive = true;
    } else {
      isModalActive = false;
      editData = null;
      loadTableData();
    }
  }

  // Handle delete action
  async function handleDelete(row: any) {
    if (!row.id || !confirm('Are you sure you want to delete this item?')) return;
    
    const result = await API.delete(model as any, row.id);
    if (result.success) {
      loadTableData();
    } else {
      console.error('Error deleting item:', result.error);
    }
  }

  // Handle sorting toggle
  function toggleSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'ascending' ? 'descending' : 'ascending';
    } else {
      sortColumn = column;
      sortDirection = 'ascending';
    }
    
    loadTableData();
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
      loadTableData(true);
    }
  });
</script>

<div class={styles.wrapper}>
  <!-- Action Bar - only show in CRUD mode -->
  {#if mode === 'crud'}
    <div class={styles.buttonGroup}>
      <Button 
        text="New Entry" 
        type="text" 
        theme="accent" 
        onclick={() => handleModal('open', 'create')} 
      />
    </div>
  {/if}
  
  {#if loading}
    <div class={styles.loading}>
      Loading...
    </div>
  {:else if data.length === 0}
    <div class={styles.noData}>
      No data available
    </div>
  {:else}
    <div class={styles.scrollWrapper}>
      <table class={styles.table}>
        <!-- Table Header -->
        <thead class={styles.thead}>
          <tr>
            {#each headers as header, index}
              <th class={index === headers.length - 1 ? styles.thLast : styles.thBase}>
                <button
                  onclick={() => toggleSort(header)}
                  class={styles.headerButton}
                  aria-label="Sort by {header.replace(/_/g, ' ')}"
                >
                  <i class="{getSortIcon(header)} {sortColumn === header ? 'text-dark-alt' : 'text-dark'} {styles.sortIcon}"></i>
                  <span class="uppercase">{header.replace(/_/g, ' ')}</span>
                </button>
              </th>
            {/each}
            {#if mode === 'crud'}
              <th class={styles.thActions}>
                Actions
              </th>
            {/if}
          </tr>
        </thead>
        
        <!-- Table Body -->
        <tbody class={styles.tbody}>
          {#each data as row (row.id)}
            <tr class={styles.trBody}>
              {#each headers as header, index}
                <td class={index === headers.length - 1 ? styles.tdLast : styles.tdBase}>
                  {#if header === 'color' && row[header]}
                    <div class={styles.colorWrapper}>
                      <div 
                        class={styles.colorSwatch}
                        style="background-color: {row[header]}"
                      ></div>
                      <span class={styles.colorText}>{row[header]}</span>
                    </div>
                  {:else}
                    {row[header] ?? '-'}
                  {/if}
                </td>
              {/each}
              {#if mode === 'crud'}
                <td class={styles.tdActions}>
                  <div class={styles.actionButtons}>
                    <Button 
                      icon="bi bi-pencil-square"
                      type="icon"
                      theme="light" 
                      onclick={() => handleModal('open', 'edit', row)} 
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
      onSuccess={() => handleModal('close')}
    />
  {/if}
</div>