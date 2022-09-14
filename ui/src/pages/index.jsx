import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import {
  Box,
  Flex,
  Grid,
  Heading,
  Button,
  Paragraph,
  Container,
  Divider,
  Text,
} from 'theme-ui'
import { FileAlt } from '@emotion-icons/fa-regular'

import { HeaderImage } from 'components/image'
import { SEO, Layout } from 'components/layout'
import { Link, OutboundLink } from 'components/link'

import { siteMetadata } from '../../gatsby-config'

const { title } = siteMetadata

const IndexPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title={title}
      subtitle="Supporting species status assessments using standardized landscape-level data"
      image={headerImage}
      credits={{
        author: 'U.S. Fish and Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/26871026541/',
      }}
      caption="Black Skimmers"
      height="10rem"
      maxHeight="10rem"
    />
    <Container>
      <Box sx={{ mt: '2rem', mb: '4rem' }}>
        <Paragraph sx={{ fontSize: '1.5rem' }}>
          <OutboundLink to="https://www.fws.gov/project/species-status-assessment">
            Species Status Assessments
          </OutboundLink>{' '}
          (SSAs) are used by U.S. Fish and Wildlife Service to make decisions
          under the Endangered Species Act. SSAs depend on the latest available
          data that describe current and projected future landscape conditions
          that may influence the persistence of populations of a species.
          <br />
          <br />
          This tool creates reports that help SSA analysts evaluate the
          potential influences of landscape-level factors. These reports include
          population-level summaries of standardized landscape-level data,
          including indicators of habitat quality and projections of future
          urbanization and sea-level rise.
        </Paragraph>
        <Flex sx={{ justifyContent: 'center', my: '2rem' }}>
          <Link to="/report">
            <Button
              sx={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center' }}
            >
              <FileAlt size="1em" />
              <Text sx={{ ml: '0.5rem' }}>Create Custom Report</Text>
            </Button>
          </Link>
        </Flex>
      </Box>

      <Divider />

      <Box sx={{ mt: '2rem', mb: '4rem' }}>
        <Heading as="h1">How to create a report</Heading>
        <Box sx={{ my: '1.5rem' }}>
          <Flex sx={{ alignItems: 'center' }}>
            <Box variant="boxes.step">1</Box>
            <Heading as="h3" sx={{ m: 0 }}>
              Upload a shapefile with population units
            </Heading>
          </Flex>
          <Paragraph sx={{ ml: '3.9rem' }}>
            The shapefile should contain one record for each population unit to
            be analyzed.
          </Paragraph>
        </Box>

        <Box sx={{ my: '1.5rem' }}>
          <Flex sx={{ alignItems: 'center' }}>
            <Box variant="boxes.step">2</Box>
            <Heading as="h3" sx={{ m: 0 }}>
              Identify population unit attribute
            </Heading>
          </Flex>
          <Paragraph sx={{ ml: '3.9rem' }}>
            You will need to identify the attribute (data column) that uniquely
            identifies each population unit.
          </Paragraph>
        </Box>

        <Box sx={{ my: '1.5rem' }}>
          <Flex sx={{ alignItems: 'center' }}>
            <Box variant="boxes.step">3</Box>
            <Heading as="h3" sx={{ m: 0 }}>
              Choose landscape-level factors
            </Heading>
          </Flex>
          <Paragraph sx={{ ml: '3.9rem' }}>
            You can choose from terrestrial, freshwater, and coastal indicators,
            land cover trends, and projected sea-level rise and urbanization.
          </Paragraph>
        </Box>

        <Box sx={{ my: '1.5rem' }}>
          <Flex sx={{ alignItems: 'center' }}>
            <Box variant="boxes.step">4</Box>
            <Heading as="h3" sx={{ m: 0 }}>
              Download report spreadsheet
            </Heading>
          </Flex>
          <Paragraph sx={{ ml: '3.9rem' }}>
            The tool will create a spreadsheet with one sheet per factor and
            additional details about the datasets used in the analysis.
          </Paragraph>
        </Box>

        <Box sx={{ mt: '2rem' }}>TODO: screenshots showing example reports</Box>
      </Box>

      <Divider />

      <Box sx={{ my: '2rem' }}>
        <Heading as="h2">What datasets are available?</Heading>
        <Paragraph sx={{ fontSize: 3, my: '0.5rem' }}>
          This tool includes the following datasets:
        </Paragraph>
        <Box as="ul" sx={{ fontSize: 2 }}>
          <li>
            Terrestrial and freshwater indicators created as part of the
            Southeast Blueprint 2022, including
            <Grid columns={3} gap={3} sx={{ mt: '0.5rem', mb: '1rem' }}>
              <Box
                sx={{
                  px: '1rem',
                  bg: 'grey.0',
                  borderLeft: '2px solid',
                  borderLeftColor: 'grey.2',
                }}
              >
                <Text sx={{ fontStyle: 'italic' }}>Terrestrial</Text>
                <Box as="ul">
                  <li>fire frequency</li>
                  <li>intact habitat cores</li>
                  <li>resilient terrestrial sites</li>
                </Box>
              </Box>
              <Box
                sx={{
                  px: '1rem',
                  bg: 'grey.0',
                  borderLeft: '2px solid',
                  borderLeftColor: 'grey.2',
                }}
              >
                <Text sx={{ fontStyle: 'italic' }}>Freshwater</Text>
                <Box as="ul">
                  <li>aquatic network complexity</li>
                  <li>natural landcover in floodplains</li>
                  <li>permeable surface</li>
                </Box>
              </Box>
              <Box
                sx={{
                  px: '1rem',
                  bg: 'grey.0',
                  borderLeft: '2px solid',
                  borderLeftColor: 'grey.2',
                }}
              >
                <Text
                  sx={{
                    fontStyle: 'italic',
                  }}
                >
                  Coastal
                </Text>
                <Box as="ul">
                  <li>coastal shoreline condition</li>
                  <li>coastal resilient sites</li>
                  <li>stable coastal wetlands</li>
                </Box>
              </Box>
            </Grid>
          </li>
          <li>
            <OutboundLink to="https://www.usgs.gov/centers/eros/science/national-land-cover-database">
              National Land Cover Database 2001 - 2019: land cover and
              impervious surface
            </OutboundLink>
          </li>
          <li>
            Current and projected future urban development areas by decade 2020
            to 2100 created by the FUTURES project
          </li>
          <li>
            Areas impacted by sea-level rise up to 10 feet calculated by the{' '}
            <OutboundLink to="https://coast.noaa.gov/slrdata/">
              National Oceanic & Atmospheric Administration
            </OutboundLink>
          </li>
          <li>
            Projected future sea-level rise depths by decade 2020 to 2100 based
            on the National Oceanic & Atmospheric Administration&apos;s{' '}
            <OutboundLink to="https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report.html">
              2022 Sea Level Rise Technical Report
            </OutboundLink>
          </li>
        </Box>
        <Paragraph sx={{ mt: '1rem' }}>
          To learn more about how datasets were prepared for use in this tool,
          please see the <Link to="/methods">Methods</Link> page.
        </Paragraph>
      </Box>

      {/* <Divider /> */}

      <Box sx={{ my: '2rem', bg: 'blue.0', p: '1rem', borderRadius: '0.5rem' }}>
        <Heading as="h2">Disclaimer</Heading>
        <Paragraph>
          Use of this tool is not required for the development of SSAs. The
          summaries provided here are intended to simplify the assessment of how
          exposed populations of fish, wildlife & plants are to various
          influences and stressors (list will grow over time). The biologist
          performing the assessment must determine if the influences and
          stressors provided here are relevant to the resiliency, redundancy,
          and representation of their focal species, as well as whether the
          spatial data summarized here is the most appropriate (i.e.,
          best-available) for their species.
        </Paragraph>
      </Box>

      <Divider sx={{ borderBottomWidth: '0.25rem' }} />

      <Box sx={{ mt: '2rem', pb: '6rem' }}>
        <Heading as="h2">Credits</Heading>
        <Paragraph>
          This application was developed by{' '}
          <OutboundLink to="https://astutespruce.com">
            Astute Spruce, LLC
          </OutboundLink>{' '}
          in partnership with the U.S. Fish and Wildlife Service under the{' '}
          <OutboundLink to="http://secassoutheast.org/">
            Southeast Conservation Adaptation Strategy
          </OutboundLink>
          .
        </Paragraph>
      </Box>
    </Container>
  </Layout>
)

export const pageQuery = graphql`
  query IndexPageQuery {
    headerImage: file(relativePath: { eq: "26871026541_48a8096dd9_o.jpg" }) {
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

IndexPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export default IndexPage

export const Head = () => <SEO />
