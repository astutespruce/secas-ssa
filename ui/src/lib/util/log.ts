/* eslint-disable no-console */
import * as Sentry from '@sentry/browser'

import { hasWindow } from './dom'

export const captureException = (err: Error | string, data: object | null = null) => {
	// @ts-expect-error Sentry is dynamically defined
	if (hasWindow && window.Sentry) {
		Sentry.withScope((scope) => {
			// capture location where error occurred
			scope.setFingerprint([window.location.pathname])
			if (data) {
				scope.setExtra('data', data)
			}
			Sentry.captureException(err)
		})
	}
}

export const logGAEvent = (event: string, data: object | null = null) => {
	// NOTE: window.gtag only available in build mode
	// @ts-expect-error gtag is dynamically defined
	if (!hasWindow || !window.gtag) {
		return
	}

	try {
		// @ts-expect-error gtag is dynamically defined
		window.gtag('event', event, data)
	} catch (ex) {
		console.error('Could not log event to google', ex)
	}
}
