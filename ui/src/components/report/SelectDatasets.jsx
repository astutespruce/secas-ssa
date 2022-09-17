import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Flex,
  Grid,
  Paragraph,
  Heading,
  Divider,
  Button,
  Text,
} from 'theme-ui'

import Category from './Category'

const SelectDatasets = ({
  categories,
  openCategories,
  availableDatasets,
  selectedDatasets,
  onToggleCategory,
  onToggleDatasets,
}) => {
  const handleSelectAll = useCallback(() => {
    onToggleDatasets(
      Object.keys(availableDatasets).reduce(
        (prev, id) => Object.assign(prev, { [id]: availableDatasets[id] }),
        {}
      )
    )
  }, [availableDatasets, onToggleDatasets])

  const handleSelectNone = useCallback(
    () => {
      onToggleDatasets(
        Object.keys(selectedDatasets).reduce(
          (prev, id) => Object.assign(prev, { [id]: false }),
          {}
        )
      )
    },
    // deliberately ignoring datasets since those don't change after mount
    [selectedDatasets, onToggleDatasets]
  )

  return (
    <Grid columns={[0, 0, '1fr 2fr']} gap={5}>
      <Box>
        <Flex sx={{ alignItems: 'center', mb: '1rem' }}>
          <Box variant="boxes.step">3</Box>
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
            onToggle={onToggleCategory}
            onToggleDatasets={onToggleDatasets}
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
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      borderColor: PropTypes.string.isRequired,
      datasets: PropTypes.arrayOf(PropTypes.object).isRequired,
    })
  ).isRequired,
  openCategories: PropTypes.objectOf(PropTypes.bool).isRequired,
  availableDatasets: PropTypes.objectOf(PropTypes.bool).isRequired,
  selectedDatasets: PropTypes.objectOf(PropTypes.bool).isRequired,
  onToggleCategory: PropTypes.func.isRequired,
  onToggleDatasets: PropTypes.func.isRequired,
}

export default SelectDatasets
