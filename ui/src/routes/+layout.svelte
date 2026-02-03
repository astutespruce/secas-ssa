<script lang="ts">
	import { onMount } from 'svelte'
	import sourceSansPro from '@fontsource/source-sans-pro/files/source-sans-pro-latin-400-normal.woff2?url'
	import sourceSansProBold from '@fontsource/source-sans-pro/files/source-sans-pro-latin-900-normal.woff2?url'

	import { browser } from '$app/environment'
	import { GOOGLE_ANALYTICS_ID } from '$lib/env'
	import { Header, Footer } from '$lib/components/layout'

	import '../app.css'

	let { params, children } = $props()

	// force scroll to top on navigate
	let contentNode: HTMLElement | null = $state(null)
	$effect.pre(() => {
		const _ = params
		contentNode?.scrollTo({ top: 0, behavior: 'auto' })
	})

	const handleGTAGLoad = () => {
		if (!window.dataLayer) {
			console.warn('GTAG not properly initialized')
			return
		}

		console.debug('setting up GTAG')

		window.gtag = (...args) => {
			dataLayer.push(...args)
		}

		gtag('js', new Date())
		gtag('config', GOOGLE_ANALYTICS_ID)
	}
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
	{#if browser && GOOGLE_ANALYTICS_ID}
		<script
			async
			src={`https://www.googletagmanager.com/gtag/js?id=${GOOGLE_ANALYTICS_ID}`}
			onload={handleGTAGLoad}
		></script>
	{/if}
</svelte:head>

<div class="flex flex-col h-full w-full overflow-none">
	<Header />

	<main bind:this={contentNode} class="h-full w-full flex-auto overflow-auto">
		{@render children()}
	</main>

	<Footer />
</div>
