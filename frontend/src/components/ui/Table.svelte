<script lang="ts">
	import { onMount } from 'svelte';
	import { getAll } from '../../api/api';
	
	interface Props {
		model: 'Period' | 'Pop' | 'Party' | 'PopPeriod' | 'PartyPeriod' | 'PopVote' | 'ElectionResult';
	}
	
	let { model }: Props = $props();
	
	let data: Array<Record<string, any>> = $state([]);
	let loading = $state(true);
	let error = $state('');
	
	// Extract column names from the first row of data
	const tableColumns = $derived(() => {
		if (data.length === 0) return [];
		return Object.keys(data[0]);
	});
	
	// Get display title from model name
	const title = $derived(() => {
		const titles = {
			'Period': 'Periods',
			'Pop': 'Populations',
			'Party': 'Parties',
			'PopPeriod': 'Population Periods',
			'PartyPeriod': 'Party Periods',
			'PopVote': 'Population Votes',
			'ElectionResult': 'Election Results'
		};
		return titles[model];
	});
	
	// Get reactive values for template  
	const displayTitle = $derived(title());
	const columns = $derived(tableColumns());
	
	// Safe toLowerCase helper
	const displayTitleLower = $derived(displayTitle?.toLowerCase() || '');
	
	// Format cell values for display
	function formatCellValue(value: any): string {
		if (value === null || value === undefined) return '-';
		if (typeof value === 'object') return JSON.stringify(value);
		return String(value);
	}
	
	// Fetch data on mount
	onMount(async () => {
		try {
			loading = true;
			error = '';
			data = await getAll(model);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load data';
			console.error(`Error loading ${model} data:`, err);
		} finally {
			loading = false;
		}
	});
</script>

<div class="w-full">
	<h3 class="text-lg font-semibold text-secondary-300 mb-4">{displayTitle}</h3>
	
	{#if loading}
		<div class="text-center py-8 text-secondary-200">
			Loading {displayTitleLower}...
		</div>
	{:else if error}
		<div class="text-center py-8 text-failure-200">
			Error: {error}
		</div>
	{:else if data.length === 0}
		<div class="text-center py-8 text-secondary-200">
			No {displayTitleLower} available
		</div>
	{:else}
		<div class="overflow-x-auto bg-secondary-50 rounded-lg border border-secondary-100">
			<table class="w-full">
				<thead>
					<tr class="bg-secondary-100">
						{#each columns as column}
							<th class="px-6 py-3 text-left text-xs font-medium text-secondary-300 uppercase tracking-wider">
								{column.replace(/_/g, ' ')}
							</th>
						{/each}
					</tr>
				</thead>
				<tbody class="divide-y divide-secondary-100">
					{#each data as row, index}
						<tr 
							class="
								{index % 2 === 1 ? 'bg-secondary-100/50' : 'bg-secondary-50'}
								hover:bg-secondary-100 transition-colors duration-150
							"
						>
							{#each columns as column}
								<td class="px-6 py-4 text-sm text-secondary-300">
									{formatCellValue(row[column])}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>