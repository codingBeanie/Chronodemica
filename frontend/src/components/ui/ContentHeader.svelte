<script lang="ts">
	interface Props {
		title: string;
		caption?: string;
	}
	
	let { title, caption }: Props = $props();
</script>

<header class="px-6 py-4 my-6">
	<div class="max-w-7xl mx-auto border-b border-secondary-200 pb-2">
		<h1 class="text-4xl font-bold text-primary-300 mb-2">{title}</h1>
		{#if caption}
			<p class="text-secondary-200 text-sm mb-1">{caption}</p>
		{/if}
	</div>
</header>