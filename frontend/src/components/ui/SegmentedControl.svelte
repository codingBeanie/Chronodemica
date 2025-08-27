<script lang="ts">
	interface Props {
		options?: Record<string, string>;
		selectedValue?: string;
		label?: string;
		onchange?: (value: string) => void;
	}
	
	let { options = {}, selectedValue = $bindable(''), label = '', onchange }: Props = $props();
	
	function handleSelection(value: string) {
		selectedValue = value;
		onchange?.(value);
	}
</script>

<div class="mb-6">
	{#if label}
		<h2 class="text-lg font-semibold text-secondary-300 mb-3">{label}</h2>
	{/if}
	<div class="flex bg-secondary-100 rounded-lg p-1 gap-1">
		{#each Object.entries(options) as [title, value]}
			<button
				class="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200
					{selectedValue === value 
						? 'bg-primary-200 text-secondary-100 shadow-sm' 
						: 'text-secondary-300 hover:bg-secondary-50 hover:text-primary-200'
					}"
				onclick={() => handleSelection(value)}
			>
				{title}
			</button>
		{/each}
	</div>
</div>