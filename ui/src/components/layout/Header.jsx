import React from 'react'
import { Flex, Heading } from 'theme-ui'

import { Link } from 'components/link'
import HeaderButtons from './HeaderButtons'

import { siteMetadata } from '../../../gatsby-config'

const { title } = siteMetadata

const Header = () => (
  <Flex
    as="header"
    sx={{
      minHeight: '2.5rem',
      flex: '0 0 auto',
      justifyContent: 'space-between',
      alignItems: 'center',
      py: '0.3rem',
      pl: '0.5rem',
      pr: '1rem',
      bg: 'primary',
      color: '#FFF',
      zIndex: 1,
      boxShadow: '0 2px 6px #000',
    }}
  >
    <>
      <Flex
        sx={{
          alignItems: 'center',
        }}
      >
        <Link
          to="/"
          sx={{
            textDecoration: 'none !important',
            display: 'block',
            color: '#FFF',
          }}
        >
          <Flex
            sx={{
              flexWrap: 'wrap',
              alignItems: ['flex-start', 'flex-start', 'baseline'],
              flexDirection: ['column', 'column', 'row'],
            }}
          >
            <Heading
              as="h1"
              sx={{
                fontWeight: 400,
                fontSize: ['10px', 1, 4],
                lineHeight: 1,
                m: 0,
                breakInside: 'avoid',
                flex: '0 1 auto',
              }}
            >
              {title}
            </Heading>
          </Flex>
        </Link>
      </Flex>

      <HeaderButtons />
    </>
  </Flex>
)

export default Header
