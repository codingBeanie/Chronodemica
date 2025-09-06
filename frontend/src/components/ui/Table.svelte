<script lang="ts">
  import ModalData from './ModalData.svelte';
  import Button from './Button.svelte';
  import { API } from '../../lib/api/core';
  
  // Types
  interface TableProps {
    model?: string;
    mode?: 'crud' | 'simple';
    externalData?: any[];
    externalHeaders?: string[];
  }
  
  type SortDirection = 'ascending' | 'descending';
  type ModalType = 'create' | 'edit';
  
  // Props with defaults
  const { 
    model = undefined, 
    mode = 'crud',
    externalData = [],
    externalHeaders = []
  } = $props();
  
  // Component state
  let data = $state<any[]>([]);
  let headers = $state<string[]>([]);
  let loading = $state(false);
  
  // Modal state
  let isModalActive = $state(false);
  let modalType = $state<ModalType>('create');
  let editData = $state<any>(null);
  
  // Sorting state
  let sortColumn = $state<string | null>(null);
  let sortDirection = $state<SortDirection>('ascending');
  
  // Style configuration
  const getStyles = (mode: string) => ({
    // Layout styles
    wrapper: 'w-full',
    scrollWrapper: 'overflow-x-auto w-full',
    table: mode === 'simple' ? 'w-full table-auto' : 'min-w-full table-auto',
    buttonGroup: 'mb-4 flex justify-start',
    actionButtons: 'flex items-center space-x-2',
    
    // Header styles
    thead: 'bg-light-alt',
    thBase: mode === 'simple' 
      ? 'px-3 py-2 text-left text-xs font-medium text-dark uppercase tracking-wider' 
      : 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider whitespace-nowrap',
    thLast: mode === 'simple' 
      ? 'px-3 py-2 text-left text-xs font-medium text-dark uppercase tracking-wider' 
      : 'px-6 py-4 text-left text-xs font-medium text-dark uppercase tracking-wider w-full',
    thActions: 'px-6 py-4 text-right text-xs font-medium text-dark uppercase tracking-wider w-1 whitespace-nowrap',
    headerButton: 'flex items-center justify-start w-full text-left cursor-pointer',
    sortIcon: 'mr-2 text-sm',
    
    // Body styles
    tbody: 'bg-light divide-y divide-light-alt',
    trBody: 'hover:bg-light-alt border-b border-light-alt transition-colors duration-200',
    tdBase: mode === 'simple' 
      ? 'px-3 py-2 text-sm text-dark-alt' 
      : 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt',
    tdLast: mode === 'simple' 
      ? 'px-3 py-2 text-sm text-dark-alt' 
      : 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt w-full',
    tdActions: 'px-6 py-4 whitespace-nowrap text-sm text-dark-alt text-right',
    
    // State styles
    loading: 'text-center py-8 text-dark',
    noData: 'text-center py-8 text-dark',
    
    // Special display styles
    colorWrapper: 'flex items-center space-x-2',
    colorSwatch: 'w-6 h-6 border border-light-alt rounded flex-shrink-0',
    colorText: 'font-mono text-sm text-dark-alt'
  });
  
  const styles = getStyles(mode);
  
  // Utility functions
  const getAlignment = (value: any, header: string): string => 
    typeof value === 'number' || header === '% change' ? 'text-right' : 'text-left';
  
  const getHeaderAlignment = (header: string): string => 
    (data.length > 0 && typeof data[0][header] === 'number') || header === '% change' ? 'text-right' : 'text-left';
  
  const getSortIcon = (column: string): string => {
    if (sortColumn !== column) return 'bi bi-arrow-down-up';
    return sortDirection === 'ascending' ? 'bi bi-arrow-up' : 'bi bi-arrow-down';
  };
  
  const formatHeaderText = (header: string): string => 
    header.replace(/_/g, ' ').toUpperCase();
  
  // Comparison utility for sorting
  const compareValues = (a: any, b: any): number => {
    if (a == null && b == null) return 0;
    if (a == null) return 1;
    if (b == null) return -1;
    
    if (typeof a === 'string' && typeof b === 'string') {
      return a.localeCompare(b);
    }
    if (typeof a === 'number' && typeof b === 'number') {
      return a - b;
    }
    return String(a).localeCompare(String(b));
  };
  
  // Data management
  const loadTableData = async (loadStructure = false) => {
    if (!model) return;
    
    if (loadStructure) {
      const structureResult = await API.getDataStructure(model.toLowerCase());
      if (structureResult.success && structureResult.data?.columns) {
        headers = structureResult.data.columns.filter((column: string) => column !== 'id');
      } else {
        console.error('Error loading data structure:', structureResult.error);
        headers = [];
      }
    }
    
    loading = true;
    const dataResult = await API.getAll(model as any, 0, 100, sortColumn || undefined, sortDirection);
    
    if (dataResult.success && dataResult.data) {
      data = dataResult.data;
    } else {
      console.error('Error loading data:', dataResult.error);
      data = [];
    }
    
    loading = false;
  };
  
  const sortExternalData = (column: string, direction: SortDirection) => {
    data = [...data].sort((a, b) => {
      const comparison = compareValues(a[column], b[column]);
      return direction === 'descending' ? -comparison : comparison;
    });
  };
  
  // Event handlers
  const toggleSort = (column: string) => {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'ascending' ? 'descending' : 'ascending';
    } else {
      sortColumn = column;
      sortDirection = 'ascending';
    }
    
    if (mode === 'simple') {
      sortExternalData(column, sortDirection);
    } else {
      loadTableData();
    }
  };
  
  const handleModal = (action: 'open' | 'close', type?: ModalType, data?: any) => {
    if (action === 'open') {
      modalType = type!;
      editData = data || null;
      isModalActive = true;
    } else {
      isModalActive = false;
      editData = null;
      loadTableData();
    }
  };
  
  const handleDelete = async (row: any) => {
    if (!row.id || !confirm('Are you sure you want to delete this item?')) return;
    
    const result = await API.delete(model as any, row.id);
    if (result.success) {
      loadTableData();
    } else {
      console.error('Error deleting item:', result.error);
    }
  };
  
  // Reactive data initialization
  $effect(() => {
    if (mode === 'simple') {
      // Always update data when externalData changes, even if empty
      data = externalData;
      headers = externalHeaders.length > 0 ? externalHeaders : Object.keys(externalData[0] || {});
      loading = false;
      
      // Reset sorting when data changes
      if (externalData.length === 0) {
        sortColumn = null;
        sortDirection = 'ascending';
      }
    } else if (model && mode === 'crud') {
      loadTableData(true);
    }
  });
