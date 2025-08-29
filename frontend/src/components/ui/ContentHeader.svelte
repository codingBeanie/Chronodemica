<script lang="ts">
	interface Props {
		title: string;
	}
	
	let { title }: Props = $props();
</script>

<header class="p-8 my-3 mx-6">
	<div class="">
		<h1 class="text-2xl font-bold">{title}</h1>
	</div>
</header>