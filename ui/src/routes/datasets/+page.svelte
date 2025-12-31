<script lang="ts">
	import ExternalLinkAlt from '~icons/fa-solid/external-link-alt'
	import { categories } from '$lib/config/constants'
</script>

<svelte:head>
	<title>Datasets | Southeast Species Status Landscape Assessment Tool</title>
</svelte:head>

<div class="relative z-0 w-full">
	<div class="relative overflow-hidden h-48">
		<div class="z-1 absolute top-0 md:-top-[75%]">
			<enhanced:img
				src="$images/5142785230_69f04b6562_o.jpg"
				class="h-auto min-w-180 object-cover brightness-70"
				alt=""
			/>
		</div>
		<div class="container mt-6 md:mt-14">
			<h1
				class="relative text-white z-2 text-shadow-sm text-shadow-black text-4xl sm:text-5xl md:text-6xl"
			>
				Dataset details
			</h1>
		</div>
	</div>
</div>
<div class="hidden sm:block text-sm text-right pr-1 leading-tight text-grey-8">
	Prescribed burn at Florida Panther NWR. Photo: <a
		href="https://flickr.com/photos/usfwssoutheast/5142785230/in/photostream/"
		target="_blank">U.S. Fish and Wildlife Service Southeast Region</a
	>.
</div>

<div class="container pt-4 pb-8">
	<div>
		<div class="text-2xl font-bold">Table of contents</div>
		<ul class="mt-2">
			<li>
				<a href="#GeneralInformation">General information</a>
			</li>
			{#each categories as category (category.id)}
				<li>
					<a href={`#${category.id}Section`}>{category.label}</a>
					<ul>
						{#each category.datasets as dataset (dataset.id)}
							<li>
								<a href={`#${dataset.id}Section`}>{dataset.name}</a>
							</li>
						{/each}
					</ul>
				</li>
			{/each}
		</ul>
	</div>

	<hr />

	<h2 id="GeneralInformation" class="text-4xl">General information</h2>
	<p>
		The latest available versions of each dataset were obtained for use in this tool. Each dataset
		was standardized to a 30 meter resolution that is aligned with the Southeast Blueprint, in the
		CONUS Albers (NAD83) spatial projection.
		<br />
		<br />
		Analysis unit boundaries uploaded by the user are rasterized to match these rasters, which means that
		the resulting data queried from each dataset is an approximation based on these rasterized boundaries.
		Analysis units that are very spatially detailed, small, or highly linear may not be approximated as
		well as analysis units that are fairly large or less detailed.
	</p>

	{#each categories as category (category.id)}
		<hr />
		<h2 id={`${category.id}Section`} class="text-4xl">{category.label}</h2>
		<div>
			{#each category.datasets as dataset (dataset.id)}
				<div class="border-l-4 border-l-grey-4 pl-2 mt-6 not-first:mt-12">
					<h3 id={`${dataset.id}Section`} class="text-2xl">{dataset.name}</h3>
					<div class="leading-tight text-lg">
						<div
							class="mt-1 py-1 px-2 bg-grey-0 flex justify-between gap-2 border-t border-t-grey-1 border-b border-b-grey-1"
						>
							<div>
								{#if dataset.url}
									<a href={dataset.url} class="flex items-center gap-2"
										>{dataset.source} <ExternalLinkAlt class="size-4 text-link/50" /></a
									>
								{:else}
									{dataset.source}
								{/if}
							</div>
							<div>
								Publication date: {dataset.date}
							</div>
						</div>
						<p class="mt-2">
							{dataset.description}
							<br />
							<br />
							<b>Data preparation methods:</b>
							<br />
							{dataset.methods}
						</p>
						{#if dataset.citation}
							<div class="border-t border-t-grey-1 italic text-grey-8 mt-4 pt-1 text-base">
								Citation: {dataset.citation}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/each}
</div>
