<script lang="ts">
	interface Props {
		title: string;
	}
	
	let { title }: Props = $props();
</script>

<header class="mb-2 mt-2 p-2">
	<div class="">
		<h1 class="text-xl font-thin">{title}</h1>
	</div>
</header>