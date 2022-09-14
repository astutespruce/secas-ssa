import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Flex, Heading } from 'theme-ui'
import { convertToBgImage } from 'gbimage-bridge'
import BackgroundImage from 'gatsby-background-image'

import { Layout, SEO } from 'components/layout'
import { Credits } from 'components/image'
import { hasWindow } from 'util/dom'

const NotFoundPage = ({
  data: {
    image: {
      childImageSharp: { gatsbyImageData: image },
    },
  },
}) => {
  if (!hasWindow) {
    // prevents initial load of this page for client routes
    return null
  }

  return (
    <Layout>
      <BackgroundImage
        {...convertToBgImage(image)}
        style={{
          height: '100%',
        }}
        alt=""
        preserveStackingContext
      >
        <Flex
          sx={{
            alignItems: 'center',
            flexDirection: 'column',
            height: '100%',
            flex: '1 1 auto',
            px: '1rem',
            pt: '4rem',
          }}
        >
          <Box
            sx={{
              p: '3rem',
              background: 'rgba(255,255,255,0.7)',
              borderRadius: '1rem',
              border: '1px solid',
              borderColor: 'grey.9',
              boxShadow: '1px 1px 6px #000',
            }}
          >
            <Heading as="h1" sx={{ color: '#000' }}>
              NOT FOUND
            </Heading>
            <Heading as="h2" sx={{ color: 'grey.9' }}>
              Sorry, we could not find what you were looking for here.
            </Heading>
          </Box>
        </Flex>
        <Credits
          author="G. Peeples / U.S. Fish and Wildlife Service Southeast Region"
          url="https://flickr.com/photos/usfwssoutheast/48754428566/"
          sx={{
            bg: 'rgba(0, 0, 0, 0.7)',
            py: '0.25rem',
            px: '1rem',
            color: '#FFF',
            position: 'absolute',
            bottom: 0,
            right: 0,
            '& a': {
              color: '#FFF',
            },
          }}
        />
      </BackgroundImage>
    </Layout>
  )
}

// image: https://flickr.com/photos/usfwssoutheast/48754428566/

export const pageQuery = graphql`
  query NotFoundPageQuery {
    image: file(relativePath: { eq: "48754428566_d34b348ac3_o.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

NotFoundPage.propTypes = {
  data: PropTypes.shape({
    image: PropTypes.object.isRequired,
  }).isRequired,
}

export default NotFoundPage

export const Head = () => <SEO title="Not Found" />
