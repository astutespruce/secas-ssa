import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Checkbox, Label, Text } from 'theme-ui'

import { InfoTooltip } from 'components/tooltip'

const Dataset = ({ id, name, description, selected, disabled, onToggle }) => {
  const handleToggle = () => {
    onToggle({ [id]: !selected })
  }

  return (
    <Flex sx={{ alignItems: 'center' }}>
      <Box sx={{ flex: '0 0 auto' }}>
        {/* {disabled ? (
          <Text sx={{ fontStyle: 'italic', color: 'grey.7' }}>
            {name} (does not overlap analysis units)
          </Text>
        ) : ( */}
        <Label
          sx={{
            cursor: 'pointer',
            border: '2px solid transparent',
            pr: '0.25rem',
            fontStyle: disabled ? 'italic' : 'inherit',
            color: disabled ? 'grey.7' : 'inherit',
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
          {disabled ? ' (not present)' : null}
        </Label>
        {/* )} */}
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
  onToggle: PropTypes.func.isRequired,
}

Dataset.defaultProps = {
  selected: true,
  disabled: false,
}

export default Dataset
