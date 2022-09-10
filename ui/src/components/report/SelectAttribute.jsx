import React from 'react'
import PropTypes from 'prop-types'

import {
  Box,
  Button,
  Flex,
  Grid,
  Divider,
  Paragraph,
  Heading,
  Select,
  Text,
} from 'theme-ui'

const SelectAttribute = ({ attributes }) => (
  <Grid columns={[0, 2]} gap={5}>
    <Box>
      <Flex sx={{ alignItems: 'center', mb: '1rem' }}>
        <Box variant="boxes.step">2</Box>
        <Heading as="h3" sx={{ m: 0 }}>
          Select population attribute
        </Heading>
      </Flex>
      <Paragraph>
        If your dataset has an attribute that identifies unique populations,
        please choose that attribute from the list to the right.
        <br />
        <br />
        If you do not select an attribute, or if one isn&apos;t available in the
        dataset, all boundaries will be combined and analyzed as a single unit.
      </Paragraph>
    </Box>
    <Box>
      <Heading as="h4" sx={{ mb: '0.5rem' }}>
        Population attribute:
      </Heading>

      <Select>
        <option value="">-- Group everything together --</option>
        {attributes.map((att) => (
          <option value={att}>{att}</option>
        ))}
      </Select>

      <Divider />
      <Flex sx={{ justifyContent: 'flex-end' }}>
        <Button as="button" variant="primary">
          Continue
        </Button>
      </Flex>
    </Box>
  </Grid>
)

SelectAttribute.propTypes = {
  attributes: PropTypes.arrayOf(PropTypes.string),
}

SelectAttribute.defaultProps = {
  attributes: [],
}

export default SelectAttribute
