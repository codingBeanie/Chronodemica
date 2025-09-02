<script lang="ts">
	import type { Snippet } from "svelte";
	interface Props {
		title?: string;
		children: Snippet;
	}
    let { children, title}: Props = $props();
</script>

<!-- Container füllt die Spaltenbreite und ist so hoch wie nötig -->
<div class="w-full h-fit">

	<div class="bg-light rounded-xl p-4 shadow-sm">
		{#if title}
			<div class="text-lg font-bold text-dark mb-8 pb-2 border-b border-light-alt">{title}</div>
		{/if}
		{@render children?.()}
	</div>
</div>