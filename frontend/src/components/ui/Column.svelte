<script lang="ts">
	interface Props {
		gap?: string;
	}
	
	let { gap = "space-y-4", children } = $props();
</script>

<div class="flex flex-col {gap}">
	{@render children?.()}
</div>