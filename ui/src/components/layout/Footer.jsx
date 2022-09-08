import React from 'react'
import { Box, Flex, Text } from 'theme-ui'
import { Envelope, ExclamationCircle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import { ContactModal, ReportProblemModal } from 'components/modal'

const modalLinkCSS = {
  cursor: 'pointer',
  '&:hover': {
    textDecoration: 'underline',
  },
}

const Footer = () => (
  <Flex
    sx={{
      alignItems: 'baseline',
      justifyContent: 'space-between',
      fontSize: 1,
      lineHeight: 1,
      px: '0.5em',
      py: '0.25em',
      bg: 'blue.9',
      color: '#FFF',
      a: {
        color: '#FFF',
      },
    }}
  >
    <Box>
      <ContactModal>
        <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
          <Envelope size="1em" style={{ marginRight: '0.5em' }} />
          <Text sx={modalLinkCSS}>Contact Us</Text>
        </Flex>
      </ContactModal>
    </Box>

    <Box
      sx={{
        display: ['none', 'none', 'unset'],
        borderLeft: '1px solid #FFF',
        height: '1em',
      }}
    />

    <Box sx={{ display: ['none', 'none', 'unset'] }}>
      <ReportProblemModal>
        <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
          <ExclamationCircle size="1em" style={{ marginRight: '0.5em' }} />
          <Text sx={modalLinkCSS}>Report a Problem</Text>
        </Flex>
      </ReportProblemModal>
    </Box>

    <Box
      sx={{
        display: ['none', 'none', 'none', 'unset'],
        borderLeft: '1px solid #FFF',
        height: '1em',
      }}
    />

    <Text sx={{ fontSize: 0, ml: '0.5em' }}>
      Created by U.S. Fish and Wildlife Service and{' '}
      <OutboundLink to="https://astutespruce.com">Astute Spruce</OutboundLink>
    </Text>
  </Flex>
)

export default Footer
