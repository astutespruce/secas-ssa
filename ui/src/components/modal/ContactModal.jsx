import React from 'react'
import PropTypes from 'prop-types'

import { OutboundLink } from 'components/link'

import BoundModal from './BoundModal'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, title } = siteMetadata

const ContactModal = ({ children }) => (
  <BoundModal title="Contact Us" anchorNode={children}>
    Do you have a question about how to use this tool or interpret results? SSA
    Geospatial Toolkit staff are here to help!
    <br />
    <br />
    Please reach out to user support:
    <br />
    <br /> <b>email</b>:{' '}
    <a
      href={`mailto:${contactEmail}?subject=${title} - user support`}
      target="_blank"
      rel="noopener noreferrer"
    >
      {contactEmail}
    </a>
  </BoundModal>
)

ContactModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ContactModal
