import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import { Layout, SEO } from 'components/layout'
import { HeaderImage } from 'components/image'
import { ReportWorkflow } from 'components/report'

const ReportPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title="Create a Population-level Landscape Status Report"
      image={headerImage}
      credits={{
        author: 'U.S. Fish and Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/26871026541/',
      }}
      caption="Black Skimmers"
      height="16rem"
      maxHeight="16rem"
      minHeight="16rem"
      backgroundPosition="bottom"
    />

    <ReportWorkflow />
  </Layout>
)

export const pageQuery = graphql`
  query ReportPageQuery {
    headerImage: file(relativePath: { eq: "5494812678_3849557155_o.jpg" }) {
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

ReportPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export default ReportPage

export const Head = () => <SEO title="Custom Report" />
