import React, { useState, useCallback } from 'react'

import { Box, Container } from 'theme-ui'

import { useDatasets } from 'components/data'
import Steps from './Steps'
import Upload from './Upload'
import SelectAttribute from './SelectAttribute'
import SelectDatasets from './SelectDatasets'
import Download from './Download'

const steps = [
  { id: 'upload', label: 'Upload' },
  {
    id: 'selectAttribute',
    label: 'Identify attribute',
  },
  {
    id: 'selectDatasets',
    label: 'Select factors',
  },
  { id: 'download', label: 'Download report' },
]

const ReportWorkflow = () => {
  const { categories, datasets } = useDatasets()

  const [
    {
      stepIndex,
      uuid, // for tracking unique upload
      attributes,
      selectedAttribute,
      openCategories,
      availableDatasets,
      selectedDatasets,
    },
    setState,
  ] = useState(() => {
    const allDatasets = Object.keys(datasets).reduce(
      (prev, id) => Object.assign(prev, { [id]: true }),
      {}
    )

    return {
      stepIndex: 0,
      uuid: null,
      attributes: {}, // set via API
      selectedAttribute: '', // blank indicates no selected attribute
      openCategories: categories.reduce(
        (prev, { id }) => Object.assign(prev, { [id]: true }),
        {}
      ),
      // by default assume all are available and selected (as separate copies)
      availableDatasets: allDatasets, // set via API
      selectedDatasets: { ...allDatasets },
    }
  })

  // TODO: depending on step, may need to reset state
  const handleStepClick = useCallback((newIndex) => {
    setState((prevState) => ({ ...prevState, stepIndex: newIndex }))
  }, [])

  const handleUploadFileSuccess = useCallback(
    ({ uuid: uploadUuid, fields = {}, available_datasets = {} }) => {
      setState((prevState) => ({
        ...prevState,
        stepIndex: 1,
        uuid: uploadUuid,
        attributes: fields,
        availableDatasets: available_datasets,
        selectedDatasets: { ...available_datasets },
      }))
    },
    []
  )

  const handleToggleCategory = useCallback((id) => {
    setState(({ openCategories: prevOpenCategories, ...prevState }) => ({
      ...prevState,
      openCategories: {
        ...prevOpenCategories,
        [id]: !prevOpenCategories[id],
      },
    }))
  }, [])

  const handleToggleDatasets = useCallback((updatedDatasets) => {
    setState(({ selectedDatasets: prevSelectedDatasets, ...prevState }) => ({
      ...prevState,
      selectedDatasets: {
        ...prevSelectedDatasets,
        ...updatedDatasets,
      },
    }))
  }, [])

  const handleSelectAttribute = useCallback((attribute) => {
    setState((prevState) => ({
      ...prevState,
      selectedAttribute: attribute,
    }))
  }, [])

  const handleStartOver = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      stepIndex: 0,
      uuid: null,
      selectedAttribute: '',
      attributes: {},
      availableDatasets: {},
      selectedDatasets: {},
    }))
  }, [])

  const handleSelectAttributeNext = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      stepIndex: 2,
    }))
  }, [])

  const handleSelectDatasetsBack = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      stepIndex: 1,
    }))
  }, [])

  const handleCreateReport = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      stepIndex: 3,
    }))
  }, [])

  let stepContent = null

  switch (steps[stepIndex].id) {
    case 'upload': {
      stepContent = <Upload onSuccess={handleUploadFileSuccess} />
      break
    }
    case 'selectAttribute': {
      stepContent = (
        <SelectAttribute
          attributes={attributes}
          selectedAttribute={selectedAttribute}
          onSelect={handleSelectAttribute}
          onBack={handleStartOver}
          onNext={handleSelectAttributeNext}
        />
      )
      break
    }
    case 'selectDatasets': {
      stepContent = (
        <SelectDatasets
          categories={categories}
          openCategories={openCategories}
          availableDatasets={availableDatasets}
          selectedDatasets={selectedDatasets}
          onToggleCategory={handleToggleCategory}
          onToggleDatasets={handleToggleDatasets}
          onBack={handleSelectDatasetsBack}
          onNext={handleCreateReport}
        />
      )
      break
    }
    case 'download': {
      stepContent = (
        <Download
          uuid={uuid}
          selectedAttribute={selectedAttribute}
          selectedDatasets={selectedDatasets}
          onCancel={handleStartOver}
        />
      )
      break
    }
    default: {
      break
    }
  }

  return (
    <Container sx={{ px: ['1rem', '1rem', '1rem', 0], pb: '4rem' }}>
      <Box sx={{ mt: '1.5rem', mb: '2rem' }}>
        <Steps steps={steps} index={stepIndex} onClick={handleStepClick} />
      </Box>

      <Box sx={{ pt: '2rem' }}>{stepContent}</Box>
    </Container>
  )
}

export default ReportWorkflow
