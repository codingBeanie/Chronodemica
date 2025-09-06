<script lang="ts">
	import type { PopPeriod, PartyPeriod } from '../../lib/api/core';
	import { API } from '../../lib/api/core';
	import { calculatePopulationRatio } from '../../lib/api/data_services/statistics';
	import Slider from '../ui/Slider.svelte';
	import Input from '../inputs/Input.svelte';
	import Grid from '../ui/Grid.svelte';
	import Button from '../ui/Button.svelte';
	import { getFieldMeta, POP_PERIOD_FIELD_META, PARTY_PERIOD_FIELD_META } from '../../lib/fieldMeta';

	type PeriodData = PopPeriod | PartyPeriod;
	type ApiAction = 'save' | 'delete';
	
	interface Props {
		data: PeriodData;
		objectName: string;
		periodYear: number;
		unsavedChanges?: boolean;
		onAction?: (action: ApiAction, success: boolean) => void;
		previousData?: PeriodData | null;
	}

	let { 
		data = $bindable(), 
		objectName,
		periodYear,
		unsavedChanges = $bindable(false), 
		onAction,
		previousData = null
	}: Props = $props();

	// Internal state
	let originalData = $state<PeriodData | null>(null);
	let popSizeCaption = $state<string>('');

	// Computed values
	let isPopPeriod = $derived('pop_id' in data);
	let dataModelType = $derived(isPopPeriod ? 'PopPeriod' : 'PartyPeriod');
	let fieldMetaObject = $derived(isPopPeriod ? POP_PERIOD_FIELD_META : PARTY_PERIOD_FIELD_META);
	let displayFields = $derived(
		Object.keys(fieldMetaObject)
			.filter(key => data.hasOwnProperty(key))
			.map(key => ({ key, meta: getFieldMeta(key, dataModelType)! }))
	);
	let saveDisabled = $derived(!unsavedChanges);

	// Utility functions
	function formatFieldName(key: string): string {
		return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
	}

	function deepClone<T>(obj: T): T {
		return JSON.parse(JSON.stringify(obj));
	}

	function getPreviousValue(fieldKey: string): string | undefined {
		if (!previousData || !(fieldKey in previousData)) return undefined;
		const prevValue = (previousData as any)[fieldKey];
		if (prevValue === null || prevValue === undefined) return undefined;
		return `prev.: ${prevValue.toString()}`;
	}

	function getCombinedCaption(fieldKey: string): string | undefined {
		const fieldMeta = getFieldMeta(fieldKey, dataModelType);
		if (fieldMeta?.showRatio && popSizeCaption) {
			const prevValue = getPreviousValue(fieldKey);
			return prevValue ? `${popSizeCaption} | ${prevValue}` : popSizeCaption;
		}
		return getPreviousValue(fieldKey);
	}

	// Change tracking
	let lastDataId = $state<number | undefined>(undefined);
	
	$effect(() => {
		if (data && (!originalData || data.id !== lastDataId)) {
			originalData = deepClone(data);
			lastDataId = data.id;
		}
	});

	$effect(() => {
		unsavedChanges = originalData ? JSON.stringify(data) !== JSON.stringify(originalData) : false;
	});

	// Update population ratio caption for PopPeriod
	$effect(() => {
		if (isPopPeriod && data.period_id && data.id && typeof (data as PopPeriod).pop_size === 'number') {
			calculatePopulationRatio((data as PopPeriod).pop_size!, data.period_id, data.id!)
				.then(ratio => {
					popSizeCaption = ratio;
				})
				.catch(() => {
					popSizeCaption = '';
				});
		}
	});

	function resetChangeTracking(): void {
		originalData = deepClone(data);
		unsavedChanges = false;
	}

	// API operations
	async function performApiAction(action: ApiAction): Promise<void> {
		if (!data.id) {
			console.error(`Cannot ${action} data without ID`);
			return;
		}

		if (action === 'delete' && !confirm('Are you sure you want to delete this data? This action cannot be undone.')) {
			return;
		}

		try {
			let result;
			if (action === 'save') {
				result = await API.update(dataModelType as any, data.id, data);
			} else {
				result = await API.delete(dataModelType as any, data.id);
			}
			
			if (result.success) {
				if (action === 'save') {
					if (result.data) Object.assign(data, result.data);
					resetChangeTracking();
				} else {
					data = null as any;
					originalData = null;
					unsavedChanges = false;
				}
				console.log(`Data ${action}d successfully`);
				onAction?.(action, true);
			} else {
				console.error(`Failed to ${action} data:`, result.error);
				onAction?.(action, false);
			}
		} catch (error) {
			console.error(`Error ${action}ing data:`, error);
			onAction?.(action, false);
		}
	}

	const handleSave = () => performApiAction('save');
	const handleDelete = () => performApiAction('delete');
</script>

<div class="mt-8">
	<!-- PARAMETERS: Field controls -->
	<Grid cols="1fr 1fr" gap="gap-4">
	{#each displayFields as field}
		{#if field.meta.type === 'input'}
			<Input
				id="{dataModelType}-{field.key}"
				label={formatFieldName(field.key)}
				bind:value={(data as any)[field.key]}
				type="number"
				hint={field.meta.hint}
				caption={getPreviousValue(field.key)}
			/>
		{:else}
			<Slider
				id="{dataModelType}-{field.key}"
				title={formatFieldName(field.key)}
				bind:value={(data as any)[field.key]}
				min={field.meta.min}
				max={field.meta.max}
				step={field.meta.step || 1}
				hint={field.meta.hint}
				caption={getCombinedCaption(field.key)}
			/>
		{/if}
	{/each}
	</Grid>
	
	<!-- FOOTER: Delete button -->
	<div class="flex justify-end items-center gap-4 mt-6">
		{#if unsavedChanges}
			<span class="text-lg text-accent font-medium">Unsaved changes detected. Don't forget to save.</span>
		{/if}
		<Button 
			text="Delete" 
			theme="light"
			disabled={!data.id}
			onclick={handleDelete}
		/>
		<Button 
		text="Save" 
		theme="accent"
		disabled={saveDisabled}
		onclick={handleSave}
	/>
	</div>
</div>