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
		<h2 class="text-lg font-semibold mb-3">{label}</h2>
	{/if}
	<div class="flex border border-light-alt rounded-lg p-2 gap-2">
		{#each Object.entries(options) as [title, value]}
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