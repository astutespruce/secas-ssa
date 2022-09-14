import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Flex,
  Grid,
  Paragraph,
  Checkbox,
  Heading,
  Divider,
  Button,
  Text,
} from 'theme-ui'

import { useDatasets } from 'components/data'

import Category from './Category'

const SelectDatasets = ({ availableDatasets }) => {
  const { categories, datasets } = useDatasets()

  // FIXME
  window.datasets = datasets

  const [selectedDatasets, setSelectedDatasets] = useState(
    Object.keys(datasets).reduce(
      (prev, id) => Object.assign(prev, { [id]: true }),
      {}
    )
  )

  // set all categories open by default
  const [openCategories, setOpenCategories] = useState(
    categories.reduce((prev, { id }) => Object.assign(prev, { [id]: true }), {})
  )

  const handleCategoryToggle = useCallback((id) => {
    setOpenCategories((prevOpen) => ({
      ...prevOpen,
      [id]: !prevOpen[id],
    }))
  }, [])

  const onDatasetChange = useCallback(
    (id) => {
      console.log('toggle dataset', id)
      setSelectedDatasets((prevState) => ({
        ...prevState,
        [id]: !prevState[id],
      }))
    },

    []
  )

  const handleSelectAll = useCallback(
    () => {
      console.log('selectAll')
      // only available datasets can be toggled on
      setSelectedDatasets(() =>
        Object.keys(datasets).reduce(
          (prev, id) => Object.assign(prev, { [id]: availableDatasets[id] }),
          {}
        )
      )
    },
    // deliberately ignoring datasets since those don't change after mount
    [availableDatasets]
  )

  const handleSelectNone = useCallback(
    () => {
      console.log('selectNone')
      setSelectedDatasets(() =>
        Object.keys(datasets).reduce(
          (prev, id) => Object.assign(prev, { [id]: false }),
          {}
        )
      )
    },
    // deliberately ignoring datasets since those don't change after mount
    [availableDatasets]
  )

  console.log('dataset state', selectedDatasets)

  return (
    <Grid columns={[0, 0, '1fr 2fr']} gap={5}>
      <Box>
        <Flex sx={{ alignItems: 'center', mb: '1rem' }}>
          <Box variant="boxes.step">2</Box>
          <Heading as="h3" sx={{ m: 0 }}>
            Select factors to include in report
          </Heading>
        </Flex>
        <Paragraph>
          This tool includes several standardized landscape-level datasets that
          help characterize different aspects of current and potential future
          conditions. Only those datasets that overlap with any of your
          population units are available for your analysis. Select any or all of
          these datasets on the right.
        </Paragraph>
      </Box>
      <Box>
        <Flex sx={{ justifyContent: 'space-between', mb: '0.5rem' }}>
          <Heading as="h4" sx={{ m: 0 }}>
            Available landscape-level factors:
          </Heading>
          <Flex sx={{ alignItems: 'center', cursor: 'pointer', color: 'link' }}>
            <Text onClick={handleSelectAll} sx={{ fontSize: 0 }}>
              select all
            </Text>
            <Text
              onClick={handleSelectNone}
              sx={{
                fontSize: 0,
                ml: '0.5rem',
                pl: '0.5rem',
                borderLeft: '1px solid',
              }}
            >
              select none
            </Text>
          </Flex>
        </Flex>

        {categories.map((category) => (
          <Category
            key={category.id}
            {...category}
            datasets={category.datasets.map(({ id, ...rest }) => ({
              id,
              ...rest,
              selected: selectedDatasets[id],
              disabled: !availableDatasets[id],
            }))}
            isOpen={openCategories[category.id]}
            onToggle={handleCategoryToggle}
            onChange={onDatasetChange}
          />
        ))}

        <Divider />
        <Flex sx={{ justifyContent: 'flex-end' }}>
          <Button as="button" variant="primary">
            Create report
          </Button>
        </Flex>
      </Box>
    </Grid>
  )
}

SelectDatasets.propTypes = {
  availableDatasets: PropTypes.objectOf(PropTypes.bool),
}

SelectDatasets.defaultProps = {
  // FIXME: remove and require
  availableDatasets: {
    nlcd_landcover: true,
    nlcd_impervious: true,
    urban: true,
    slr_depth: true,
    slr_proj: true,
    se_blueprint_coastalshorelinecondition: true,
    se_blueprint_resilientcoastalsites: true,
    se_blueprint_stablecoastalwetlands: true,
    se_blueprint_naturallandcoverinfloodplains: true,
    se_blueprint_networkcomplexity: true,
    se_blueprint_permeablesurface: true,
    se_blueprint_firefrequency: true,
    se_blueprint_intacthabitatcores: true,
    se_blueprint_resilientterrestrialsites: true,
  },
}

export default SelectDatasets
