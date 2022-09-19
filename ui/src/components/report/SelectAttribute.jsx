import React, { useCallback } from 'react'
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

import { OutboundLink } from 'components/link'
import { siteMetadata } from '../../../gatsby-config'

const SelectAttribute = ({
  attributes,
  selectedAttribute,
  onBack,
  onNext,
  onSelect,
}) => {
  const handleSelect = useCallback(
    ({ target: { value } }) => {
      onSelect(value)
    },
    [onSelect]
  )

  const attributeIds = Object.keys(attributes)
  attributeIds.sort()

  const hasAttributes = attributeIds.length > 0

  return (
    <Grid columns={2} gap={5}>
      <Box>
        <Flex sx={{ alignItems: 'center', mb: '1rem' }}>
          <Box variant="boxes.step">2</Box>
          <Heading as="h3" sx={{ m: 0 }}>
            Select analysis unit attribute
          </Heading>
        </Flex>
        <Paragraph>
          If your dataset has an attribute that identifies unique analysis
          units, please choose that attribute from the list to the right.
          <br />
          <br />
          If you do not select an attribute, or if one isn&apos;t available in
          the dataset, all boundaries will be combined and analyzed as a single
          unit.
        </Paragraph>
      </Box>
      <Box>
        <Heading as="h4" sx={{ mb: '0.5rem' }}>
          Analysis unit attribute:
        </Heading>

        <Select
          onChange={handleSelect}
          disabled={!hasAttributes}
          defaultValue={selectedAttribute}
        >
          <option value="">-- Group everything together --</option>
          {attributeIds.map((id) => (
            <option key={id} value={id}>
              {id} ({attributes[id]} unique values)
            </option>
          ))}
        </Select>

        {!hasAttributes ? (
          <Text sx={{ mt: '1rem', color: 'grey.7' }}>
            We did not find any attributes that appear to identify unique
            analysis units in this dataset (limited to text or integer fields).
            If there is an attribute present that we did not detect, please{' '}
            <OutboundLink to={`mailto:${siteMetadata.contactEmail}`}>
              let us know
            </OutboundLink>
            .
          </Text>
        ) : null}

        <Divider />
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Button as="button" variant="secondary" onClick={onBack}>
            Back
          </Button>
          <Button as="button" variant="primary" onClick={onNext}>
            Next
          </Button>
        </Flex>
      </Box>
    </Grid>
  )
}

SelectAttribute.propTypes = {
  attributes: PropTypes.objectOf(PropTypes.number),
  selectedAttribute: PropTypes.string,
  onBack: PropTypes.func.isRequired,
  onNext: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired,
}

SelectAttribute.defaultProps = {
  attributes: {},
  selectedAttribute: null,
}

export default SelectAttribute
