<script lang="ts">
  import ModalData from './ModalData.svelte';
  import Button from './Button.svelte';
  import { API } from '../../api/api';
  import { COMPONENT_STYLES } from '../../styles/component-classes.js';
  
  // Svelte 5 runes
  const { model } = $props<{ model: string }>();
  
  let data = $state<any[]>([]);
  let headers = $state<string[]>([]);
  let loading = $state(false);
  
  // Modal state management
  let isModalActive = $state(false);
  let modalType = $state<'create' | 'edit'>('create');
  let editData = $state<any>(null);
  
  const styles = COMPONENT_STYLES.table;
  const colorStyles = COMPONENT_STYLES.colorDisplay;
  const layoutStyles = COMPONENT_STYLES.layout;
  
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
    const result = await API.getAll(model as any);
    
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

  // Reactive effect to load data when model changes
  $effect(() => {
    if (model) {
      loadDataStructure();
      loadData();
    }
  });
</script>

<div class={styles.wrapper}>
  <!-- Action Bar -->
  <div class={COMPONENT_STYLES.layout.buttonGroup}>
    <Button 
      text="New Entry" 
      type="text" 
      theme="accent" 
      onclick={() => openModal('create')} 
    />
  </div>
  
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
                {header.replace(/_/g, ' ')}
              </th>
            {/each}
            <th class={styles.header.thActions}>
              Actions
            </th>
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
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

  <!-- Single Modal for both Create and Edit -->
  <ModalData 
    active={isModalActive}
    datamodel={model}
    type={modalType}
    editData={editData}
    onSuccess={handleDataChanged}
  />
</div>