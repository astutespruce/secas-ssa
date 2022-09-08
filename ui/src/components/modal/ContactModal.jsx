import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import BoundModal from './BoundModal'

const ContactModal = ({ children }) => (
  <BoundModal title="Contact Us" anchorNode={children}>
    <Text as="p">TODO:</Text>
  </BoundModal>
)

ContactModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ContactModal
