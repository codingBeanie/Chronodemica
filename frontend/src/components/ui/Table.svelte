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
  
  // Configuration
  const TABLE_CONFIG = {
    SPECIAL_COLUMNS: {
      PERCENTAGE_CHANGE: '% change',
      PERCENTAGE: 'percentage',
      COLOR: 'color'
    },
    SPECIAL_PARTY_FIELDS: {
      IN_GOVERNMENT: 'in_government'
    },
    DEFAULT_PARTY_COLOR: '#525252',
    ICONS: {
      SORT_NEUTRAL: 'bi bi-arrow-down-up',
      SORT_ASC: 'bi bi-arrow-up', 
      SORT_DESC: 'bi bi-arrow-down',
      GOVERNMENT: 'bi bi-bank2',
      EDIT: 'bi bi-pencil-square',
      DELETE: 'bi bi-trash3'
    }
  };

  // Style configuration
  const STYLE_CONFIG = {
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
  };

  // Computed values
  let hasData = $derived(data.length > 0);
  let isSimpleMode = $derived(mode === 'simple');
  let isCrudMode = $derived(mode === 'crud');
  let tableClasses = $derived(getTableClasses());

  // Utility functions
  function getAlignment(value: any, header: string): string {
    return typeof value === 'number' || header === TABLE_CONFIG.SPECIAL_COLUMNS.PERCENTAGE_CHANGE || header === TABLE_CONFIG.SPECIAL_COLUMNS.PERCENTAGE
      ? 'text-right' 
      : 'text-left';
  }
  
  function getHeaderAlignment(header: string): string {
    return (hasData && typeof data[0][header] === 'number') || header === TABLE_CONFIG.SPECIAL_COLUMNS.PERCENTAGE_CHANGE || header === TABLE_CONFIG.SPECIAL_COLUMNS.PERCENTAGE
      ? 'text-right' 
      : 'text-left';
  }
  
  function getSortIcon(column: string): string {
    if (sortColumn !== column) return TABLE_CONFIG.ICONS.SORT_NEUTRAL;
    return sortDirection === 'ascending' 
      ? TABLE_CONFIG.ICONS.SORT_ASC 
      : TABLE_CONFIG.ICONS.SORT_DESC;
  }
  
  function formatHeaderText(header: string): string {
    return header.replace(/_/g, ' ').toUpperCase();
  }
  
  // Comparison utility for sorting
  function compareValues(a: any, b: any): number {
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
  }
  
  // Data management
  async function loadTableData(loadStructure = false) {
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
  }
  
  function sortExternalData(column: string, direction: SortDirection) {
    data = [...data].sort((a, b) => {
      const comparison = compareValues(a[column], b[column]);
      return direction === 'descending' ? -comparison : comparison;
    });
  }
  
  // Event handlers
  function toggleSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'ascending' ? 'descending' : 'ascending';
    } else {
      sortColumn = column;
      sortDirection = 'ascending';
    }
    
    if (isSimpleMode) {
      sortExternalData(column, sortDirection);
    } else {
      loadTableData();
    }
  }
  
  function handleModal(action: 'open' | 'close', type?: ModalType, modalData?: any) {
    if (action === 'open') {
      modalType = type!;
      editData = modalData || null;
      isModalActive = true;
    } else {
      isModalActive = false;
      editData = null;
      loadTableData();
    }
  }
  
  async function handleDelete(row: any) {
    if (!row.id || !confirm('Are you sure you want to delete this item?')) return;
    
    const result = await API.delete(model as any, row.id);
    if (result.success) {
      loadTableData();
    } else {
      console.error('Error deleting item:', result.error);
    }
  }

  // Cell rendering functions
  function renderColorCell(value: string) {
    return {
      wrapper: STYLE_CONFIG.colorWrapper,
      swatch: STYLE_CONFIG.colorSwatch,
      text: STYLE_CONFIG.colorText,
      value: value
    };
  }

  function renderPartyCell(row: any, header: string) {
    const hasGovernmentStatus = row[TABLE_CONFIG.SPECIAL_PARTY_FIELDS.IN_GOVERNMENT] !== undefined;
    const isInGovernment = row[TABLE_CONFIG.SPECIAL_PARTY_FIELDS.IN_GOVERNMENT];
    const isHeadOfGovernment = row.head_of_government;
    
    return {
      hasIcon: hasGovernmentStatus && isInGovernment,
      iconClass: TABLE_CONFIG.ICONS.GOVERNMENT,
      iconTitle: isHeadOfGovernment ? "Head of Government" : "In Government",
      value: row[header] ?? '-'
    };
  }

  function getTableClasses() {
    return {
      wrapper: STYLE_CONFIG.wrapper,
      scrollWrapper: STYLE_CONFIG.scrollWrapper,
      table: STYLE_CONFIG.table,
      buttonGroup: STYLE_CONFIG.buttonGroup
    };
  }

  function getHeaderClasses(index: number, isLast: boolean) {
    const baseClass = isLast ? STYLE_CONFIG.thLast : STYLE_CONFIG.thBase;
    const alignmentClass = getHeaderAlignment(headers[index]);
    return `${baseClass} ${alignmentClass}`;
  }

  function getCellClasses(index: number, isLast: boolean, value: any, header: string) {
    const baseClass = isLast ? STYLE_CONFIG.tdLast : STYLE_CONFIG.tdBase;
    const alignmentClass = getAlignment(value, header);
    return `${baseClass} ${alignmentClass}`;
  }
  
  // Reactive data initialization
  $effect(() => {
    if (isSimpleMode) {
      data = externalData;
      headers = externalHeaders.length > 0 ? externalHeaders : Object.keys(externalData[0] || {});
      loading = false;
      
      // Reset sorting when data changes
      if (externalData.length === 0) {
        sortColumn = null;
        sortDirection = 'ascending';
      }
    } else if (model && isCrudMode) {
      loadTableData(true);
    }
  });
