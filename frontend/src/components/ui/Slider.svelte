<script lang="ts">
	interface Props {
		id: string;
		title: string;
		value: number;
		min: number;
		max: number;
		step?: number;
		hint?: string;
	}

	let { id, title, value = $bindable(), min, max, step = 1, hint }: Props = $props();

	function formatNumber(num: number): string {
		return num.toLocaleString();
	}
</script>

<!-- SLIDER CONTAINER: Overall layout and spacing -->
<div class="flex flex-col border border-light-alt rounded-xl p-4">
	<!-- SLIDER HEADER: Title and current value display -->
	<div class="flex justify-between items-center">
		<!-- SLIDER LABEL: Field title with optional hint -->
		<div class="flex items-start gap-2 relative">
			<label for={id} class="uppercase text-sm font-medium text-dark-text">{title}</label>
			{#if hint}
				<div class="relative group">
					<span class="text-xs text-lightText cursor-help rounded-full bg-light-alt w-4 h-4 flex items-center justify-center">?</span>
					<!-- HINT TOOLTIP: Appears on hover -->
					<div class="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-dark text-light text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
						{hint}
					</div>
				</div>
			{/if}
		</div>

	</div>
	<!-- SLIDER INPUT: Range input element styling -->
	<input 
		{id}
		type="range" 
		bind:value 
		{min} 
		{max} 
		{step}
		class="w-full py-1 my-4 h-2 bg-light-alt rounded-lg appearance-none cursor-pointer"
	/>
	<!-- SLIDER RANGE LABELS: Min/max value indicators -->
	<div class="flex justify-between font-mono">
		<span class="text-xs">{formatNumber(min)}</span>
		<!-- SLIDER VALUE DISPLAY: Current value with monospace font -->
		<span class="p-2 bg-light-alt rounded-md">{formatNumber(value)}</span>
		<span class="text-xs">{formatNumber(max)}</span>
	</div>
</div>