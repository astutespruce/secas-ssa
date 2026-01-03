<script lang="ts">
	import { resolve } from '$app/paths'
	import { Root as Alert } from '$lib/components/ui/alert'
	import { Badge } from '$lib/components/ui/badge'
	import { Button } from '$lib/components/ui/button'

	import ExclamationTriangle from '~icons/fa-solid/exclamation-triangle'
	import FileAlt from '~icons/fa-regular/file-alt'

	const steps = [
		{
			label: 'Upload a shapefile with analysis units',
			description:
				'The shapefile should contain one record for each analysis unit to be analyzed. Analysis units can be species population units, representation units, or ranges.'
		},
		{
			label: 'Identify analysis unit attribute',
			description:
				'You will need to identify the attribute (data column) that uniquely identifies each analysis unit.'
		},
		{
			label: 'Choose landscape-level factors',
			description:
				'You can choose from terrestrial, freshwater, and coastal indicators, land cover trends, and projected sea-level rise and urbanization.'
		},
		{
			label: 'Download report spreadsheet',
			description:
				'The tool will create a spreadsheet with one sheet per factor and additional details about the datasets used in the analysis.'
		}
	]
</script>

<svelte:head>
	<title>Southeast Species Status Landscape Assessment Tool</title>
</svelte:head>

<svelte:window />

<div class="relative z-0 w-full">
	<div class="relative overflow-hidden h-48 sm:h-64 md:h-80">
		<div class="z-1 absolute top-0">
			<enhanced:img
				src="$images/robert-thiemann-1bj4WGNDFHw-unsplash.jpg"
				class="h-auto min-w-180 object-cover brightness-80"
				alt=""
			/>
		</div>
		<div class="container mt-6 md:mt-14">
			<h1
				class="relative text-white z-2 text-shadow-sm text-shadow-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl"
			>
				Southeast Species Status Landscape Assessment Tool
			</h1>
			<div
				class="relative z-2 hidden sm:block sm:text-3xl font-normal mt-2 text-white text-shadow-black text-shadow-sm"
			>
				Supporting species status assessments using standardized landscape-level data
			</div>
		</div>
	</div>
</div>
<div class="hidden sm:block text-sm text-right pr-1 leading-tight text-grey-8">
	Great Smokey Mountains National Park. Photo: <a
		href="https://unsplash.com/photos/1bj4WGNDFHw"
		target="_blank"
		tabindex="-1">Robert Thiemann</a
	>
</div>