</script>

<div class={tableClasses.wrapper}>
  <!-- Action Bar - CRUD mode only -->
  {#if isCrudMode}
    <div class={tableClasses.buttonGroup}>
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
    <div class={STYLE_CONFIG.loading}>Loading...</div>
  
  <!-- Empty state -->
  {:else if !hasData}
    <div class={STYLE_CONFIG.noData}>No data available</div>
  
  <!-- Table content -->
  {:else}
    <div class={tableClasses.scrollWrapper}>
      <table class={tableClasses.table}>
        <!-- Table Header -->
        <thead class={STYLE_CONFIG.thead}>
          <tr>
            {#each headers as header, index}
              {@const isLast = index === headers.length - 1}
              <th class={getHeaderClasses(index, isLast)}>
                <button
                  onclick={() => toggleSort(header)}
                  class="{STYLE_CONFIG.headerButton} {getHeaderAlignment(header)} w-full"
                  aria-label="Sort by {formatHeaderText(header)}"
                >
                  <i class="{getSortIcon(header)} {sortColumn === header ? 'text-dark-alt' : 'text-dark'} {STYLE_CONFIG.sortIcon}"></i>
                  <span>{formatHeaderText(header)}</span>
                </button>
              </th>
            {/each}
            
            {#if isCrudMode}
              <th class={STYLE_CONFIG.thActions}>Actions</th>
            {/if}
          </tr>
        </thead>
        
        <!-- Table Body -->
        <tbody class={STYLE_CONFIG.tbody}>
          {#each data as row, index (isSimpleMode ? index : row.id)}
            <tr class={STYLE_CONFIG.trBody}>
              {#each headers as header, cellIndex}
                {@const isLast = cellIndex === headers.length - 1}
                <td class={getCellClasses(cellIndex, isLast, row[header], header)}>
                  {#if header === TABLE_CONFIG.SPECIAL_COLUMNS.COLOR && row[header]}
                    {@const colorData = renderColorCell(row[header])}
                    <div class={colorData.wrapper}>
                      <div 
                        class={colorData.swatch}
                        style="background-color: {colorData.value}"
                      ></div>
                      <span class={colorData.text}>{colorData.value}</span>
                    </div>
                  {:else if header === 'party_name' && row[TABLE_CONFIG.SPECIAL_PARTY_FIELDS.IN_GOVERNMENT] !== undefined}
                    {@const partyData = renderPartyCell(row, header)}
                    <div class="flex items-center gap-1">
                      {#if partyData.hasIcon}
                        <i class="{partyData.iconClass} text-accent" title={partyData.iconTitle}></i>
                      {/if}
                      {partyData.value}
                    </div>
                  {:else}
                    {row[header] ?? '-'}
                  {/if}
                </td>
              {/each}
              
              {#if isCrudMode}
                <td class={STYLE_CONFIG.tdActions}>
                  <div class={STYLE_CONFIG.actionButtons}>
                    <Button 
                      icon={TABLE_CONFIG.ICONS.EDIT}
                      type="icon"
                      theme="light" 
                      onclick={() => handleModal('open', 'edit', row)} 
                    />
                    <Button 
                      icon={TABLE_CONFIG.ICONS.DELETE}
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
  {#if isCrudMode}
    <ModalData 
      active={isModalActive}
      datamodel={model}
      type={modalType}
      editData={editData}
      onSuccess={() => handleModal('close')}
    />
  {/if}
</div>