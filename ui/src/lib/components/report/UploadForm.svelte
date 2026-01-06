<script lang="ts">
	import { fromEvent as getFilesFromEvent } from 'file-selector'
	import { superForm, fileProxy, defaults } from 'sveltekit-superforms'
	import { zod4, zod4Client } from 'sveltekit-superforms/adapters'
	import { z } from 'zod'

	import DownloadIcon from '~icons/fa-solid/download'
	import UploadIcon from '~icons/fa-solid/upload'
	import ExclamationTriangle from '~icons/fa-solid/exclamation-triangle'
	import ReplyAllIcon from '~icons/fa-solid/reply-all'
	import { cn } from '$lib/utils.js'
	import { Field, Control, Label, Button as SubmitButton } from '$lib/components/ui/form'
	import { Badge } from '$lib/components/ui/badge'
	import { Button } from '$lib/components/ui/button'
	import { Input } from '$lib/components/ui/input'

	const MAXSIZE_MB = 100
	const MIME_TYPES = new Set([
		'application/zip',
		'application/x-zip-compressed',
		'application/x-compressed',
		'multipart/x-zip'
	])

	const { onSubmit, onReset } = $props()
	let isDragValid: boolean | null = $state(null)

	const schema = z.object({
		file: z
			.instanceof(File, {
				error: 'Please select a file'
			})
			.refine((f) => f.size < MAXSIZE_MB * 1e6, `File must be less than ${MAXSIZE_MB} MB`)
			.refine(({ type: mimeType }) => MIME_TYPES.has(mimeType), 'File must be a ZIP file')
	})

	const form = superForm(defaults(zod4(schema)), {
		SPA: true,
		validators: zod4Client(schema),
		onUpdate: function ({ form }) {
			const {
				valid,
				data: { file }
			} = form

			if (!valid) {
				return
			}

			onSubmit({ file })
		}
	})

	const { form: formData, enhance, errors, validate } = form
	const fileHandle = fileProxy(formData, 'file')

	const handleDragOver = async (e: DragEvent) => {
		e.preventDefault()
		e.stopPropagation()

		const hasFiles =
			e.dataTransfer &&
			Array.prototype.some.call(
				e.dataTransfer.types,
				(type) => type === 'Files' || type === 'application/x-moz-file'
			)

		if (hasFiles) {
			const files = await getFilesFromEvent(e)
			const [file] = files
			// cannot check file size here, it isn't always defined on file
			isDragValid = files.length === 1 && MIME_TYPES.has(file.type)
		}
	}

	const handleDragOut = (e: DragEvent) => {
		e.preventDefault()
		isDragValid = null
	}

	const handleDrop = async (e: DragEvent) => {
		e.preventDefault()
		isDragValid = null

		const hasFiles =
			e.dataTransfer &&
			Array.prototype.some.call(
				e.dataTransfer.types,
				(type) => type === 'Files' || type === 'application/x-moz-file'
			)

		if (hasFiles) {
			const files = await getFilesFromEvent(e)
			const [file] = files

			if (files.length > 1) {
				alert('Multiple files not allowed')
				return
			}

			fileHandle.set(file as File)
			await validate('file')
		}
	}

	const handleResetFile = () => {
		form.reset()
		onReset()
	}

	const isValid = $derived($formData.file && !$errors.file)
</script>

<form enctype="multipart/form-data" use:enhance>
	<div class="grid sm:grid-cols-2 gap-16">
		<div>
			<div class="flex gap-4 items-center">
				<Badge class="text-2xl size-9">1</Badge>
				<div class="text-2xl font-bold leading-tight">Upload analysis unit boundaries</div>
			</div>
			<p class="mt-4">
				Upload a shapefile or ESRI File Geodatabase Feature Class with the boundaries of the
				analysis units you want to use for your report. Each analysis unit will be analyzed
				independently.
				<br />
				<br />
				You will be able to select the attribute that identifies the analysis units in the next step.
			</p>
		</div>
		<div>
			<Field {form} name="file" class="">
				<Control>
					{#snippet children({ props })}
						<Label
							for="file"
							class="block"
							ondragover={handleDragOver}
							ondrop={handleDrop}
							ondragleave={handleDragOut}
						>
							<div class="text-xl font-bold">Analysis unit boundaries:</div>
							<Input
								type="file"
								{...props}
								bind:files={$fileHandle}
								accept={[...MIME_TYPES].join(',')}
								multiple={false}
								class="mt-2 hidden"
							/>

							<div
								class={cn(
									'border-2 border-grey-5 rounded-lg bg-grey-1/40 border-dashed p-6 flex flex-col justify-center items-center text-center cursor-pointer mt-2',
									{
										'border-error': isDragValid === false || $errors.file,
										'bg-error/10': isDragValid === false || $errors.file,
										'cursor-not-allowed': isDragValid === false,
										'border-ok': isDragValid === true,
										'bg-ok/10': isDragValid === true,
										hidden: isValid
									}
								)}
							>
								<div>
									<DownloadIcon class="size-8" />
								</div>
								<p class="text-2xl font-bold mt-2">Drop your zip file here</p>
								<p class="text-lg text-grey-8 leading-tight mt-4">
									Zip file must contain all associated files for a shapefile (at least .shp, .prj,
									.shx) <br />or file geodatabase (.gdb).
									<br />
									<br />
									Max size: {MAXSIZE_MB} MB.
								</p>
							</div>

							{#if isValid}
								<div class="text-lg ml-4">
									{$formData.file.name}
								</div>
							{/if}
						</Label>

						{#if $errors.file}
							<div class="flex items-center gap-2 text-accent ml-2 mt-4 mb-8">
								<ExclamationTriangle width="1em" height="1em" />
								{$errors.file}
							</div>
						{/if}
					{/snippet}
				</Control>
			</Field>
		</div>
	</div>

	<hr class="border-b-6 my-8" />

	<div class="flex justify-between">
		<div>
			{#if isValid}
				<Button onclick={handleResetFile} variant="destructive">
					<ReplyAllIcon class="size-5" aria-hidden="true" />
					Start over
				</Button>
			{/if}
		</div>
		<SubmitButton disabled={!isValid}>
			<UploadIcon class="size-5" aria-hidden="true" />

			Upload File</SubmitButton
		>
	</div>
</form>
