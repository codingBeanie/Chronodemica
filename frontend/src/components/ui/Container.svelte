<script lang="ts">
	let { children } = $props();
</script>

<!-- Container füllt die Spaltenbreite und ist so hoch wie nötig -->
<div class="w-full h-fit">
	<div class="bg-light rounded-xl p-4 shadow-sm">
		{@render children?.()}
	</div>
</div>