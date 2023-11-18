import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Divider, Paragraph, Text } from 'theme-ui'
import { ReplyAll, Download as DownloadIcon } from '@emotion-icons/fa-solid'

import { JobContainer } from 'components/job'
import { OutboundLink } from 'components/link'

import config from '../../../gatsby-config'

const { apiHost } = config.siteMetadata

const Download = ({ uuid, selectedAttribute, selectedDatasets, onCancel }) => {
  const [reportURL, setReportURL] = useState(null)

  const handleSuccess = useCallback((reportPath) => {
    const url = `${apiHost}${reportPath}`
    setReportURL(url)

    window.location.href = url
  }, [])

  if (reportURL !== null) {
    return (
      <Box>
        <Paragraph sx={{ fontSize: 4, pb: '2rem' }}>
          Your report should download automatically. You can also click the
          button below to download your report.
        </Paragraph>

        <Divider />

        <Flex sx={{ justifyContent: 'space-between' }}>
          <Button onClick={onCancel}>
            <Flex>
              <ReplyAll size="1.5em" style={{ marginRight: '0.5rem' }} />
              <Text>Start over</Text>
            </Flex>
          </Button>
          <Box>
            <OutboundLink to={reportURL}>
              <Button variant="primary">
                <Flex>
                  <DownloadIcon
                    size="1.5em"
                    style={{ marginRight: '0.5rem' }}
                  />
                  <Text>Download report</Text>
                </Flex>
              </Button>
            </OutboundLink>
          </Box>
        </Flex>
      </Box>
    )
  }

  // failsafe to prevent submitting if no uuid
  if (uuid === null) {
    return null
  }

  const data = {
    uuid,
    datasets: selectedDatasets
      ? Object.entries(selectedDatasets)
          .filter(([_, v]) => v)
          .map(([k, _]) => k)
          .join(',')
      : '',
  }

  if (selectedAttribute) {
    data.field = selectedAttribute
  }

  return (
    <JobContainer
      path="report"
      data={data}
      defaultMessage="Creating report..."
      onSuccess={handleSuccess}
      onCancel={onCancel}
    />
  )
}

Download.propTypes = {
  uuid: PropTypes.string.isRequired,
  selectedAttribute: PropTypes.string,
  selectedDatasets: PropTypes.objectOf(PropTypes.bool).isRequired,
  onCancel: PropTypes.func.isRequired,
}

Download.defaultProps = {
  selectedAttribute: null,
}

export default Download
