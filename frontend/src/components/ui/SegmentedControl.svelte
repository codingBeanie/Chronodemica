<script lang="ts">
	interface Props {
		options?: Record<string, string>;
		optionsArray?: Array<{title: string, value: string}>;
		selectedValue?: string;
		label?: string;
		onchange?: (value: string) => void;
	}
	
	let { options = {}, optionsArray, selectedValue = $bindable(''), label = '', onchange }: Props = $props();
	
	function handleSelection(value: string) {
		selectedValue = value;
		onchange?.(value);
	}
	
	let displayOptions = $derived(
		optionsArray || Object.entries(options).map(([title, value]) => ({title, value}))
	);
</script>

<div class="mb-6">
	{#if label}
		<h2 class="text-md font-thin mb-3">{label}</h2>
	{/if}
	<div class="flex flex-wrap border border-light-alt rounded-lg p-2 gap-2">
		{#each displayOptions as {title, value}}
			<button
				class="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 cursor-pointer
					{selectedValue === value 
						? 'bg-dark text-light shadow-sm' 
						: 'text-dark-text bg-light-alt hover:bg-dark-alt hover:text-light'
					}"
				onclick={() => handleSelection(value)}
			>
				{title}
			</button>
		{/each}
	</div>
</div>