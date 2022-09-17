/* eslint-disable no-await-in-loop */
import { hasWindow } from 'util/dom'
import { captureException } from 'util/log'
import config from '../../../gatsby-config'

const { apiToken } = config.siteMetadata
let { apiHost } = config.siteMetadata

const pollInterval = 1000 // milliseconds; 1 second
const jobTimeout = 600000 // milliseconds; 10 minutes
const failedFetchLimit = 5

if (hasWindow && !apiHost) {
  apiHost = `//${window.location.host}`
}

export const submitJob = async (path, data, onProgress) => {
  const formData = new FormData()
  Object.entries(data).forEach(([key, value]) => {
    formData.append(key, value)
  })

  const response = await fetch(`${apiHost}/api/${path}?token=${apiToken}`, {
    method: 'POST',
    body: formData,
  })

  const json = await response.json()
  const { job, detail } = json

  if (response.status === 400) {
    // indicates error with user request, show error to user

    // just for logging
    console.error('Bad job submit request', json)
    captureException('Bad job submit request', json)

    return { error: detail }
  }

  if (response.status !== 200) {
    console.error('Bad response', json)
    captureException('Bad job submit response', json)

    throw new Error(response.statusText)
  }

  const result = await pollJob(job, onProgress)
  return result
}

const pollJob = async (jobId, onProgress) => {
  let time = 0
  let failedRequests = 0

  let response = null

  while (time < jobTimeout && failedRequests < failedFetchLimit) {
    try {
      response = await fetch(`${apiHost}/api/reports/status/${jobId}`, {
        cache: 'no-cache',
      })
    } catch (ex) {
      failedRequests += 1

      // sleep and try again
      await new Promise((r) => setTimeout(r, pollInterval))
      time += pollInterval
      /* eslint-disable-next-line no-continue */
      continue
    }

    const json = await response.json()
    const {
      status = null,
      progress = null,
      message = null,
      errors = null,
      detail: error = null, // error message
      result = null,
    } = json

    if (response.status !== 200 || status === 'failed') {
      captureException('Job failed', json)
      if (error) {
        return { error }
      }

      throw Error(response.statusText)
    }

    if (status === 'success') {
      return { result, errors }
    }

    if (progress != null) {
      onProgress({ progress, message, errors })
    }

    // sleep
    await new Promise((r) => setTimeout(r, pollInterval))
    time += pollInterval
  }

  // if we got here, it meant that we hit a timeout error or a fetch error
  if (failedRequests) {
    captureException(`Job encountered ${failedRequests} fetch errors`)

    return {
      error:
        'network errors were encountered.  The server may be too busy or your network connection may be having problems.  Please try again in a few minutes.',
    }
  }

  if (time >= jobTimeout) {
    captureException('Report job timed out')
    return {
      error:
        'timeout while running job.  Your areas may be too big or complex.',
    }
  }

  captureException('Job had an unexpected error')
  return {
    error:
      'unexpected errors prevented your job from completing successfully.  Please try again.',
  }
}
