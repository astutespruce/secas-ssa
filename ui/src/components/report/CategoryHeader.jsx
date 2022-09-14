import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Heading, Image } from 'theme-ui'
import { CaretDown, CaretRight } from '@emotion-icons/fa-solid'

const CategoryHeader = ({ id, isOpen, label, color, borderColor, onClick }) => {
  // eslint-disable-next-line global-require, import/no-dynamic-require
  const icon = require(`images/${id}.svg`).default

  return (
    <Box
      onClick={onClick}
      sx={{
        bg: color,
        py: ['1rem', '0.5rem'],
        px: '1rem',
        borderBottom: '1px solid',
        borderBottomColor: borderColor,
        cursor: 'pointer',
      }}
    >
      <Flex sx={{ alignItems: 'center' }}>
        <Box sx={{ flex: '0 0 auto', mr: '0.25em' }}>
          {isOpen ? <CaretDown size="1.5em" /> : <CaretRight size="1.5em" />}
        </Box>

        <Image
          src={icon}
          sx={{
            width: '2.5em',
            height: '2.5em',
            mr: '0.5em',
            bg: '#FFF',
            borderRadius: '2.5em',
          }}
        />

        <Heading as="h4">{label}</Heading>
      </Flex>
    </Box>
  )
}

CategoryHeader.propTypes = {
  id: PropTypes.string.isRequired,
  isOpen: PropTypes.bool,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

CategoryHeader.defaultProps = {
  isOpen: true,
}

export default CategoryHeader
