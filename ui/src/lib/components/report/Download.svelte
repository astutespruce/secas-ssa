<script lang="ts">
	import DownloadIcon from '~icons/fa-solid/download'
	import ReplyAllIcon from '~icons/fa-solid/reply-all'
	import { API_HOST } from '$lib/env'
	import { Button } from '$lib/components/ui/button'
	import Job from './Job.svelte'

	type SubmitData = {
		uuid: string
		datasets: string
		field?: string
	}

	const { uuid, selectedAttribute, selectedDatasets, onCancel } = $props()
	let reportURL: string | null = $state(null)

	const data = $derived.by(() => {
		const submitData: SubmitData = {
			uuid,
			datasets: Object.entries(selectedDatasets)
				.filter(([_, v]) => v)
				.map(([k, _]) => k)
				.join(',')
		}
		if (selectedAttribute) {
			submitData.field = selectedAttribute
		}

		return submitData
	})

	const handleSuccess = (reportPath: string) => {
		const url = `${API_HOST}${reportPath}`
		reportURL = url

		window.location.href = url
	}

	$inspect('report URL', reportURL)
</script>

<div class="gap-8 sm:mt-12">
	{#if reportURL !== null}
		<div class="text-2xl font-bold">All done!</div>
		<p class="text-xl">
			Your report should download automatically. You can also click the button below to download
			your report.
		</p>

		<hr />

		<div class="flex gap-4 justify-between">
			<Button variant="destructive" onclick={onCancel}>
				<ReplyAllIcon class="size-6" aria-hidden="true" />
				Start over
			</Button>

			<Button href={reportURL} target="_blank" class="no-underline">
				<DownloadIcon class="size-6" aria-hidden="true" />
				Download report
			</Button>
		</div>
	{:else}
		<Job
			path="report"
			{data}
			defaultMessage="Creating report..."
			onSuccess={handleSuccess}
			{onCancel}
		/>
	{/if}
</div>
