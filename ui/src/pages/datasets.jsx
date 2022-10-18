import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import {
  Container,
  Flex,
  Box,
  Heading,
  Paragraph,
  Divider,
  Text,
} from 'theme-ui'
import { ExternalLinkAlt } from '@emotion-icons/fa-solid'

import { Layout, SEO } from 'components/layout'
import { OutboundLink } from 'components/link'
import { HeaderImage } from 'components/image'

import { useDatasets } from 'components/data'

const MethodsPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  },
}) => {
  const { categories } = useDatasets()

  return (
    <Layout>
      <HeaderImage
        title="Dataset details"
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

      <Container sx={{ pb: '4rem' }}>
        <Box>
          <Heading as="h3" sx={{ mb: '0.5rem' }}>
            Table of contents
          </Heading>
          <Box>
            <ul>
              <li>
                <a href="#GeneralInformation">General information</a>
              </li>
              {categories.map((category) => (
                <li key={category.id}>
                  <a href={`#${category.id}Section`}>{category.label}</a>
                  <ul>
                    {category.datasets.map(({ id, name }) => (
                      <li key={id}>
                        <a href={`#${id}Section`}>{name}</a>
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          </Box>
        </Box>

        <Divider />

        <Heading id="GeneralInformation" as="h2">
          General information
        </Heading>
        <Paragraph>
          The latest available versions of each dataset were obtained for use in
          this tool. Each dataset was standardized to a 30 meter resolution that
          is aligned with the Southeast Blueprint, in the CONUS Albers (NAD83)
          spatial projection.
          <br />
          <br />
          Analysis unit boundaries uploaded by the user are rasterized to match
          these rasters, which means that the resulting data queried from each
          dataset is an approximation based on these rasterized boundaries.
          Analysis units that are very spatially detailed, small, or highly
          linear may not be approximated as well as analysis units that are
          fairly large or less detailed.
        </Paragraph>

        {categories.map((category) => (
          <Box key={category.id}>
            <Divider />
            <Heading id={`${category.id}Section`} as="h2" sx={{ mb: '2rem' }}>
              {category.label}
            </Heading>
            <Box>
              {category.datasets.map(
                ({
                  id,
                  name,
                  description,
                  methods,
                  source,
                  date,
                  url,
                  citation,
                }) => (
                  <Box key={id} sx={{ mb: '3rem' }}>
                    <Heading id={`${id}Section`} as="h3" sx={{ mb: '0.25rem' }}>
                      {name}
                    </Heading>
                    <Box
                      sx={{
                        fontSize: 2,
                        borderTop: '1px solid',
                        borderTopColor: 'grey.1',
                        borderBottom: '1px solid',
                        borderBottomColor: 'grey.1',
                        pb: '0.25rem',
                        bg: 'grey.0',
                        px: '0.5rem',
                        py: '0.25rem',
                        lineHeight: 1,
                      }}
                    >
                      <Flex sx={{ justifyContent: 'space-between' }}>
                        <Box>
                          {url ? (
                            <Flex>
                              <Box sx={{ mr: '0.25rem' }}>
                                <OutboundLink to={url}>{source}</OutboundLink>
                              </Box>
                              <Box
                                sx={{
                                  color: 'link',
                                  flex: '0 0 auto',
                                  opacity: 0.5,
                                  mt: '-2px',
                                }}
                              >
                                <ExternalLinkAlt size="0.75em" />
                              </Box>
                            </Flex>
                          ) : (
                            source
                          )}
                        </Box>
                        <Box>Publication date: {date}</Box>
                      </Flex>
                    </Box>

                    <Paragraph sx={{ mt: '0.5rem' }}>
                      {description}
                      <br />
                      <br />
                      <b>Data preparation methods:</b>
                      <br />
                      {methods}
                    </Paragraph>

                    {citation ? (
                      <Box
                        sx={{
                          mt: '1rem',
                          pt: '0.25rem',
                          borderTop: '1px solid',
                          borderTopColor: 'grey.1',
                          color: 'grey.8',
                          fontStyle: 'italic',
                        }}
                      >
                        {citation}
                      </Box>
                    ) : null}
                  </Box>
                )
              )}
            </Box>
          </Box>
        ))}
      </Container>
    </Layout>
  )
}

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
