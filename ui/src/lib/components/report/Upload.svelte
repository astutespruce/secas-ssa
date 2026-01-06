<script lang="ts">
	import Job from './Job.svelte'
	import UploadForm from './UploadForm.svelte'

	const { onSuccess } = $props()

	let data = $state(null)

	const handleSubmit = (newData) => {
		data = newData
	}

	const handleReset = () => {
		data = null
	}
</script>

<div class="text-lg sm:mt-12">
	{#if data !== null}
		<Job path="upload" {data} defaultMessage="Uploading..." {onSuccess} onCancel={handleReset} />
	{:else}
		<UploadForm onSubmit={handleSubmit} onReset={handleReset} />
	{/if}
</div>
