import React from 'react'
import PropTypes from 'prop-types'

import { OutboundLink } from 'components/link'

import BoundModal from './BoundModal'

const ContactModal = ({ children }) => (
  <BoundModal title="Contact Us" anchorNode={children}>
    Do you have a question about how to use this tool or interpret results?
    SECAS staff are here to support you! We really mean it. It is what we do!
    <br />
    <br />
    Please reach out to the user support contact{' '}
    <OutboundLink to="http://secassoutheast.org/staff">
      {' '}
      for your state
    </OutboundLink>
  </BoundModal>
)

ContactModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ContactModal
