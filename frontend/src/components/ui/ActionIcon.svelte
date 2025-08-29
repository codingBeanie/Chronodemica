<script lang="ts">
	interface Props {
		icon: string;
		disabled?: boolean;
		onclick?: () => void;
		tooltip?: string;
	}

	let { icon, disabled = false, onclick, tooltip }: Props = $props();
</script>

<button 
	class="
		w-8 h-8 
		flex items-center justify-center 
		rounded 
		text-sm 
		transition-all duration-200 
		border 
		bg-light 
		border-light-text 
		text-dark-text
		hover:bg-light 
		hover:border-dark-text
		disabled:opacity-50 
		disabled:cursor-not-allowed
		enabled:cursor-pointer
	"
	onclick={onclick}
	{disabled}
	title={tooltip || ''}
>
	{icon}
</button>