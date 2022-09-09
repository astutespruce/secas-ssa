import React from 'react'
import PropTypes from 'prop-types'
import { Global } from '@emotion/react'
import { Box, Flex } from 'theme-ui'
import { useErrorBoundary } from 'use-error-boundary'

import { hasWindow, isUnsupported } from 'util/dom'
import ErrorMessage from './ErrorMessage'
import UnsupportedBrowser from './UnsupportedBrowser'
import Header from './Header'
import Footer from './Footer'
import { fonts } from './fonts'

const Layout = ({ children, overflowY }) => {
  const { ErrorBoundary, didCatch } = useErrorBoundary({
    onDidCatch: (err, errInfo) => {
      // eslint-disable-next-line no-console
      console.error('Error boundary caught', err, errInfo)

      if (hasWindow && window.Sentry) {
        const { Sentry } = window
        Sentry.withScope((scope) => {
          scope.setExtras(errInfo)
          Sentry.captureException(err)
        })
      }
    },
  })

  return (
    <>
      <Global styles={fonts} />
      <Flex
        sx={{
          height: '100%',
          flexDirection: 'column',
        }}
      >
        <Header />
        {isUnsupported ? (
          <UnsupportedBrowser />
        ) : (
          <Box sx={{ flex: '1 1 auto', overflowY, height: '100%' }}>
            {didCatch ? (
              <ErrorMessage />
            ) : (
              <ErrorBoundary>{children}</ErrorBoundary>
            )}
          </Box>
        )}
        <Footer />
      </Flex>
    </>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
  overflowY: PropTypes.string,
}

Layout.defaultProps = {
  overflowY: 'auto',
}

export default Layout
