import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import BoundModal from './BoundModal'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, title } = siteMetadata

const ReportProblemModal = ({ children }) => (
  <BoundModal title="Report a Problem" anchorNode={children}>
    <Text as="p">
      Did you encounter an error while using this application?
      <br />
      <br />
      We want to hear from you!
      <br />
      <br />
      <b>email</b>{' '}
      <a
        href={`mailto:${contactEmail}?subject=${title} - report a problem`}
        target="_blank"
        rel="noopener noreferrer"
      >
        {contactEmail}
      </a>
    </Text>
  </BoundModal>
)

ReportProblemModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ReportProblemModal
