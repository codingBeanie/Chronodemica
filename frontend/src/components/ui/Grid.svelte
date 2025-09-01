<script lang="ts">
	interface Props {
		cols: string; // z.B. "1fr 2fr" oder "200px 1fr 300px" oder "repeat(3, 1fr)"
		gap?: string;
	}
	
	let { cols, gap = "gap-4", children } = $props();
</script>

<div class="w-full px-1 py-1">
	<div 
		class="grid {gap}" 
		style="grid-template-columns: {cols};"
	>
		{@render children?.()}
	</div>
</div>