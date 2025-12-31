<script lang="ts">
	import { onMount } from 'svelte'
	import ExclamationTriangle from '~icons/fa-solid/exclamation-triangle'
	import ReplyAllIcon from '~icons/fa-solid/reply-all'

	import { Root as Alert } from '$lib/components/ui/alert'
	import { Button } from '$lib/components/ui/button'
	import { Progress } from '$lib/components/ui/progress'

	import { CONTACT_EMAIL } from '$lib/env'
	import { captureException, logGAEvent } from '$lib/util/log'
	import { submitJob } from './api'

	const { data, path, defaultMessage, onCancel, onSuccess } = $props()

	let progress: number = $state(0)
	let message: string = $derived(defaultMessage)
	let error: string | null = $state(null)

	onMount(async () => {
		if (data.file) {
			logGAEvent('file-upload', {
				file: data.file.name,
				sizeKB: data.file.size / 1024
			})
		} else if (data.datasets) {
			logGAEvent('create-report', {
				datasets: data.datasets
			})
		}
		try {
			// upload file and update progress
			const { result, error: jobError } = await submitJob(
				path,
				data,
				({ progress: nextProgress, message: nextMessage = null, errors: nextErrors = null }) => {
					progress = nextProgress
					message = nextMessage || message || defaultMessage
					error = nextErrors && nextErrors.length ? nextErrors.join(', ') : error
				}
			)

			if (jobError) {
				// eslint-disable-next-line no-console
				console.error(jobError)
				progress = 0
				message = defaultMessage
				error = jobError

				logGAEvent('file-upload-error')

				return
			}

			// job completed successfully, return
			progress = 100
			message = 'Done!'
			error = null

			onSuccess(result)
		} catch (ex) {
			captureException('job failed', ex)
			// eslint-disable-next-line no-console
			console.error(`Caught unhandled error from job: ${path}`, ex)

			progress = 0
			message = defaultMessage
			error = ''
		}
	})

	const handleCancel = () => {
		progress = 0
		message = defaultMessage
		error = null
		onCancel()
	}
</script>

{#if error !== null}
	<Alert class="text-lg mt-16 bg-destructive/10 text-destructive flex gap-4 border-destructive">
		<div>
			<ExclamationTriangle class="size-14 flex-none" />
		</div>
		<div>
			<div class="text-2xl font-bold">Uh oh! There was an error!</div>
			<p>
				{#if error}
					The server says: {error}
				{:else}
					Please try again. If that does not work, please
					<a href={`mailto:${CONTACT_EMAIL}`}>contact us </a>
					.
				{/if}
			</p>
		</div>
	</Alert>
	<hr />
	<div class="flex justify-center">
		<Button variant="destructive" onclick={handleCancel}>
			<ReplyAllIcon class="size-6" />
			Start over
		</Button>
	</div>
{:else}
	<h3 class="text-xl">
		{message}
	</h3>
	<div class="flex items-center gap-4 mt-2">
		<Progress value={progress} max={100} class="h-4" />
		<div class="text-xl leading-none">{progress}%</div>
	</div>
{/if}
