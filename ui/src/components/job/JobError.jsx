import React from 'react'
import PropTypes from 'prop-types'
import { Alert, Heading, Close, Box, Text, Link } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import config from '../../../gatsby-config'

const { contactEmail } = config.siteMetadata

const JobError = ({ error, showClose, handleClearError }) => (
  <Alert
    sx={{
      mt: '2rem',
      mb: '4rem',
      py: '1rem',
      bg: '#fff8c9',
      border: '1px solid',
      borderColor: '#faeb88',
      color: 'grey.9',
    }}
  >
    <ExclamationTriangle
      size="4rem"
      style={{
        margin: '0 1rem 0 0',
      }}
    />
    <Box sx={{ mr: '2rem' }}>
      <Heading as="h2" sx={{ m: 0 }}>
        Uh oh! There was an error!
      </Heading>
      {error ? (
        `The server says: ${error}`
      ) : (
        <>
          <Text sx={{ fontSize: 3 }}>
            Please try again. If that does not work, please{' '}
            <Link
              sx={{ textDecoration: 'underline' }}
              href={`mailto:${contactEmail}`}
            >
              Contact Us
            </Link>
            .
          </Text>
        </>
      )}
    </Box>

    {showClose ? (
      <Close
        ml="auto"
        sx={{
          flex: '0 0 auto',
          color: 'grey.9',
          border: '1px solid',
          borderColor: 'grey.9',
          borderRadius: '2rem',
        }}
        onClick={handleClearError}
      />
    ) : null}
  </Alert>
)

JobError.propTypes = {
  error: PropTypes.string,
  showClose: PropTypes.bool,
  handleClearError: PropTypes.func.isRequired,
}

JobError.defaultProps = {
  showClose: true,
  error: null,
}

export default JobError
