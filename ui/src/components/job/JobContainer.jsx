import React, { useState, useCallback, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Button, Divider, Heading, Flex, Progress, Text } from 'theme-ui'

import { captureException } from 'util/log'
import { submitJob } from './api'
import JobError from './JobError'

const JobContainer = ({ data, path, defaultMessage, onCancel, onSuccess }) => {
  const [{ progress, message, error }, setState] = useState({
    progress: 0,
    message: defaultMessage,
    error: null,
  })

  const doSubmitJob = useCallback(async () => {
    try {
      // upload file and update progress
      const { result, error: jobError } = await submitJob(
        path,
        data,
        ({
          progress: nextProgress,
          message: nextMessage = null,
          errors: nextErrors = null,
        }) => {
          setState(
            ({ message: prevMessage, errors: prevErrors, ...prevState }) => ({
              ...prevState,
              progress: nextProgress,
              message: nextMessage || prevMessage || defaultMessage,
              errors: nextErrors || prevErrors,
            })
          )
        }
      )

      if (jobError) {
        // eslint-disable-next-line no-console
        console.error(jobError)

        setState((prevState) => ({
          ...prevState,
          progress: 0,
          message: null,
          error: jobError,
        }))
        return
      }

      // job completed successfully, return
      setState((prevState) => ({
        ...prevState,
        progress: 100,
        message: 'Done!',
      }))

      onSuccess(result)
    } catch (ex) {
      captureException('job failed', ex)
      // eslint-disable-next-line no-console
      console.error(`Caught unhandled error from job: ${path}`, ex)

      setState((prevState) => ({
        ...prevState,
        progress: 0,
        message: null,
        error: '',
      }))
    }
  }, [path, data, defaultMessage, onSuccess])

  // create job on mount
  useEffect(() => {
    doSubmitJob()
  }, [doSubmitJob])

  const handleCancel = useCallback(() => {
    // reset state
    setState(() => ({
      progress: 0,
      message: defaultMessage,
      error: null,
    }))
    onCancel()
  }, [defaultMessage, onCancel])

  if (error !== null) {
    return (
      <>
        <JobError
          error={error}
          showClose={false}
          handleClearError={handleCancel}
        />
        <Divider />
        <Flex sx={{ justifyContent: 'center' }}>
          <Button onClick={handleCancel}>Try again</Button>
        </Flex>
      </>
    )
  }

  return (
    <>
      <Heading as="h3" sx={{ mb: '0.5rem' }}>
        {message}
      </Heading>

      <Flex sx={{ alignItems: 'center' }}>
        <Progress variant="styles.progress" max={100} value={progress} />
        <Text sx={{ ml: '1rem' }}>{progress}%</Text>
      </Flex>
    </>
  )
}

JobContainer.propTypes = {
  data: PropTypes.object,
  path: PropTypes.string.isRequired,
  defaultMessage: PropTypes.string,
  onCancel: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
}

JobContainer.defaultProps = {
  data: null,
  defaultMessage: null,
}

export default JobContainer
