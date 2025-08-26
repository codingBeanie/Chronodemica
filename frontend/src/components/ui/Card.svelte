<script lang="ts">
	let { 
		title = '', 
		description = '',
		children 
	} = $props();
</script>

<div class="bg-secondary-100 border border-secondary-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
	{#if title}
		<div class="px-6 py-4 border-b border-secondary-200">
			<h3 class="text-lg font-semibold text-secondary-300">{title}</h3>
			{#if description}
				<p class="mt-1 text-sm text-secondary-300">{description}</p>
			{/if}
		</div>
	{/if}
	<div class="px-6 py-4">
		{@render children?.()}
	</div>
</div>