import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Container, Flex, Box } from 'theme-ui'

import { Layout, SEO } from 'components/layout'
import { HeaderImage } from 'components/image'

const MethodsPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title="Data Preparation Methods"
      image={headerImage}
      credits={{
        author: 'U.S. Fish and Wildlife Service Southeast Region',
        url: 'https://flickr.com/photos/usfwssoutheast/5142785230/in/photostream/',
      }}
      caption="Prescribed burn at Florida Panther NWR"
      height="12rem"
      maxHeight="12rem"
      minHeight="12rem"
    />

    <Container>TODO: write methods...</Container>
  </Layout>
)

export const pageQuery = graphql`
  query MethodsPageQuery {
    headerImage: file(relativePath: { eq: "5142785230_69f04b6562_o.jpg" }) {
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

MethodsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export default MethodsPage

export const Head = () => <SEO title="Methods" />
