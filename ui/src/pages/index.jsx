import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage as Image } from 'gatsby-plugin-image'
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

import { Credits, HeaderImage } from 'components/image'
import { SEO, Layout } from 'components/layout'
import { Link, OutboundLink } from 'components/link'

import { siteMetadata } from '../../gatsby-config'

const { title } = siteMetadata

const IndexPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    photo1: {
      childImageSharp: { gatsbyImageData: photo1 },
    },
    photo2: {
      childImageSharp: { gatsbyImageData: photo2 },
    },
    photo3: {
      childImageSharp: { gatsbyImageData: photo3 },
    },
    photo4: {
      childImageSharp: { gatsbyImageData: photo4 },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title={title}
      subtitle="Supporting species status assessments using standardized landscape-level data"
      image={headerImage}
      credits={{
        author: 'Robert Thiemann',
        url: 'https://unsplash.com/photos/1bj4WGNDFHw',
      }}
      caption="Great Smokey Mountains National Park"
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
        <Grid columns="2fr 1fr" gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ mb: '1.5rem' }}>
              <Flex sx={{ alignItems: 'center' }}>
                <Box variant="boxes.step">1</Box>
                <Heading as="h3" sx={{ m: 0 }}>
                  Upload a shapefile with population units
                </Heading>
              </Flex>
              <Paragraph sx={{ ml: '3.9rem' }}>
                The shapefile should contain one record for each population unit
                to be analyzed.
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
                You will need to identify the attribute (data column) that
                uniquely identifies each population unit.
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
                You can choose from terrestrial, freshwater, and coastal
                indicators, land cover trends, and projected sea-level rise and
                urbanization.
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
          </Box>
          <Box>
            <Image image={photo4} alt="Key Deer at Key Deer NWR" />
            <Credits
              caption="Key Deer at Key Deer NWR"
              author="U.S. Fish and Wildlife Service Southeast Region"
              url="https://flickr.com/photos/usfwssoutheast/4971502145/in/photostream/"
            />
          </Box>
        </Grid>

        <Box sx={{ mt: '2rem' }}>TODO: screenshots showing example reports</Box>
      </Box>

      <Divider />

      <Box sx={{ my: '2rem' }}>
        <Heading as="h2">What datasets are available?</Heading>
        <Paragraph sx={{ fontSize: 3, my: '0.5rem' }}>
          This tool includes the following datasets:
        </Paragraph>
        <Grid columns="2fr 1fr" gap={5}>
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
              Current and projected future urban development areas by decade
              2020 to 2100 created by the FUTURES project
            </li>
            <li>
              Areas impacted by sea-level rise up to 10 feet calculated by the{' '}
              <OutboundLink to="https://coast.noaa.gov/slrdata/">
                National Oceanic & Atmospheric Administration
              </OutboundLink>
            </li>
            <li>
              Projected future sea-level rise depths by decade 2020 to 2100
              based on the National Oceanic & Atmospheric Administration&apos;s{' '}
              <OutboundLink to="https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report.html">
                2022 Sea Level Rise Technical Report
              </OutboundLink>
            </li>
          </Box>

          <Box>
            <Image
              image={photo2}
              alt="Prescribed fire at Mississippi Sandhill Crane NWR 2004"
            />
            <Credits
              caption="Prescribed fire at Mississippi Sandhill Crane NWR 2004"
              author="U.S. Fish and Wildlife Service Southeast Region"
              url="https://flickr.com/photos/usfwssoutheast/5142785872/"
            />
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '1rem' }}>
          To learn more about how datasets were prepared for use in this tool,
          please see the <Link to="/methods">Methods</Link> page.
        </Paragraph>
      </Box>

      <Divider />

      <Box sx={{ mt: '3rem', mb: '2rem' }}>
        <Grid columns="1fr 2fr" gap={5}>
          <Box>
            <Image
              image={photo3}
              alt="Looking for mussels on the Little Tennessee River"
            />
            <Credits
              caption="Looking for mussels on the Little Tennessee River"
              author="Gary Peeples / U.S. Fish and Wildlife Service Southeast Region"
              url="https://flickr.com/photos/usfwssoutheast/5149490458/"
            />
          </Box>
          <Box>
            <Heading as="h2">Disclaimer</Heading>
            <Paragraph>
              Use of this tool is not required for the development of SSAs. The
              summaries provided here are intended to simplify the assessment of
              how exposed populations of fish, wildlife & plants are to various
              influences and stressors (list will grow over time). The biologist
              performing the assessment must determine if the influences and
              stressors provided here are relevant to the resiliency,
              redundancy, and representation of their focal species, as well as
              whether the spatial data summarized here is the most appropriate
              (i.e., best-available) for their species.
            </Paragraph>
          </Box>
        </Grid>
      </Box>

      <Divider sx={{ borderBottomWidth: '0.25rem' }} />

      <Box sx={{ mt: '2rem', pb: '6rem' }}>
        <Heading as="h2">Credits</Heading>
        <Grid columns="2fr 1fr" gap={5}>
          <Box>
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
          <Box>
            <Image
              image={photo1}
              alt="Endangered mussels for release in the Powell River"
            />
            <Credits
              caption="Endangered mussels for release in the Powell River"
              author="Gary Peeples / U.S. Fish and Wildlife Service Southeast Region"
              url="https://flickr.com/photos/usfwssoutheast/8027062941/in/photostream/"
            />
          </Box>
        </Grid>
      </Box>
    </Container>
  </Layout>
)

export const pageQuery = graphql`
  query IndexPageQuery {
    headerImage: file(
      relativePath: { eq: "robert-thiemann-1bj4WGNDFHw-unsplash.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    photo1: file(relativePath: { eq: "8027062941_e8fcdf1247_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 640
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    photo2: file(relativePath: { eq: "5142785872_b34caf59e3_h.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 640
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    photo3: file(relativePath: { eq: "5149490458_5ffcce6c44_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 640
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    photo4: file(relativePath: { eq: "4971502145_03d6b78f28_o.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 640
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
    photo1: PropTypes.object.isRequired,
    photo2: PropTypes.object.isRequired,
    photo3: PropTypes.object.isRequired,
    photo4: PropTypes.object.isRequired,
  }).isRequired,
}

export default IndexPage

export const Head = () => <SEO />
