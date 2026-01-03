<script lang="ts">
	import CaretDown from '~icons/fa-solid/caret-down'
	import CaretRight from '~icons/fa-solid/caret-right'
	import BackIcon from '~icons/fa-solid/angle-double-left'
	import FileIcon from '~icons/fa-solid/file-alt'
	import { Badge } from '$lib/components/ui/badge'
	import { Button } from '$lib/components/ui/button'
	import { Checkbox } from '$lib/components/ui/checkbox'
	import * as Collapsible from '$lib/components/ui/collapsible'
	import { Label } from '$lib/components/ui/label'
	import { InfoTooltip } from '$lib/components/tooltip'
	import { cn } from '$lib/utils'

	import { categories } from '$lib/config/constants'
	import FreshwaterIcon from '$images/freshwater.svg'
	import CoastalIcon from '$images/coastal.svg'
	import LandIcon from '$images/land.svg'
	import TrendsIcon from '$images/trends.svg'

	const icons = {
		freshwater: FreshwaterIcon,
		coastal: CoastalIcon,
		land: LandIcon,
		trends: TrendsIcon
	}
	type IconIndex = 'freshwater' | 'coastal' | 'land' | 'trends'

	let {
		openCategories = $bindable(),
		availableDatasets,
		selectedDatasets = $bindable(),
		onBack,
		onNext
	} = $props()

	const handleSelectAll = () => {
		selectedDatasets = Object.fromEntries(
			Object.entries(availableDatasets).map(([id, isAvailable]) => [id, isAvailable])
		)
	}

	const handleSelectNone = () => {
		selectedDatasets = Object.fromEntries(
			Object.entries(selectedDatasets).map(([id]) => [id, false])
		)
	}

	const hasDatasets = $derived(Object.values(selectedDatasets).some((v) => v))
</script>

<div class="grid sm:grid-cols-[2fr_2fr] gap-8 sm:mt-12">
	<div>
		<div class="flex items-center gap-4">
			<Badge class="text-2xl size-9">3</Badge>
			<div class="text-2xl font-bold leading-tight">Select factors to include in report</div>
		</div>
		<p class="mt-4">
			This tool includes several standardized landscape-level datasets that help characterize
			different aspects of current and potential future conditions. Only those datasets that overlap
			with any of your analyis units are available for your analysis. Select any or all of these
			datasets on the right.
		</p>
	</div>
	<div>
		<div class="sm:flex justify-between gap-4">
			<div class="text-2xl font-bold">Available landscape-level factors:</div>
			<div class="flex items-center gap-2 flex-none justify-end">
				<Button variant="link" class="p-0" onclick={handleSelectAll}>select all</Button>
				<div class="text-grey-3">|</div>
				<Button variant="link" class=" p-0" onclick={handleSelectNone}>select none</Button>
			</div>
		</div>

		<div>
			{#each categories as category (category.id)}
				<Collapsible.Root
					bind:open={openCategories[category.id]}
					class="not-first-of-type:mt-2 not-last-of-type:mb-8"
				>
					<Collapsible.Trigger
						class="w-full py-2 border-t border-b items-center flex gap-2 text-start px-2 cursor-pointer"
						style={`background-color: ${category.color}; border-color: ${category.borderColor}`}
					>
						{#if openCategories[category.id]}
							<CaretDown class="size-6" aria-hidden="true" />
						{:else}
							<CaretRight class="size-6" aria-hidden="true" />
						{/if}
						<img src={icons[category.id as IconIndex]} alt="" aria-hidden="true" class="size-8" />
						<div class="font-bold text-xl">
							{category.label}
						</div>
					</Collapsible.Trigger>
					<Collapsible.Content class="pt-4">
						{#each category.datasets as dataset (dataset.id)}
							<div class="flex items-center gap-2">
								<Checkbox
									id={dataset.id}
									aria-label={`Select / deselect ${dataset.name}`}
									class="cursor-pointer size-5 rounded-xs disabled:border-grey-4 border-2 [&_svg]:size-4"
									bind:checked={selectedDatasets[dataset.id]}
									disabled={!availableDatasets[dataset.id]}
								/>
								<Label
									for={dataset.id}
									class={cn('text-base cursor-pointer', {
										'italic opacity-100! text-grey-8 cursor-not-allowed':
											!availableDatasets[dataset.id]
									})}
									>{dataset.name}
									{#if !availableDatasets[dataset.id]}
										<span class="text-sm"> (no data available) </span>
									{/if}
								</Label>
								<InfoTooltip
									title={dataset.name}
									description={dataset.description}
									aria-label={`Show details for ${dataset.name}`}
								/>
							</div>
						{/each}
					</Collapsible.Content>
				</Collapsible.Root>
			{/each}
		</div>
	</div>
</div>

<hr />

<div class="flex justify-between gap-4 pb-8">
	<Button variant="secondary" onclick={onBack}>
		<BackIcon class="size-5" aria-hidden="true" />

		Select factors</Button
	>
	<Button onclick={hasDatasets ? onNext : () => {}} disabled={!hasDatasets}>
		<FileIcon class="size-5" aria-hidden="true" />

		Create report</Button
	>
</div>
