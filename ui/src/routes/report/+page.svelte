<script lang="ts">
	import Check from '~icons/fa-solid/check'
	import { cn } from '$lib/utils'

	import { Badge } from '$lib/components/ui/badge'
	import { Button } from '$lib/components/ui/button'

	import { Download, SelectAttribute, SelectDatasets, Upload } from '$lib/components/report'
	import { categories, datasets } from '$lib/config/constants'

	const steps = [
		{ id: 'upload', label: 'Upload' },
		{
			id: 'selectAttribute',
			label: 'Identify attribute'
		},
		{
			id: 'selectDatasets',
			label: 'Select factors'
		},
		{ id: 'download', label: 'Download report' }
	]

	type Step = 'upload' | 'selectAttribute' | 'selectDatasets' | 'download' | 'error'

	let stepIndex: number = $state(0)
	let step: Step = $derived(steps[stepIndex].id as Step)

	let uuid: string | null = $state(null)
	let attributes: object = $state({}) // set via API
	let selectedAttribute: string = $state('') // blank indicates no selected attribute
	let openCategories: Record<string, boolean> = $state(
		Object.fromEntries(categories.map(({ id }) => [id, true]))
	)
	let allDatasets: Record<string, boolean> = Object.fromEntries(
		Object.keys(datasets).map((id) => [id, true])
	)
	// by default assume all are available and selected (as separate copies)
	let availableDatasets: Record<string, boolean> = $state(allDatasets)
	let selectedDatasets: Record<string, boolean> = $state({ ...allDatasets })

	type FileUploadSuccessParams = {
		uuid: string
		fields: object
		datasets: string[]
	}
	const handleFileUploadSuccess = ({
		uuid: uploadUuid,
		fields: uploadAvailableFields = {},
		datasets: availableDatasetIds = []
	}: FileUploadSuccessParams) => {
		stepIndex = 1
		uuid = uploadUuid
		attributes = uploadAvailableFields
		selectedAttribute = ''

		const uploadAvailableDatasets = new Set(availableDatasetIds)
		availableDatasets = Object.fromEntries(
			Object.keys(datasets).map((id) => [id, uploadAvailableDatasets.has(id)])
		)

		selectedDatasets = { ...availableDatasets }
	}

	const handleStartOver = () => {
		stepIndex = 0
		uuid = null
		selectedAttribute = ''
		attributes = {}
		availableDatasets = allDatasets
		selectedDatasets = { ...allDatasets }
	}

	const handleStepClick = (newIndex: number) => {
		if (newIndex === 0) {
			handleStartOver()
		} else {
			stepIndex = newIndex
		}
	}

	const handleSelectAttributeNext = () => {
		stepIndex = 2
	}

	const handleSelectDatasetsBack = () => {
		stepIndex = 1
	}

	const handleCreateReport = () => {
		stepIndex = 3
	}
</script>

<svelte:head>
	<title>Create Report | Southeast Species Status Landscape Assessment Tool</title>
</svelte:head>

<svelte:document
	ondragover={(e) => {
		e.preventDefault()
	}}
	ondrop={(e) => {
		e.preventDefault()
	}}
/>

<div class="relative z-0 w-full">
	<div class="relative overflow-hidden h-48 md:h-64">
		<div class="z-1 absolute top-0">
			<enhanced:img
				src="$images/5494812678_3849557155_o.jpg"
				class="h-auto min-w-180 object-cover brightness-70"
				alt=""
				fetchpriority="high"
			/>
		</div>
		<div class="container mt-6 md:mt-12">
			<h1
				class="relative text-white z-2 text-shadow-sm text-shadow-black text-4xl sm:text-5xl md:text-6xl"
			>
				Create a Species Status Landscape Assessment Report
			</h1>
		</div>
	</div>
</div>
<div class="hidden sm:block text-sm text-right pr-1 leading-tight text-grey-8">
	White River National Wildlife Refuge. Photo: <a
		href="https://www.flickr.com/photos/usfwssoutheast/5494812678/"
		target="_blank"
		tabindex="-1">U.S. Fish and Wildlife Service Southeast Region</a
	>.
</div>

<div class="container pt-8 pb-4">
	<nav class="grid-cols-4 border border-grey-8/50 hidden sm:grid">
		{#each steps as step, i (step.id)}
			<Button
				variant="ghost"
				class={cn(
					'flex items-center gap-4 flex-auto rounded-none text-base disabled:opacity-100 not-last-of-type:border-r border-r-grey-8/20 pt-2',
					{
						'bg-ok/20 hover:bg-ok/30': i < stepIndex,
						'bg-grey-8/30 font-bold cursor-default hover:bg-grey-8/30': i === stepIndex,
						'bg-grey-1 text-grey-8 cursor-not-allowed': i > stepIndex
					}
				)}
				disabled={i > stepIndex}
				onclick={i < stepIndex
					? () => {
							handleStepClick(i)
						}
					: () => {}}
			>
				<Badge
					class={cn('size-6 text-base hidden md:flex', {
						'bg-ok': i < stepIndex,
						'bg-foreground': i === stepIndex,
						'bg-grey-8': i > stepIndex
					})}
				>
					{i + 1}
				</Badge>
				<div>
					{step.label}
				</div>

				<Check
					class={cn('size-4 invisible', {
						visible: i < stepIndex
					})}
					aria-hidden="true"
				/>
			</Button>
		{/each}
	</nav>

	{#if step === 'upload'}
		<Upload onSuccess={handleFileUploadSuccess} />
	{:else if step === 'selectAttribute'}
		<SelectAttribute
			{attributes}
			bind:selectedAttribute
			onBack={handleStartOver}
			onNext={handleSelectAttributeNext}
		/>
	{:else if step === 'selectDatasets'}
		<SelectDatasets
			bind:openCategories
			{availableDatasets}
			bind:selectedDatasets
			onBack={handleSelectDatasetsBack}
			onNext={handleCreateReport}
		/>
	{:else if step === 'download'}
		<Download {uuid} {selectedAttribute} {selectedDatasets} onCancel={handleStartOver} />
	{/if}
</div>