<div class="container pt-6 pb-8">
	<p class="text-xl sm:text-2xl">
		<a href="https://www.fws.gov/project/species-status-assessment" target="_blank">
			Species Status Assessments
		</a>
		(SSAs) are used by U.S. Fish and Wildlife Service to make decisions under the Endangered Species Act.
		SSAs depend on the latest available data that describe current and projected future landscape conditions
		that may influence the persistence of populations of a species.
		<br />
		<br />
		This tool creates reports that help SSA analysts evaluate the potential influences of landscape-level
		factors. These reports include summaries of standardized landscape-level data for user-uploaded analysis
		units, including indicators of habitat quality and projections of future urbanization and sea-level
		rise.
	</p>

	<div class="flex justify-center mt-16">
		<Button href={resolve('/report')} class="no-underline text-2xl py-6">
			<FileAlt class="size-6" aria-hidden="true" />
			Create Custom Report</Button
		>
	</div>

	<Alert class="text-lg mt-16 bg-destructive/15 text-foreground flex gap-4 border-none">
		<div>
			<ExclamationTriangle class="size-14 flex-none" aria-hidden="true" />
		</div>
		<div>
			<b>WARNING</b>: This is an early development version of this application that is being used to
			test this approach for supporting Species Status Assessments. This has not yet been officially
			released.
		</div>
	</Alert>

	<hr />

	<h2 class="text-3xl sm:text-4xl md:text-6xl mt-8">How to create a report</h2>
	<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-8">
		<div>
			{#each steps as step, i (step.label)}
				<div class="not-first:mt-8">
					<div class="flex gap-4 items-center">
						<Badge class="text-2xl size-9">
							{i + 1}
						</Badge>
						<div class="text-xl sm:text-2xl font-bold leading-tight">{step.label}</div>
					</div>
					<p class="ml-14">
						{step.description}
					</p>
				</div>
			{/each}
		</div>

		<figure class="hidden sm:block">
			<enhanced:img src="$images/4971502145_03d6b78f28_o.jpg" alt="Key Deer at Key Deer NWR" />
			<figcaption>
				Key Deer at Key Deer NWR. <br />Photo:
				<a
					href="https://flickr.com/photos/usfwssoutheast/4971502145/in/photostream/"
					target="_blank"
					tabindex="-1">USFWS Southeast Region</a
				>.
			</figcaption>
		</figure>
	</div>

	<hr />

	<h2 class="text-2xl sm:text-3xl md:text-4xl mt-8">What datasets are available?</h2>

	<p class="text-xl mt-2">This tool includes the following datasets:</p>
	<div class="grid gap-8 sm:grid-cols-[2fr_1fr] mt-2 text-lg">
		<ul>
			<li class="[&_ul_li]:leading-tight">
				Terrestrial and freshwater indicators created as part of the Southeast Blueprint 2025,
				including

				<div class="grid gap-px sm:grid-cols-3 mt-2 sm:bg-grey-2 sm:border sm:border-grey-2">
					<div class="sm:bg-grey-0 px-4 pb-4 sm:pt-2">
						<div class="italic">Terrestrial</div>
						<ul>
							<li>fire frequency</li>
							<li>intact habitat cores</li>
							<li>resilient terrestrial sites</li>
						</ul>
					</div>

					<div class="sm:bg-grey-0 px-4 pb-4 sm:pt-2">
						<div class="italic text-lg">Freshwater</div>
						<ul>
							<li>aquatic network complexity</li>
							<li>natural landcover in floodplains</li>
						</ul>
					</div>

					<div class="sm:bg-grey-0 px-4 pb-4 sm:pt-2">
						<div class="italic text-lg">Coastal</div>
						<ul>
							<li>coastal shoreline condition</li>
							<li>resilient coastal sites</li>
							<li>stable coastal wetlands</li>
						</ul>
					</div>
				</div>
			</li>
			<li>
				<a
					href="https://www.usgs.gov/centers/eros/science/national-land-cover-database"
					target="_blank"
				>
					National Land Cover Database 2001 - 2021: land cover and impervious surface
				</a>
			</li>
			<li>
				Current and projected future urban development areas by decade 2030 to 2100 created by the
				FUTURES project
			</li>
			<li>
				Areas impacted by sea-level rise up to 10 feet calculated by the{' '}
				<a href="https://coast.noaa.gov/slrdata/">
					National Oceanic & Atmospheric Administration
				</a>
			</li>
			<li>Floodplain inundation frequency by land cover class.</li>
			<li>
				Projected future sea-level rise depths by decade 2020 to 2100 based on the National Oceanic
				& Atmospheric Administration&apos;s{' '}
				<a
					href="https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report.html"
					target="_blank"
				>
					2022 Sea Level Rise Technical Report
				</a>
			</li>
			<li>
				Dams, potential road-related barriers, and aquatic network alteration based on the Southeast
				Aquatic Resource Partnership's{' '}
				<a href="https://aquaticbarriers.org/" target="_blank">
					National Aquatic Barrier Prioritization Tool
				</a>
				.
			</li>
		</ul>
		<figure class="hidden sm:block">
			<enhanced:img
				src="$images/5142785872_b34caf59e3_h.jpg"
				alt="Prescribed fire, Mississippi Sandhill Crane NWR 2004"
			/>
			<figcaption>
				Prescribed fire, Mississippi Sandhill Crane NWR 2004. <br />Photo:
				<a href="https://flickr.com/photos/usfwssoutheast/5142785872/" target="_blank" tabindex="-1"
					>USFWS Southeast Region</a
				>.
			</figcaption>
		</figure>
	</div>

	<p class="mt-8">
		To learn more about these datasets, including how they were prepared for use in this tool,
		please see the{' '}
		<a href={resolve('/datasets')}>dataset details</a> page.
	</p>

	<hr />

	<div class="grid sm:grid-cols-[1fr_2fr] gap-8">
		<figure class="hidden sm:block">
			<enhanced:img
				src="$images/5149490458_5ffcce6c44_c.jpg"
				alt="Looking for mussels on the Little Tennessee River"
			/>
			<figcaption class="text-left">
				Looking for mussels on the Little Tennessee River.
				<br />Photo:
				<a href="https://flickr.com/photos/usfwssoutheast/5149490458/" target="_blank" tabindex="-1"
					>Gary Peeples / USFWS Southeast Region</a
				>.
			</figcaption>
		</figure>
		<div>
			<h2 class="text-4xl">Disclaimer</h2>
			<p class=" mt-2">
				Use of this tool is not required for the development of SSAs. The summaries provided here
				are intended to simplify the assessment of how exposed populations of fish, wildlife &
				plants are to various influences and stressors (list will grow over time). The biologist
				performing the assessment must determine if the influences and stressors provided here are
				relevant to the resiliency, redundancy, and representation of their focal species, as well
				as whether the spatial data summarized here is the most appropriate (i.e., best-available)
				for their species.
			</p>
		</div>
	</div>

	<hr />

	<h2 class="mt-8 text-4xl">Credits</h2>
	<div class="grid gap-8 sm:grid-cols-[2fr_1fr] mt-2">
		<div>
			<p>
				This application was developed by{' '}
				<a href="https://astutespruce.com" target="_blank"> Astute Spruce, LLC </a>{' '}
				in partnership with the U.S. Fish and Wildlife Service under the{' '}
				<a href="http://secassoutheast.org/" target="_blank">
					Southeast Conservation Adaptation Strategy
				</a>
				.
			</p>
		</div>
		<figure class="hidden sm:block">
			<enhanced:img
				src="$images/8027062941_e8fcdf1247_c.jpg"
				alt="Endangered mussels for release in the Powell River"
			/>
			<figcaption>
				Endangered mussels for release in the Powell River. <br />Photo:
				<a href="https://flickr.com/photos/usfwssoutheast/8027062941/in/photostream/"
					>Gary Peeples / USFWS Southeast Region</a
				>.
			</figcaption>
		</figure>
	</div>
</div>
