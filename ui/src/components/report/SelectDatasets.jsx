import React from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Flex,
  Grid,
  Paragraph,
  Checkbox,
  Heading,
  Divider,
  Button,
} from 'theme-ui'

const SelectDatasets = ({ datasets }) => (
  <Grid columns={[0, 2]} gap={5}>
    <Box>
      <Flex sx={{ alignItems: 'center', mb: '1rem' }}>
        <Box variant="boxes.step">2</Box>
        <Heading as="h3" sx={{ m: 0 }}>
          Select factors to include in report
        </Heading>
      </Flex>
      <Paragraph>TODO: instructions</Paragraph>
    </Box>
    <Box>
      <Heading as="h4" sx={{ mb: '0.5rem' }}>
        Available landscape-level factors:
      </Heading>
      TODO: list of datasets
      <Divider />
      <Flex sx={{ justifyContent: 'flex-end' }}>
        <Button as="button" variant="primary">
          Create report
        </Button>
      </Flex>
    </Box>
  </Grid>
)

SelectDatasets.propTypes = {}

SelectDatasets.defaultProps = {}

export default SelectDatasets
