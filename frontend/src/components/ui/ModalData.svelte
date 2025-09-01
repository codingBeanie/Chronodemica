<script lang="ts">
  import Button from './Button.svelte';
  import Input from '../inputs/Input.svelte';
  import ColorPicker from '../inputs/ColorPicker.svelte';
  import { API } from '../../api/api';
  import { COMPONENT_STYLES } from '../../styles/component-classes.js';
  
  interface Props {
    active: boolean;
    datamodel: string;
    type: 'create' | 'edit';
    title?: string;
    editData?: any;
    onSuccess?: () => void;
  }
  
  interface FieldInfo {
    type: string;
    required: boolean;
    default: any;
  }
  
  interface SchemaData {
    model?: string;
    table_name?: string;
    columns?: string[];
    fields?: Record<string, FieldInfo>;
    error?: string;
  }
  
  let {
    active,
    datamodel,
    type,
    title = type === 'edit' ? `Edit ${datamodel}` : `New ${datamodel}`,
    editData,
    onSuccess
  }: Props = $props();
  
  let schemaData: SchemaData | null = $state(null);
  let formData: Record<string, any> = $state({});
  let fieldErrors: Record<string, string> = $state({});
  let apiError: string = $state('');
  
  const modalStyles = COMPONENT_STYLES.modal;
  
  async function loadSchema() {
    console.log('Loading schema for:', datamodel);
    const result = await API.getDataStructure(datamodel);
    
    if (result.success && result.data) {
      console.log('Schema data loaded:', result.data);
      schemaData = result.data;
      
      // Initialize formData with default values or edit data
      if (result.data.fields) {
        const initialFormData: Record<string, any> = {};
        for (const [fieldName, fieldInfo] of Object.entries(result.data.fields)) {
          const typedFieldInfo = fieldInfo as FieldInfo;
          // Use editData if available, otherwise use default values
          initialFormData[fieldName] = (type === 'edit' && editData && editData[fieldName] !== undefined) 
            ? editData[fieldName] 
            : (typedFieldInfo.default || '');
        }
        formData = initialFormData;
      }
    } else {
      console.error('Failed to load schema:', result.error);
      schemaData = { error: result.error || 'Failed to load schema' };
    }
  }
  

  function isValidHexColor(color: string): boolean {
    // Check if it's a valid hex color format: #RRGGBB or #RGB
    const hexColorRegex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/;
    return hexColorRegex.test(color);
  }

  function validateForm(): boolean {
    if (!schemaData?.fields) return false;
    
    fieldErrors = {};
    let isValid = true;
    
    for (const [fieldName, fieldInfo] of Object.entries(schemaData.fields)) {
      if (fieldName === 'id') continue; // Skip id field
      
      const typedFieldInfo = fieldInfo as FieldInfo;
      const value = formData[fieldName];
      
      // Check required fields
      if (typedFieldInfo.required) {
        if (!value || (typeof value === 'string' && value.trim() === '')) {
          fieldErrors[fieldName] = 'This field is required';
          isValid = false;
          continue; // Skip other validations for this field
        }
      }
      
      // Check color field format
      if (fieldName === 'color' && value && typeof value === 'string') {
        if (!isValidHexColor(value.trim())) {
          fieldErrors[fieldName] = 'Please enter a valid hex color format (e.g., #FF0000 or #F00)';
          isValid = false;
        }
      }
    }
    
    return isValid;
  }
  
  
  async function handleSave() {
    apiError = ''; // Clear previous API errors
    
    if (validateForm()) {
      if (type === 'create') {
        console.log('Creating new entry:', formData);
        
        const result = await API.create(datamodel as any, formData);
        
        if (result.success) {
          console.log('Entry created successfully');
          if (onSuccess) {
            onSuccess();
          }
        } else {
          apiError = result.error || 'Failed to create entry';
        }
      } else if (type === 'edit' && editData?.id) {
        console.log('Updating entry:', formData);
        
        const result = await API.update(datamodel as any, editData.id, formData);
        
        if (result.success) {
          console.log('Entry updated successfully');
          if (onSuccess) {
            onSuccess();
          }
        } else {
          apiError = result.error || 'Failed to update entry';
        }
      }
    }
  }
  
  function handleCancel() {
    // Let parent component handle closing
    if (onSuccess) onSuccess();
  }
  
  function handleClickOutside() {
    // Let parent component handle closing
    if (onSuccess) onSuccess();
  }

  // Load schema when modal becomes active
  $effect(() => {
    if (active) {
      fieldErrors = {}; // Clear previous errors
      apiError = ''; // Clear previous API errors
      if (!schemaData) {
        loadSchema();
      } else if (schemaData.fields) {
        // Re-initialize formData when modal opens (for edit mode data)
        const initialFormData: Record<string, any> = {};
        for (const [fieldName, fieldInfo] of Object.entries(schemaData.fields)) {
          const typedFieldInfo = fieldInfo as FieldInfo;
          initialFormData[fieldName] = (type === 'edit' && editData && editData[fieldName] !== undefined) 
            ? editData[fieldName] 
            : (typedFieldInfo.default || '');
        }
        formData = initialFormData;
      }
    }
  });
