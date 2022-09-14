import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Checkbox, Label } from 'theme-ui'

import { InfoTooltip } from 'components/tooltip'

const Dataset = ({ id, name, description, selected, disabled, onChange }) => {
  const handleToggle = useCallback(() => {
    onChange(id)
  }, [id, onChange])

  return (
    <Flex sx={{ alignItems: 'center' }}>
      <Box sx={{ flex: '0 0 auto' }}>
        <Label
          sx={{
            cursor: 'pointer',
            border: '2px solid transparent',
            pr: '0.25rem',
            '&:focus-within': {
              border: '2px dashed',
              borderColor: 'highlight',
            },
          }}
        >
          <Checkbox
            readOnly={false}
            checked={selected}
            onChange={handleToggle}
            sx={{
              'input:focus ~ &': {
                backgroundColor: 'transparent',
              },
            }}
          />
          {name}
        </Label>
      </Box>
      <Box>
        <InfoTooltip content={description} />
      </Box>
    </Flex>
  )
}

Dataset.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  selected: PropTypes.bool,
  disabled: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

Dataset.defaultProps = {
  selected: true,
  disabled: false,
}

export default Dataset
