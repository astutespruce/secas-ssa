export type ReportJobResult = {
	error?: string
	result?: string
	errors?: string[]
}

export type ProgressCallbackParams = {
	status: string
	progress: number
	queuePosition?: number
	elapsedTime?: number
	message: string | null
	errors: string[] | null
}

export type ProgressCallback = (params: ProgressCallbackParams) => void

export type JobStatus = {
	progress: number
	message?: string | null
	error?: string | null
}
