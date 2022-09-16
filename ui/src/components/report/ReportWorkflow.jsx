import React, { useState, useCallback } from 'react'

import { Box, Container } from 'theme-ui'

import { useDatasets } from 'components/data'
import UploadContainer from './UploadContainer'
import SelectAttribute from './SelectAttribute'
import SelectDatasets from './SelectDatasets'
import Download from './Download'
import Steps from './Steps'

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
      attributes: {
        // FIXME:
        Foo: 3,
        Bar: 20,
      }, // set via API
      selectedAttribute: '', // blank indicates null
      openCategories: categories.reduce(
        (prev, { id }) => Object.assign(prev, { [id]: true }),
        {}
      ),
      // by default assume all are available and selected (as separate copies)
      availableDatasets: allDatasets, // set via API
      selectedDatasets: { ...allDatasets },
    }
  })

  const handleStepClick = useCallback((newIndex) => {
    setState((prevState) => ({ ...prevState, stepIndex: newIndex }))
  }, [])

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

  // FIXME: remove
  console.log(
    `step=${steps[stepIndex].id}\nattributes=${JSON.stringify(
      attributes
    )}\nselectedAttribute=${selectedAttribute}`
  )

  let stepContent = null

  switch (steps[stepIndex].id) {
    case 'upload': {
      stepContent = <UploadContainer />
      break
    }
    case 'selectAttribute': {
      // TODO: pass attributes from API
      stepContent = (
        <SelectAttribute
          attributes={attributes}
          selectedAttribute={selectedAttribute}
          onSelect={handleSelectAttribute}
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
        />
      )
      break
    }
    case 'download': {
      stepContent = <Download />
      break
    }
    default: {
      break
    }
  }

  return (
    <Container sx={{ px: ['1rem', '1rem', '1rem', 0], pb: '4rem' }}>
      <Box sx={{ mt: '0.5rem', mb: '2rem' }}>
        <Steps steps={steps} index={stepIndex} onClick={handleStepClick} />
      </Box>

      {stepContent}
    </Container>
  )
}

export default ReportWorkflow
