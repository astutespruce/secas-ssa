<script lang="ts">
	import ReplyAllIcon from '~icons/fa-solid/reply-all'
	import NextIcon from '~icons/fa-solid/angle-double-right'
	import { Badge } from '$lib/components/ui/badge'
	import { Button } from '$lib/components/ui/button'
	import * as Select from '$lib/components/ui/select'
	import { CONTACT_EMAIL } from '$lib/env'

	let { attributes: rawAttributes, selectedAttribute = $bindable(''), onBack, onNext } = $props()

	const noAttributeOption = { value: '', label: '-- Group everything together --' }

	const attributes = $derived(
		[noAttributeOption].concat(
			Object.entries(rawAttributes)
				.map(([value, count]) => ({ value, label: `${value} (${count} unique values)` }))
				.sort(({ value: left }, { value: right }) => (left < right ? -1 : 1))
		)
	)
	const hasAttributes = $derived(Object.keys(rawAttributes).length > 0)
</script>

<div class="grid sm:grid-cols-2 gap-8 sm:mt-12">
	<div>
		<div class="flex items-center gap-4">
			<Badge class="text-2xl size-9">2</Badge>
			<div class="text-2xl font-bold leading-tight">Select analysis unit attribute</div>
		</div>
		<p class="mt-4">
			If your dataset has an attribute that identifies unique analysis units, please choose that
			attribute from the list to the right.
			<br />
			<br />
			If you do not select an attribute, or if one isn&apos;t available in the dataset, all boundaries
			will be combined and analyzed as a single unit.
		</p>
	</div>
	<div>
		<div class="text-xl font-bold">Analysis unit attribute:</div>
		<Select.Root type="single" disabled={!hasAttributes} bind:value={selectedAttribute}>
			<Select.Trigger class="w-full text-base"
				>{attributes.find(({ value: optionValue }) => optionValue === selectedAttribute)
					?.label}</Select.Trigger
			>
			<Select.Content>
				{#each attributes as attribute (attribute.value)}
					<Select.Item
						value={attribute.value}
						class="cursor-pointer text-base data-highlighted:bg-blue-1! data-highlighted:text-foreground!"
					>
						{attribute.label}
					</Select.Item>
				{/each}
			</Select.Content>
		</Select.Root>

		{#if !hasAttributes}
			<div class="text-grey-8 text-base mt-4">
				We did not find any attributes that appear to identify unique analysis units in this dataset
				(limited to text or integer fields). If there is an attribute present that we did not
				detect, please{' '}
				<a href={`mailto:${CONTACT_EMAIL}`}> let us know </a>
				.
			</div>
		{/if}
	</div>
</div>

<hr />

<div class="flex justify-between gap-4">
	<Button variant="destructive" onclick={onBack}
		><ReplyAllIcon class="size-5" />
		Start over</Button
	>
	<Button onclick={onNext}>
		Select factors
		<NextIcon class="size-5" />
	</Button>
</div>
