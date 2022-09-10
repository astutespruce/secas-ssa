import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'

import { Box, Container, Flex } from 'theme-ui'

import UploadContainer from './UploadContainer'
import SelectAttribute from './SelectAttribute'
import SelectDatasets from './SelectDatasets'
import Steps from './Steps'

const steps = [
  { id: 'upload', label: 'Upload Population Units', shortLabel: 'Upload' },
  {
    id: 'selectAttribute',
    label: 'Identify attribute that identifies unique population units',
    shortLabel: 'Identify attribute',
  },
  {
    id: 'selectDatasets',
    label: 'Select factors to include in report',
    shortLabel: 'Select factors',
  },
  { id: 'download', label: 'Download report', shortLabel: 'Download report' },
]

const ReportWorkflow = () => {
  const [{ stepIndex }, setState] = useState({ stepIndex: 0 })

  const handleStepClick = useCallback(
    (newIndex) => {
      setState((prevState) => ({ ...prevState, stepIndex: newIndex }))
    },
    [setState]
  )

  let stepContent = null

  switch (steps[stepIndex].id) {
    case 'upload': {
      stepContent = <UploadContainer />
      break
    }
    case 'selectAttribute': {
      // TODO: pass attributes from API
      stepContent = <SelectAttribute />
      break
    }
    case 'selectFactors': {
      // TODO: pass dataset state from API
      stepContent = <SelectDatasets />
      break
    }
    default: {
      break
    }
  }

  return (
    <Container>
      <Box sx={{ mt: '0.5rem', mb: '2rem' }}>
        <Steps steps={steps} index={stepIndex} onClick={handleStepClick} />
      </Box>

      {stepContent}
    </Container>
  )
}

export default ReportWorkflow
