<script lang="ts">
	import ContentHeader from '../../components/ui/ContentHeader.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import CrudTable from '../../components/ui/CrudTable.svelte';

	// Configuration hashmap for the segmented control options
	const dataTypeOptions = {
		'Population': 'Pop',
		'Party': 'Party', 
		'Period': 'Period'
	};
	
	let selectedDataType: 'Pop' | 'Party' | 'Period' = 'Pop';
</script>

<ContentHeader 
	title="Data Entry" 
	caption="Capture and manage your simulation data"
/>

<div class="p-6 space-y-8">
	<SegmentedControl 
		label="Select Data Type"
		options={dataTypeOptions}
		bind:selectedValue={selectedDataType}
	/>
	
	<CrudTable model={selectedDataType} />
</div>