</script>

{#if active}
  <div 
    class={modalStyles.overlay}
    style="background-color: {modalStyles.backdrop};"
    onclick={handleClickOutside}
    onkeydown={(e) => e.key === 'Escape' && handleClickOutside()}
    role="button"
    tabindex="0"
  >
    <div 
      class={modalStyles.container}
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      tabindex="-1"
    >
      <!-- Modal header -->
      <div class={modalStyles.header}>
        <h2 class={modalStyles.title}>
          {title}
        </h2>
      </div>
      
      <!-- Modal content -->
      <div class={modalStyles.content}>
        {#if schemaData === null}
          <div class={modalStyles.loading}>
            Loading schema...
          </div>
        {:else if schemaData.error}
          <div class={modalStyles.loading}>
            <span class={modalStyles.apiError}>{schemaData.error}</span>
          </div>
        {:else if schemaData.fields}
          <form class={modalStyles.form}>
            {#each Object.entries(schemaData.fields) as [fieldName, fieldInfo]}
              {#if fieldName !== 'id'}
                <div class={modalStyles.field}>
                  {#if fieldName === 'color'}
                    <ColorPicker 
                      id={`${datamodel}-${fieldName}`}
                      label={fieldName.replace(/_/g, ' ')}
                      bind:value={formData[fieldName]}
                      required={fieldInfo.required}
                    />
                  {:else if fieldInfo.type.includes('str')}
                    <Input 
                      id={`${datamodel}-${fieldName}`}
                      label={fieldName.replace(/_/g, ' ')}
                      type="text"
                      bind:value={formData[fieldName]}
                      required={fieldInfo.required}
                      placeholder={fieldInfo.default !== null ? String(fieldInfo.default) : ''}
                    />
                  {:else if fieldInfo.type.includes('int')}
                    <Input 
                      id={`${datamodel}-${fieldName}`}
                      label={fieldName.replace(/_/g, ' ')}
                      type="number"
                      bind:value={formData[fieldName]}
                      required={fieldInfo.required}
                      placeholder={fieldInfo.default !== null ? String(fieldInfo.default) : ''}
                    />
                  {:else}
                    <div class="border border-light-alt rounded p-3 bg-light-bg">
                      <div class="font-semibold text-dark mb-2">{fieldName.replace(/_/g, ' ')}</div>
                      <div class="space-y-1 text-sm">
                        <div><span class="font-medium text-dark-text">Type:</span> <span class="text-light-text font-mono">{fieldInfo.type}</span></div>
                        <div><span class="font-medium text-dark-text">Required:</span> <span class="text-light-text">{fieldInfo.required ? 'Yes' : 'No'}</span></div>
                        <div><span class="font-medium text-dark-text">Default:</span> <span class="text-light-text font-mono">{fieldInfo.default !== null ? fieldInfo.default : 'None'}</span></div>
                      </div>
                    </div>
                  {/if}
                  
                  {#if fieldErrors[fieldName]}
                    <div class={modalStyles.error}>
                      {fieldErrors[fieldName]}
                    </div>
                  {/if}
                </div>
              {/if}
            {/each}
          </form>
        {:else}
          <div class="text-light-text p-4 bg-light-bg rounded">
            <pre>{JSON.stringify(schemaData, null, 2)}</pre>
          </div>
        {/if}
      </div>
      
      <!-- Modal footer -->
      <div class={modalStyles.footer}>
        <div class="flex-1">
          {#if apiError}
            <div class={modalStyles.apiError}>
              {apiError}
            </div>
          {/if}
        </div>
        <div class="flex space-x-3">
          <Button text="Cancel" type="text" theme="light" onclick={handleCancel} />
          <Button text="Save" type="text" theme="accent" onclick={handleSave} />
        </div>
      </div>
    </div>
  </div>
{/if}