</script>

<div class={styles.wrapper}>
  <!-- Action Bar - CRUD mode only -->
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
  
  <!-- Loading state -->
  {#if loading}
    <div class={styles.loading}>Loading...</div>
  
  <!-- Empty state -->
  {:else if data.length === 0}
    <div class={styles.noData}>No data available</div>
  
  <!-- Table content -->
  {:else}
    <div class={styles.scrollWrapper}>
      <table class={styles.table}>
        <!-- Table Header -->
        <thead class={styles.thead}>
          <tr>
            {#each headers as header, index}
              <th class="{index === headers.length - 1 ? styles.thLast : styles.thBase} {getHeaderAlignment(header)}">
                <button
                  onclick={() => toggleSort(header)}
                  class="{styles.headerButton} {getHeaderAlignment(header)} w-full"
                  aria-label="Sort by {formatHeaderText(header)}"
                >
                  <i class="{getSortIcon(header)} {sortColumn === header ? 'text-dark-alt' : 'text-dark'} {styles.sortIcon}"></i>
                  <span>{formatHeaderText(header)}</span>
                </button>
              </th>
            {/each}
            
            {#if mode === 'crud'}
              <th class={styles.thActions}>Actions</th>
            {/if}
          </tr>
        </thead>
        
        <!-- Table Body -->
        <tbody class={styles.tbody}>
          {#each data as row, index (mode === 'simple' ? index : row.id)}
            <tr class={styles.trBody}>
              {#each headers as header, cellIndex}
                <td class="{cellIndex === headers.length - 1 ? styles.tdLast : styles.tdBase} {getAlignment(row[header], header)}">
                  {#if header === 'color' && row[header]}
                    <!-- Special color display -->
                    <div class={styles.colorWrapper}>
                      <div 
                        class={styles.colorSwatch}
                        style="background-color: {row[header]}"
                      ></div>
                      <span class={styles.colorText}>{row[header]}</span>
                    </div>
                  {:else if header === 'party_name' && row.in_government !== undefined}
                    <!-- Party name with government icon -->
                    <div class="flex items-center gap-1">
                      {#if row.in_government}
                        <i class="bi bi-bank2 text-accent" title={row.head_of_government ? "Head of Government" : "In Government"}></i>
                      {/if}
                      {row[header] ?? '-'}
                    </div>
                  {:else}
                    <!-- Regular cell content -->
                    {row[header] ?? '-'}
                  {/if}
                </td>
              {/each}
              
              {#if mode === 'crud'}
                <!-- Action buttons -->
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

  <!-- Modal - CRUD mode only -->
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