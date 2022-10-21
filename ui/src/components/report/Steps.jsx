import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

const arrowCSS = {
  content: '""',
  display: 'block',
  position: 'absolute',
  width: '1.5rem',
  height: '1.5rem',
  right: '-0.8rem',
  top: '0.33rem',
  bg: 'grey.1',
  transform: 'rotate(45deg)',
  zIndex: 5,
  borderRight: '1px solid #FFF',
  borderTop: '1px solid #FFF',
}

const stepCSS = {
  flex: '1 1 100%',
  pr: '0.5rem',
  pl: '1rem',
  height: '2.25rem',
  position: 'relative',
  '&:after': {
    ...arrowCSS,
  },
  '&:not(:first-of-type)': {
    pl: '2rem',
  },
  '&:last-of-type': {
    '&:after': {
      display: 'none',
    },
  },
}

// enabled
const prevStepCSS = {
  ...stepCSS,
  cursor: 'pointer',
  bg: 'blue.2',
  color: 'grey.8',
  '&:after': {
    ...arrowCSS,
    bg: 'blue.2',
  },
}

const curStepCSS = {
  ...stepCSS,
  bg: 'blue.4',
  fontWeight: 'bold',
  cursor: 'default',
  '&:after': {
    ...arrowCSS,
    bg: 'blue.4',
  },
}

// disabled
const nextStepCSS = {
  ...stepCSS,
  cursor: 'not-allowed',
  bg: 'grey.1',
  color: 'grey.8',
}

const Steps = ({ steps, index, onClick }) => {
  const handleClick = useCallback(
    (newIndex) => () => {
      onClick(newIndex)
    },
    [onClick]
  )

  const getStepCSS = (i) => {
    if (i < index) {
      return prevStepCSS
    }

    if (i === index) {
      return curStepCSS
    }

    return nextStepCSS
  }

  return (
    <Flex
      sx={{
        alignItems: 'center',
        justifyContent: 'space-evenly',
        boxShadow: '1px 1px 3px #666',
      }}
    >
      {steps.map(({ id, label }, i) => (
        <Flex
          key={id}
          onClick={i < index ? handleClick(i) : null}
          sx={{
            alignItems: 'center',
            ...getStepCSS(i),
          }}
        >
          <Box
            variant="boxes.step"
            sx={{
              width: '1.5rem',
              height: '1.5rem',
              fontSize: '1rem',
              bg: i <= index ? 'grey.9' : 'grey.8',
            }}
          >
            {i + 1}
          </Box>{' '}
          <Text>{label}</Text>
        </Flex>
      ))}
    </Flex>
  )
}

Steps.propTypes = {
  steps: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      disabled: PropTypes.bool,
    })
  ).isRequired,
  index: PropTypes.number,
  onClick: PropTypes.func.isRequired,
}

Steps.defaultProps = {
  index: 0,
}

export default Steps
