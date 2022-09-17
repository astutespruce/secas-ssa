import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { JobContainer } from 'components/job'
import UploadForm from './UploadForm'

const Upload = ({ onSuccess }) => {
  const [data, setData] = useState(null)

  const handleSubmit = (newData) => {
    setData(() => newData)
  }

  const handleReset = () => {
    setData(() => null)
  }

  if (data !== null) {
    return (
      <JobContainer
        path="upload"
        data={data}
        defaultMessage="Uploading..."
        onSuccess={onSuccess}
        onCancel={handleReset}
      />
    )
  }

  return <UploadForm onSubmit={handleSubmit} onReset={handleReset} />
}

Upload.propTypes = {
  onSuccess: PropTypes.func.isRequired,
}

export default Upload
