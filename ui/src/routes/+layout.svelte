<script lang="ts">
	import { onMount } from 'svelte'
	import sourceSansPro from '@fontsource/source-sans-pro/files/source-sans-pro-latin-400-normal.woff2?url'
	import sourceSansProBold from '@fontsource/source-sans-pro/files/source-sans-pro-latin-900-normal.woff2?url'

	import { Analytics, Header, Footer } from '$lib/components/layout'

	import '../app.css'

	let { params, children } = $props()

	// force scroll to top on navigate
	let contentNode: HTMLElement | null = $state(null)
	$effect.pre(() => {
		const _ = params
		contentNode?.scrollTo({ top: 0, behavior: 'auto' })
	})
</script>

<svelte:head>
	<link rel="preload" as="font" type="font/woff2" href={sourceSansPro} crossorigin="anonymous" />
	<link
		rel="preload"
		as="font"
		type="font/woff2"
		href={sourceSansProBold}
		crossorigin="anonymous"
	/>
</svelte:head>

<Analytics />

<div class="flex flex-col h-full w-full overflow-none">
	<Header />

	<main bind:this={contentNode} class="h-full w-full flex-auto overflow-auto">
		{@render children()}
	</main>

	<Footer />
</div>
