import React, { useCallback } from 'react'
import PropTypes from 'prop-types'

import { Box } from 'theme-ui'

import CategoryHeader from './CategoryHeader'
import Dataset from './Dataset'

const Category = ({
  id,
  label,
  color,
  borderColor,
  datasets,
  isOpen,
  onToggle,
  onToggleDatasets,
}) => {
  const handleToggle = useCallback(() => {
    onToggle(id)
  }, [id, onToggle])

  return (
    <Box>
      <CategoryHeader
        id={id}
        label={label}
        color={color}
        borderColor={borderColor}
        isOpen={isOpen}
        onClick={handleToggle}
      />
      {isOpen ? (
        <Box sx={{ pt: '0.5rem', pb: '2rem' }}>
          {datasets.map((dataset) => (
            <Dataset
              key={dataset.id}
              {...dataset}
              onToggle={onToggleDatasets}
            />
          ))}
        </Box>
      ) : null}
    </Box>
  )
}

Category.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
  datasets: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      selected: PropTypes.bool,
      disabled: PropTypes.bool,
    })
  ).isRequired,
  isOpen: PropTypes.bool,
  onToggle: PropTypes.func.isRequired,
  onToggleDatasets: PropTypes.func.isRequired,
}

Category.defaultProps = {
  isOpen: true,
}

export default Category
